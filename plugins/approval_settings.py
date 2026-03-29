#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout

APPROVAL_PHOTO = "https://graph.org/file/f59a5ff9aa7ec7f2c44cb-0aecfb57f2d38d364e.jpg"
PAGE_SIZE = 8

@Client.on_callback_query(filters.regex("^auto_approve$"))
async def approval_settings_entry(client: Client, query: CallbackQuery):
    await query.answer()
    await approval_panel(client, query)

async def approval_panel(client: Client, query: CallbackQuery):
    """Generates and displays the main Auto Approval settings panel."""
    is_enabled = getattr(client, 'auto_approval_enabled', False)
    delay = getattr(client, 'approval_delay', 5)
    
    status_text = "Eɴᴀʙʟᴇᴅ ✅" if is_enabled else "Dɪꜱᴀʙʟᴇᴅ ❌"
    toggle_button_text = "Dɪꜱᴀʙʟᴇ Mᴏᴅᴇ ❌" if is_enabled else "Eɴᴀʙʟᴇ Mᴏᴅᴇ ✅"

    enabled_channels_count = len(await client.mongodb.get_auto_approval_channels())

    caption = f"""<blockquote><b>✧ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴀʟ ꜱᴇᴛᴛɪɴɢꜱ</b></blockquote>
<b><blockquote>🚦 ɢʟᴏʙᴀʟ ꜱᴛᴀᴛᴜꜱ: {status_text}</blockquote></b>
<b><blockquote>⏱️ ᴀᴘᴘʀᴏᴠᴀʟ ᴅᴇʟᴀʏ: {delay} seconds</blockquote></b>
<b><blockquote>#️⃣ ᴄʜᴀɴɴᴇʟꜱ ᴄᴏɴꜰɪɢᴜʀᴇᴅ: {enabled_channels_count}</blockquote></b>

<i>Use the buttons below to manage the auto-approval system.</i>"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_button_text, callback_data="approval_toggle")],
        [InlineKeyboardButton("⏱ Sᴇᴛ Dᴇʟᴀʏ", callback_data="approval_set_delay")],
        [InlineKeyboardButton("➕ Aᴅᴅ Cʜᴀɴɴᴇʟ", callback_data="approval_add_ch"), InlineKeyboardButton("➖ Rᴇᴍᴏᴠᴇ Cʜᴀɴɴᴇʟ", callback_data="approval_rem_ch")],
        [InlineKeyboardButton("📜 Vɪᴇᴡ Cʜᴀɴɴᴇʟꜱ", callback_data="approval_view_channels_0")],
        [InlineKeyboardButton("‹ Bᴀᴄᴋ", callback_data="settings_pg2")]
    ])
    
    try:
        if query.message.photo:
            await query.message.edit_media(media=InputMediaPhoto(media=APPROVAL_PHOTO, caption=caption), reply_markup=reply_markup)
        else:
            await query.message.delete()
            await client.send_photo(chat_id=query.message.chat.id, photo=APPROVAL_PHOTO, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in approval_panel: {e}")
        await query.message.edit_text(caption, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^approval_view_channels_(\d+)"))
async def view_approval_channels_cb(client, query: CallbackQuery):
    """Callback for the 'View Channels' button with pagination."""
    page = int(query.data.split("_")[-1])
    channels = await client.mongodb.get_auto_approval_channels()
    
    if not channels:
        await query.answer("No channels are configured for auto-approval yet.", show_alert=True)
        return

    await send_approval_channels_page(client, query, channels, page)

async def send_approval_channels_page(client, query, channels, page):
    """Sends a paginated list of auto-approved channels."""
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    
    text_lines = []
    for idx, channel_id in enumerate(channels[start_idx:end_idx], start=start_idx + 1):
        try:
            chat = await client.get_chat(channel_id)
            text_lines.append(f"<b>{idx}. {chat.title}</b>\n   <code>{channel_id}</code>")
        except Exception:
            text_lines.append(f"<b>{idx}. Invalid Channel</b>\n   <code>{channel_id}</code>")
    
    caption = "<blockquote><b>📜 Auto-Approved Channels</b></blockquote>\n" + "\n\n".join(text_lines)
    caption += f"\n\n<b>Page {page + 1} of {total_pages}</b>"
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"approval_view_channels_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"approval_view_channels_{page+1}"))
    
    buttons = [nav_buttons] if nav_buttons else []
    buttons.append([InlineKeyboardButton("‹ Bᴀᴄᴋ", callback_data="auto_approve")])
    
    await query.message.edit_caption(caption=caption, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^approval_toggle$"))
async def approval_toggle(client: Client, query: CallbackQuery):
    current_status = getattr(client, 'auto_approval_enabled', False)
    client.auto_approval_enabled = not current_status
    await client.mongodb.save_bot_setting('auto_approval_enabled', client.auto_approval_enabled)
    await query.answer(f"Auto Approval has been {'Enabled' if client.auto_approval_enabled else 'Disabled'}", show_alert=True)
    await approval_panel(client, query)

@Client.on_callback_query(filters.regex("^approval_set_delay$"))
async def set_approval_delay(client: Client, query: CallbackQuery):
    await query.message.delete()
    prompt = await client.send_message(query.from_user.id, "Please send the new approval delay in seconds (e.g., `5`).")
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        delay = int(res.text.strip())
        if delay >= 0:
            client.approval_delay = delay
            await client.mongodb.save_bot_setting('approval_delay', client.approval_delay)
            await res.reply(f'✅ Approval delay has been set to {delay} seconds.')
        else:
            await res.reply("❌ Please enter a non-negative number.")
    except (ListenerTimeout, ValueError):
        await prompt.reply("<b>Timeout or invalid input! No changes were made.</b>")
    
    dummy_msg = await client.send_message(query.from_user.id, "Loading...")
    query.message = dummy_msg
    await approval_panel(client, query)
    await dummy_msg.delete()

@Client.on_callback_query(filters.regex("^(approval_add_ch|approval_rem_ch)$"))
async def manage_approval_channel(client: Client, query: CallbackQuery):
    action = query.data
    await query.message.delete()
    prompt_text = "send the Channel ID to **add** to auto-approval." if "add" in action else "send the Channel ID to **remove** from auto-approval."
    prompt = await client.send_message(query.from_user.id, f"Please {prompt_text}")
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id = int(res.text.strip())
        
        if "add" in action:
            await client.mongodb.set_auto_approval(channel_id, True)
            await res.reply(f"✅ Channel `{channel_id}` will now be auto-approved.")
        else:
            await client.mongodb.set_auto_approval(channel_id, False)
            await res.reply(f"✅ Channel `{channel_id}` will no longer be auto-approved.")
    except (ListenerTimeout, ValueError):
        await prompt.reply("<b>Timeout or invalid input! No changes were made.</b>")
        
    dummy_msg = await client.send_message(query.from_user.id, "Loading...")
    query.message = dummy_msg
    await approval_panel(client, query)
    await dummy_msg.delete()
