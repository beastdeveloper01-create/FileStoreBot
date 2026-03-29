#  Developed by t.me/napaaextra
import asyncio
import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired, RPCError
from helper.helper_func import encode, decode
from datetime import datetime, timedelta

PAGE_SIZE = 6


async def revoke_invite_after_minutes(client, channel_id: int, link: str, minutes: int = 5):
    """Auto-revoke invite links after specified minutes"""
    await asyncio.sleep(minutes * 60)
    try:
        await client.revoke_chat_invite_link(channel_id, link)
        client.LOGGER(__name__, client.name).info(f"Invite link revoked for channel {channel_id}")
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Failed to revoke invite for {channel_id}: {e}")


@Client.on_message(filters.command('addch') & filters.private)
async def add_channel_command(client: Client, message: Message):
    """Add a channel to link sharing system"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    if len(message.command) < 2:
        return await message.reply(
            "<b>Usage:</b> <code>/addch {channel_id}</code>\n\n"
            "<b>Example:</b> <code>/addch -1001234567890</code>",
            parse_mode=ParseMode.HTML
        )
    
    try:
        channel_id = int(message.command[1])
    except ValueError:
        return await message.reply(
            "<b>❌ Invalid channel ID. Please provide a valid integer.</b>",
            parse_mode=ParseMode.HTML
        )
    
    try:
        chat = await client.get_chat(channel_id)
        bot_member = await client.get_chat_member(channel_id, "me")

        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply(
                f"<b>❌ I am not an admin in {chat.title}.</b>\n\n"
                "Please make me an admin to continue.",
                parse_mode=ParseMode.HTML,
            )

        if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
            if not bot_member.privileges or not bot_member.privileges.can_invite_users:
                return await message.reply(
                    f"<b>❌ I am an admin in {chat.title}, but I'm missing the 'Invite Users via Link' permission.</b>\n\nPlease grant this permission.",
                    parse_mode=ParseMode.HTML,
                )
        
        await client.mongodb.save_link_channel(channel_id)
        
        base64_invite = await encode(f"lnk_{channel_id}")
        base64_request = await encode(f"req_{channel_id}")
        
        normal_link = f"https://t.me/{client.username}?start={base64_invite}"
        request_link = f"https://t.me/{client.username}?start={base64_request}"
        
        await message.reply(
            f"<b>✅ Channel Added Successfully!</b>\n\n"
            f"<b>Channel:</b> {chat.title}\n"
            f"<b>ID:</b> <code>{channel_id}</code>\n\n"
            f"<b>🔗 Normal Link:</b>\n<code>{normal_link}</code>\n\n"
            f"<b>🔗 Request Link:</b>\n<code>{request_link}</code>",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        return await message.reply(
            f"<b>❌ Error:</b> <code>{str(e)}</code>",
            parse_mode=ParseMode.HTML
        )

@Client.on_message(filters.command('delch') & filters.private)
async def delete_channel_command(client: Client, message: Message):
    """Remove a channel from link sharing system"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    if len(message.command) < 2:
        return await message.reply(
            "<b>Usage:</b> <code>/delch {channel_id}</code>\n\n"
            "<b>Example:</b> <code>/delch -1001234567890</code>",
            parse_mode=ParseMode.HTML
        )
    
    try:
        channel_id = int(message.command[1])
        chat = await client.get_chat(channel_id)
        
        success = await client.mongodb.remove_link_channel(channel_id)
        
        if success:
            await message.reply(
                f"<b>✅ Channel Removed Successfully!</b>\n\n"
                f"<b>Channel:</b> {chat.title}\n"
                f"<b>ID:</b> <code>{channel_id}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply(
                f"<b>❌ Channel not found in link sharing system!</b>",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        return await message.reply(
            f"<b>❌ Error:</b> <code>{str(e)}</code>",
            parse_mode=ParseMode.HTML
        )


@Client.on_message(filters.command('channels') & filters.private)
async def show_channels_command(client: Client, message: Message):
    """Show all link sharing channels"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        return await message.reply(
            "<b>📋 No link sharing channels configured.</b>\n\n"
            "Use <code>/addch {channel_id}</code> to add one.",
            parse_mode=ParseMode.HTML
        )
    
    await send_channels_page(client, message, channels, page=0)

async def send_channels_page(client, message, channels, page, edit=False):
    """Paginated channel listing"""
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    
    text = "<b>📋 Link Sharing Channels:</b>\n\n"
    
    for idx, channel_id in enumerate(channels[start_idx:end_idx], start=start_idx + 1):
        try:
            chat = await client.get_chat(channel_id)
            base64_invite = await encode(f"lnk_{channel_id}")
            button_link = f"https://t.me/{client.username}?start={base64_invite}"
            
            text += f"<b>{idx}. {chat.title}</b>\n"
            text += f"   <b>ID:</b> <code>{channel_id}</code>\n"
            text += f"   <b>Link:</b> <code>{button_link}</code>\n\n"
        except Exception as e:
            text += f"<b>{idx}. Channel {channel_id}</b>\n"
            text += f"   <b>Status:</b> Error fetching info\n\n"
    
    text += f"<b>📄 Page {page + 1} of {total_pages}</b>\n"
    text += f"<b>Total Channels:</b> {len(channels)}"
    
    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"chpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"chpage_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if edit:
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"chpage_(\d+)"))
async def paginate_channels(client, callback_query):
    """Handle channel pagination"""
    page = int(callback_query.data.split("_")[1])
    channels = await client.mongodb.get_link_channels()
    await send_channels_page(client, callback_query.message, channels, page, edit=True)


@Client.on_message(filters.command('links') & filters.private)
async def show_all_links(client: Client, message: Message):
    """Show all channel links as text"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        return await message.reply(
            "<b>📋 No link sharing channels configured.</b>\n\n"
            "Use <code>/addch {channel_id}</code> to add one.",
            parse_mode=ParseMode.HTML
        )
    
    await send_links_page(client, message, channels, page=0)

async def send_links_page(client, message, channels, page, edit=False):
    """Paginated link listing"""
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    
    text = "<b>➤ All Channel Links:</b>\n\n"
    
    for idx, channel_id in enumerate(channels[start_idx:end_idx], start=start_idx + 1):
        try:
            chat = await client.get_chat(channel_id)
            base64_invite = await encode(f"lnk_{channel_id}")
            base64_request = await encode(f"req_{channel_id}")
            
            normal_link = f"https://t.me/{client.username}?start={base64_invite}"
            request_link = f"https://t.me/{client.username}?start={base64_request}"
            
            text += f"<b>{idx}. {chat.title}</b>\n"
            text += f"<b>➥ Normal:</b> <code>{normal_link}</code>\n"
            text += f"<b>➤ Request:</b> <code>{request_link}</code>\n\n"
        except Exception as e:
            text += f"<b>{idx}. Channel {channel_id}</b> (Error)\n\n"
    
    text += f"<b>📄 Page {page + 1} of {total_pages}</b>"
    
    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"lnkpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"lnkpage_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if edit:
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"lnkpage_(\d+)"))
async def paginate_links(client, callback_query):
    """Handle links pagination"""
    page = int(callback_query.data.split("_")[1])
    channels = await client.mongodb.get_link_channels()
    await send_links_page(client, callback_query.message, channels, page, edit=True)


@Client.on_message(filters.command('reqlink') & filters.private)
async def show_request_links(client: Client, message: Message):
    """Show all request-to-join links"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        return await message.reply(
            "<b>📋 No link sharing channels configured.</b>\n\n"
            "Use <code>/addch {channel_id}</code> to add one.",
            parse_mode=ParseMode.HTML
        )
    
    await send_request_page(client, message, channels, page=0)

async def send_request_page(client, message, channels, page, edit=False):
    """Paginated request link buttons"""
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    buttons = []
    
    row = []
    for channel_id in channels[start_idx:end_idx]:
        try:
            base64_request = await encode(f"req_{channel_id}")
            button_link = f"https://t.me/{client.username}?start={base64_request}"
            chat = await client.get_chat(channel_id)
            
            row.append(InlineKeyboardButton(chat.title, url=button_link))
            
            if len(row) == 2:
                buttons.append(row)
                row = []
        except Exception as e:
            client.LOGGER(__name__, client.name).error(f"Error for channel {channel_id}: {e}")
    
    if row:
        buttons.append(row)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"reqpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"reqpage_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if edit:
        await message.edit_text(
            "<b>Select a channel to request access:</b>",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text(
            "<b>Select a channel to request access:</b>",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

@Client.on_callback_query(filters.regex(r"reqpage_(\d+)"))
async def paginate_requests(client, callback_query):
    """Handle request links pagination"""
    page = int(callback_query.data.split("_")[1])
    channels = await client.mongodb.get_link_channels()
    await send_request_page(client, callback_query.message, channels, page, edit=True)


@Client.on_message(filters.command('bulklink') & filters.private)
async def bulk_link_generation(client: Client, message: Message):
    """Generate links for multiple channels at once"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    if len(message.command) < 2:
        return await message.reply(
            "<b>Usage:</b> <code>/bulklink {id1} {id2} {id3} ...</code>\n\n"
            "<b>Example:</b> <code>/bulklink -1001234567890 -1009876543210</code>",
            parse_mode=ParseMode.HTML
        )
    
    ids = message.command[1:]
    reply_text = "<b>➤ Bulk Link Generation:</b>\n\n"
    
    for idx, id_str in enumerate(ids, start=1):
        try:
            channel_id = int(id_str)
            chat = await client.get_chat(channel_id)
            
            base64_invite = await encode(f"lnk_{channel_id}")
            base64_request = await encode(f"req_{channel_id}")
            
            normal_link = f"https://t.me/{client.username}?start={base64_invite}"
            request_link = f"https://t.me/{client.username}?start={base64_request}"
            
            reply_text += f"<b>{idx}. {chat.title}</b>\n"
            reply_text += f"<b>ID:</b> <code>{channel_id}</code>\n"
            reply_text += f"<b>➥ Normal:</b> <code>{normal_link}</code>\n"
            reply_text += f"<b>➤ Request:</b> <code>{request_link}</code>\n\n"
        except Exception as e:
            reply_text += f"<b>{idx}. Channel {id_str}</b> (Error: {e})\n\n"
    
    await message.reply(reply_text, parse_mode=ParseMode.HTML)


async def handle_link_sharing(client: Client, message: Message, decoded_param: str):
    """Handle link sharing when user clicks generated links. Receives a DECODED parameter."""
    try:
        is_request = decoded_param.startswith("req_")
        channel_id_str = decoded_param.replace("lnk_", "").replace("req_", "")
        
        try:
            channel_id = int(channel_id_str)
        except (ValueError, TypeError):
            client.LOGGER(__name__, client.name).error(f"Invalid channel ID in link: {channel_id_str}")
            return await message.reply("<b>❌ Invalid channel link format.</b>", parse_mode=ParseMode.HTML)
            
        if not await client.mongodb.is_link_channel(channel_id):
            return await message.reply("<b>❌ This channel link is invalid or has been disabled.</b>", parse_mode=ParseMode.HTML)
        
        old_link_info = await client.mongodb.get_current_invite_link(channel_id)
        if old_link_info:
            try:
                await client.revoke_chat_invite_link(channel_id, old_link_info["invite_link"])
                client.LOGGER(__name__, client.name).info(f"Revoked old link for {channel_id}")
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to revoke old link: {e}")
        
        invite = await client.create_chat_invite_link(
            chat_id=channel_id,
            expire_date=datetime.now() + timedelta(minutes=5),
            creates_join_request=is_request
        )
        
        await client.mongodb.save_invite_link(channel_id, invite.invite_link, is_request)
        
        button_text = "• ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ •" if is_request else "• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •"
        button = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=invite.invite_link)]])
        
        wait_msg = await message.reply("<b>Please wait...</b>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(0.5)
        await wait_msg.delete()
        
        await message.reply(
            "<b>ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ! ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ</b>",
            reply_markup=button,
            parse_mode=ParseMode.HTML
        )
        
        note_msg = await message.reply(
            "<u><b>Note: If the link expires, click the post link again to get a new one.</b></u>",
            parse_mode=ParseMode.HTML
        )
        
        asyncio.create_task(delete_after_delay(note_msg, 300))
        
        asyncio.create_task(revoke_invite_after_minutes(client, channel_id, invite.invite_link, 5))
        
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Link sharing error: {e}")
        await message.reply("<b>❌ An unexpected error occurred while generating your link.</b>", parse_mode=ParseMode.HTML)

async def delete_after_delay(msg, delay):
    """Helper to delete message after delay"""
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass
