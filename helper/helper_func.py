#  Developed by t.me/napaaextra

import base64
import re
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.errors import UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired, FloodWait
from datetime import datetime, timedelta
from pyrogram import errors

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, channel_id, message_ids):
    """Fetches messages, falling back to backup DB if necessary."""
    final_messages = {}
    ids_to_fetch = list(message_ids)
    
    try:
        all_raw_msgs = []
        for i in range(0, len(ids_to_fetch), 200):
            batch_ids = ids_to_fetch[i:i+200]
            try:
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                all_raw_msgs.extend(msgs)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                all_raw_msgs.extend(msgs)

        successful_ids = {msg.id for msg in all_raw_msgs if msg}
        for msg in all_raw_msgs:
            if msg:
                final_messages[msg.id] = msg

        failed_ids = set(ids_to_fetch) - successful_ids
        backup_db_id = client.databases.get('backup')
        
        if backup_db_id and failed_ids:
            backup_map = {await client.mongodb.get_backup_msg_id(channel_id, o_id): o_id for o_id in failed_ids}
            backup_map = {k: v for k, v in backup_map.items() if k is not None}
            
            if backup_map:
                backup_msg_ids = list(backup_map.keys())
                for i in range(0, len(backup_msg_ids), 200):
                    batch_backup_ids = backup_msg_ids[i:i+200]
                    try:
                        backup_msgs = await client.get_messages(backup_db_id, batch_backup_ids)
                        for b_msg in backup_msgs:
                            if b_msg and b_msg.id in backup_map:
                                final_messages[backup_map[b_msg.id]] = b_msg
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in get_messages: {e}")
        
    return [final_messages.get(og_id) for og_id in message_ids if og_id in final_messages]

async def get_message_id(client, message: Message):
    """
    Robustly extracts channel_id and message_id from a message.
    Handles modern forwards, deprecated forwards, and text links.
    """
    chat_id, msg_id = (None, None)

    
    if message.forward_from_chat:
        chat_id = message.forward_from_chat.id
        msg_id = message.forward_from_message_id

    elif getattr(message, 'forward_origin', None) and message.forward_origin.chat:
        chat_id = message.forward_origin.chat.id
        msg_id = message.forward_origin.message_id

    if chat_id and chat_id in client.all_db_ids:
        return chat_id, msg_id

    if message.text:
        pattern = r"https://t.me/(?:c/)?(.*?)/(\d+)"
        matches = re.match(pattern, message.text)
        if matches:
            channel_str = matches.group(1)
            msg_id = int(matches.group(2))
            
            for db_id in client.all_db_ids:
                try:
                    if str(db_id) == f"-100{channel_str}":
                        return db_id, msg_id
                    chat = await client.get_chat(db_id)
                    if chat.username and chat.username.lower() == channel_str.lower():
                        return db_id, msg_id
                except Exception:
                    continue
    
    return 0, 0


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0: break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

async def is_bot_admin(client, channel_id):
    try:
        bot = await client.get_chat_member(channel_id, "me")
        if bot.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            if bot.privileges:
                required = ["can_invite_users", "can_delete_messages"]
                missing = [r for r in required if not getattr(bot.privileges, r, False)]
                if missing:
                    return False, f"Bot is missing rights: {', '.join(missing)}"
            return True, None
        return False, "Bot is not an admin in the channel."
    except errors.ChatAdminRequired:
        return False, "Bot can't access admin info in this channel."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

async def check_subscription(client, user_id):
    statuses = {}
    for ch_id, (ch_name, ch_link, req, timer) in client.fsub_dict.items():
        if req and await client.mongodb.is_user_in_channel(ch_id, user_id):
            statuses[ch_id] = ChatMemberStatus.MEMBER
            continue
        try:
            user = await client.get_chat_member(ch_id, user_id)
            statuses[ch_id] = user.status
        except UserNotParticipant:
            statuses[ch_id] = ChatMemberStatus.BANNED
        except (Forbidden, ChatAdminRequired):
            client.LOGGER(__name__, client.name).warning(f"Permission error for {ch_name}.")
            statuses[ch_id] = None
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error checking {ch_name}: {e}")
            statuses[ch_id] = None
    return statuses

def is_user_subscribed(statuses):
    return all(
        s in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        for s in statuses.values() if s is not None
    ) and bool(statuses)

def force_sub(func):
    """Decorator to enforce force subscription with a status message."""
    async def wrapper(client: Client, message: Message):
        if not client.fsub_dict:
            return await func(client, message)
        
        photo = client.messages.get('FSUB_PHOTO', '')
        msg = await message.reply_photo(caption="<b>ᴡᴀɪᴛ ᴀ ꜱᴇᴄᴏɴᴅ....</b>", photo=photo, parse_mode=ParseMode.HTML) if photo else await message.reply("<b>ᴡᴀɪᴛ ᴀ ꜱᴇᴄᴏɴᴅ....</b>", parse_mode=ParseMode.HTML)
        
        statuses = await check_subscription(client, message.from_user.id)
        if is_user_subscribed(statuses):
            await msg.delete()
            return await func(client, message)

        buttons = []
        status_lines = []
        for ch_id, (ch_name, ch_link, req, timer) in client.fsub_dict.items():
            status = statuses.get(ch_id)
            if status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                status_text = "<b>Joined</b> ✅"
            else:
                status_text = "<i>Required</i> ❗️"
                if timer > 0:
                    invite = await client.create_chat_invite_link(chat_id=ch_id, expire_date=datetime.now() + timedelta(minutes=timer), creates_join_request=req)
                    ch_link = invite.invite_link
                buttons.append(InlineKeyboardButton(f"Join {ch_name}", url=ch_link))
            status_lines.append(f"› {ch_name} - {status_text}")
        
        fsub_text = client.messages.get('FSUB', "<blockquote><b>Join Required</b></blockquote>\nYou must join the following channel(s) to continue:")
        channels_message = f"{fsub_text}\n\n" + "\n".join(status_lines)

        try_again_button = []
        if len(message.text.split()) > 1:
            try:
                try_again_link = f"https://t.me/{client.username}/?start={message.text.split()[1]}"
                try_again_button = [InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=try_again_link)]
            except:
                pass

        button_layout = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        if try_again_button:
            button_layout.append(try_again_button)
        
        try:
            await msg.edit(text=channels_message, reply_markup=InlineKeyboardMarkup(button_layout) if button_layout else None, parse_mode=ParseMode.HTML)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error updating FSUB message: {e}")
    return wrapper

async def delete_files(messages, client, k, enter):
    if client.auto_del > 0:
        await asyncio.sleep(client.auto_del)
        for msg in messages:
            try:
                await msg.delete()
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to auto-delete message {msg.id}: {e}")
    
    command_part = enter.split(" ")[1] if len(enter.split(" ")) > 1 else None
    
    button_url = None
    if command_part:
        try:
            button_url = f"https://t.me/{client.username}?start={command_part}"
        except:
            pass

    final_text = "<b>Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑</b>"
    keyboard = None

    if button_url:
        final_text += f'\n<blockquote><b>Iғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ:[<a href="{button_url}">⭕️ Cʟɪᴄᴋ Hᴇʀᴇ</a>] ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</blockquote></b>'
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⭕️ Cʟɪᴄᴋ Hᴇʀᴇ", url=button_url), InlineKeyboardButton("Cʟᴏꜱᴇ ✖️", callback_data="close")]]
        )
    
    await k.edit_text(
        final_text,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML
    )
