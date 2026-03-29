#  Developed by t.me/napaaextra

from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import humanize
import asyncio
from datetime import timedelta
from plugins.shortner import get_short
from plugins.link_sharing import handle_link_sharing
from plugins.others import send_start_message
from plugins.credit_system import handle_credit_system, handle_earn_credit_link
from plugins.gofile_uploader import background_upload_task

async def get_messages_with_fallback(client: Client, channel_id: int, msg_ids: list):
    """
    Enhanced message fetching with automatic backup fallback.
    """
    final_messages = {}
    ids_to_fetch = list(msg_ids)
    
    client.LOGGER(__name__, client.name).info(f"📥 Fetching {len(ids_to_fetch)} messages from channel {channel_id}")
    
    try:
        all_raw_msgs = []
        for i in range(0, len(ids_to_fetch), 200):
            batch_ids = ids_to_fetch[i:i+200]
            try:
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                if isinstance(msgs, list): all_raw_msgs.extend(msgs)
                else: all_raw_msgs.append(msgs)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                if isinstance(msgs, list): all_raw_msgs.extend(msgs)
                else: all_raw_msgs.append(msgs)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"❌ Major error fetching from original channel {channel_id}: {e}")
    
    successful_ids = {msg.id for msg in all_raw_msgs if msg and not msg.empty}
    for msg in all_raw_msgs:
        if msg and not msg.empty:
            final_messages[msg.id] = msg

    failed_ids = set(ids_to_fetch) - successful_ids
    if failed_ids:
        client.LOGGER(__name__, client.name).info(f"🔄 {len(failed_ids)} messages not found. Checking backup...")
        backup_db_id = client.databases.get('backup')
        if backup_db_id:
            backup_map = {await client.mongodb.get_backup_msg_id(channel_id, og_id): og_id for og_id in failed_ids}
            backup_map = {k: v for k, v in backup_map.items() if k is not None}

            if backup_map:
                backup_msg_ids = list(backup_map.keys())
                for i in range(0, len(backup_msg_ids), 200):
                    batch_backup_ids = backup_msg_ids[i:i+200]
                    try:
                        backup_msgs = await client.get_messages(backup_db_id, batch_backup_ids)
                        if not isinstance(backup_msgs, list): backup_msgs = [backup_msgs]
                        for b_msg in backup_msgs:
                            if b_msg and not b_msg.empty:
                                original_id = backup_map.get(b_msg.id)
                                if original_id:
                                    final_messages[original_id] = b_msg
                    except Exception as e:
                        client.LOGGER(__name__, client.name).error(f"❌ Error fetching from backup: {e}")
    
    return [final_messages.get(og_id) for og_id in msg_ids if final_messages.get(og_id)]


async def backup_files(client: Client, original_channel_id: int, message_ids: list):
    """
    Asynchronously backs up files to the backup channel.
    """
    backup_db_id = client.databases.get('backup')
    if not backup_db_id or not message_ids:
        return

    for msg_id in message_ids:
        try:
            if await client.mongodb.is_backed_up(original_channel_id, msg_id):
                continue
            original_msg = await client.get_messages(original_channel_id, msg_id)
            if not original_msg or original_msg.empty:
                continue
            backup_msg = await original_msg.copy(backup_db_id)
            await client.mongodb.add_backup_mapping(original_channel_id, msg_id, backup_msg.id)
            await asyncio.sleep(1)
        except Exception as e:
            client.LOGGER(__name__, client.name).error(f"BACKGROUND BACKUP: Failed for message {msg_id}: {e}")

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await client.mongodb.present_user(user_id):
        await client.mongodb.add_user(user_id)
    if await client.mongodb.is_banned(user_id):
        return await message.reply("**You have been banned!**")

    text = message.text
    if len(text) <= 7:
        return await send_start_message(client, message)

    try:
        param = text.split(" ", 1)[1]
    except IndexError:
        return await send_start_message(client, message)

    is_from_shortener = param.startswith("dl_")
    is_credit_get = param.startswith("creditget_")
    is_earn_credit = param.startswith("earn_credit_")

    base64_string = param
    if is_from_shortener or is_credit_get or is_earn_credit:
        base64_string = param.split("_", 1)[1]

    try:
        decoded_string = await decode(base64_string)
    except Exception:
        return await message.reply("❌ Invalid or expired link.")

    if decoded_string.startswith("earn_credit_"):
        await handle_earn_credit_link(client, message)
        return

    if decoded_string.startswith(("lnk_", "req_")):
        return await handle_link_sharing(client, message, decoded_string)

    if is_credit_get:
        await client.mongodb.update_credits(user_id, client.credits_per_visit)
        await message.reply(f"<b>✅ You earned {client.credits_per_visit} credit(s) for visiting the link!</b>")

    can_proceed = await handle_credit_system(client, message, base64_string)
    if not can_proceed:
        return

    is_admin = user_id in client.admins
    is_premium = await client.mongodb.is_pro(user_id)
    if client.shortner_enabled and not client.credit_system_enabled and not is_admin and not is_premium and not is_from_shortener:
        redirect_param = f"dl_{base64_string}"
        direct_link_after_shortener = f"https://t.me/{client.username}?start={redirect_param}"
        shortened_url = get_short(direct_link_after_shortener, client)
        
        photo_url = client.messages.get("SHORTNER_PHOTO")
        caption_text = client.messages.get('SHORTNER_MSG', "<b>YOUR LINK IS READY!</b>")
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ •", url=shortened_url)],
            [InlineKeyboardButton("ᴘʀᴇᴍɪᴜᴍ", url=client.messages.get("PREMIUM_CONTACT", "https://t.me/username")), InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ", url=client.tutorial_link)]
        ])
        
        if photo_url:
            return await message.reply_photo(photo=photo_url, caption=caption_text, reply_markup=buttons, parse_mode=ParseMode.HTML)
        else:
            return await message.reply_text(caption_text, reply_markup=buttons, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    is_single_file_link = False
    try:
        parts = decoded_string.split("_")
        command = parts[0]
        if command == "single":
            is_single_file_link = True
            channel_id, msg_ids = int(parts[1]), [int(parts[2])]
        elif command == "batch":
            if len(parts) == 4:
                channel_id, start_id, end_id = int(parts[1]), int(parts[2]), int(parts[3])
                msg_ids = list(range(start_id, end_id + 1))
            else:
                channel_id, msg_ids = await client.mongodb.get_batch(parts[1])
                if not (channel_id and msg_ids): return await message.reply("❌ This link has expired.")
        else:
            raise ValueError("Unsupported link format")
    except (IndexError, ValueError):
        return await message.reply("❌ Invalid or malformed file link.")

    temp_msg = await message.reply("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>", parse_mode=ParseMode.HTML)
    
    messages_to_send = await get_messages_with_fallback(client, channel_id, msg_ids)
    if not messages_to_send:
        return await temp_msg.edit("❌ <b>Content Not Found.</b> It may have been deleted.")
    
    if client.databases.get('backup'):
        asyncio.create_task(backup_files(client, channel_id, msg_ids))
    
    await temp_msg.delete()

    sent_messages, failed_count = [], 0
    for msg in messages_to_send:
        
        is_web_page = hasattr(msg, 'web_page') and msg.web_page is not None

        if msg.media and not is_web_page:
            final_caption = "" if client.hide_caption else (msg.caption.html if msg.caption else "")
            
            buttons = []
            if client.channel_button_enabled and client.button_name and client.button_url:
                buttons.append([InlineKeyboardButton(client.button_name, url=client.button_url)])

            gofile_url = None
            if client.gofile_enabled and client.gofile_manager and (msg.document or msg.video):
                gofile_url = await client.mongodb.get_gofile_link(channel_id, msg.id)
                if gofile_url:
                    gofile_button = InlineKeyboardButton("⚡️ ɢᴏғɪʟᴇ ʟɪɴᴋ", url=gofile_url)
                    if buttons and len(buttons[0]) < 2:
                        buttons[0].append(gofile_button)
                    else:
                        buttons.insert(0, [gofile_button])

            final_markup = InlineKeyboardMarkup(buttons) if buttons else None
            
            try:
                sent_msg = await msg.copy(
                    chat_id=user_id,
                    caption=final_caption,
                    reply_markup=final_markup,
                    protect_content=client.protect
                )
                sent_messages.append(sent_msg)
                
                if is_single_file_link and client.gofile_enabled and client.gofile_manager and not gofile_url and (msg.document or msg.video):
                    asyncio.create_task(background_upload_task(client, channel_id, msg.id))

            except FloodWait as e:
                await asyncio.sleep(e.x + 1)
                try:
                    sent_msg = await msg.copy(user_id, caption=final_caption, reply_markup=final_markup, protect_content=client.protect)
                    sent_messages.append(sent_msg)
                    if is_single_file_link and client.gofile_enabled and client.gofile_manager and not gofile_url and (msg.document or msg.video):
                        asyncio.create_task(background_upload_task(client, channel_id, msg.id))
                except Exception: failed_count += 1
            except Exception:
                failed_count += 1
        
        elif msg.text:
            try:
                sent_text = await client.send_message(user_id, msg.text.html, disable_web_page_preview=True)
                sent_messages.append(sent_text)
            except Exception:
                failed_count += 1
    
    if not sent_messages and not failed_count:
        await message.reply("No valid content found in the requested link(s).")
        return

    if failed_count > 0:
        await client.send_message(user_id, f"⚠️ <b>Note:</b> {failed_count} item(s) could not be sent.")
    
    if sent_messages and client.auto_del > 0:
        k = await client.send_message(
            chat_id=user_id, 
            text=f'<b>⚠️ Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....\n<blockquote>Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {humanize.naturaldelta(timedelta(seconds=client.auto_del))}. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ.</blockquote>\n<blockquote>ɴᴏᴛᴇ : ᴜsᴇ ᴠʟᴄ ᴏʀ ᴀɴʏ ᴏᴛʜᴇʀ ɢᴏᴏᴅ ᴠɪᴅᴇᴏ ᴘʟᴀʏᴇʀ ᴀᴘᴘ ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ!</blockquote></b>'
        )
        asyncio.create_task(delete_files(sent_messages, client, k, text))
