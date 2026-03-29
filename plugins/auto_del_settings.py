#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from datetime import timedelta

AUTO_DEL_PHOTO = "https://graph.org/file/05a0e8ced8eab1a01b430-bd7cce57283ba44013.jpg"

def get_readable_time_string(seconds: int) -> str:
    """Converts seconds into a human-readable string like '15 Minutes'."""
    if not seconds or seconds == 0:
        return "Disabled"
    
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, sec = divmod(rem, 60)

    if days > 0: return f"{days} Day{'s' if days > 1 else ''}"
    if hours > 0: return f"{hours} Hour{'s' if hours > 1 else ''}"
    if minutes > 0: return f"{minutes} Minute{'s' if minutes > 1 else ''}"
    return f"{sec} Second{'s' if sec > 1 else ''}"

@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del_entry(client: Client, query: CallbackQuery):
    """Main entry point for the Auto Delete settings panel."""
    await query.answer()
    await auto_del_panel(client, query)

async def auto_del_panel(client: Client, query: CallbackQuery):
    """Generates and displays the Auto Delete settings panel."""
    is_enabled = client.auto_del > 0
    status_text = "Eɴᴀʙʟᴇᴅ ✅" if is_enabled else "Dɪꜱᴀʙʟᴇᴅ ❌"
    timer_text = get_readable_time_string(client.auto_del)
    
    caption = f"""<blockquote><b>✧ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ꜱᴇᴛᴛɪɴɢꜱ</b></blockquote>

<b><blockquote>🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ: {status_text}</blockquote></b>
<b><blockquote>⏱ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ: {timer_text}</blockquote></b>

<b>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs</b>"""

    toggle_button_text = "Dɪꜱᴀʙʟᴇ Mᴏᴅᴇ ❌" if is_enabled else "Eɴᴀʙʟᴇ Mᴏᴅᴇ ✅"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_button_text, callback_data="auto_del_toggle"), InlineKeyboardButton("›› Sᴇᴛ Tɪᴍᴇʀ", callback_data="auto_del_set_timer")],
        [InlineKeyboardButton("‹ Bᴀᴄᴋ", callback_data="settings_pg1"), InlineKeyboardButton("✗ Cʟᴏꜱᴇ", callback_data="close")]
    ])
    
    try:
        if query.message.photo:
            await query.message.edit_media(media=InputMediaPhoto(media=AUTO_DEL_PHOTO, caption=caption), reply_markup=reply_markup)
        else:
            await query.message.delete()
            await client.send_photo(chat_id=query.message.chat.id, photo=AUTO_DEL_PHOTO, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in auto_del_panel: {e}")
        await query.message.edit_text(caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("^auto_del_toggle$"))
async def auto_del_toggle(client: Client, query: CallbackQuery):
    """Toggles the auto-delete mode on or off."""
    if client.auto_del > 0:
        client.auto_del = 0
        await query.answer("Auto Delete has been Disabled!", show_alert=True)
    else:
        client.auto_del = 900 
        await query.answer("Auto Delete Enabled! (Default: 15 Minutes)", show_alert=True)

    await client.mongodb.save_settings(client.name, client.get_current_settings())
    await auto_del_panel(client, query)

@Client.on_callback_query(filters.regex("^auto_del_set_timer$"))
async def set_auto_del_timer(client: Client, query: CallbackQuery):
    """Prompts the user to set a new auto-delete timer."""
    await query.message.delete()
    prompt_message = await client.send_message(
        chat_id=query.from_user.id,
        text="<blockquote><b>⏱️ Set Auto Delete Timer</b></blockquote>\n\nEnter the new timer value in <b>seconds</b>.\n\nFor example, to set it to 15 minutes, enter `900`.",
        parse_mode=ParseMode.HTML
    )
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        timer_str = res.text.strip()
        
        if timer_str.lower() == 'cancel':
            await res.reply("🚫 Action cancelled.")
        else:
            timer = int(timer_str)
            if timer >= 0:
                client.auto_del = timer
                await client.mongodb.save_settings(client.name, client.get_current_settings())
                await res.reply(f'✅ Auto Delete timer has been set to <b>{get_readable_time_string(timer)}</b>!', parse_mode=ParseMode.HTML)
            else:
                await res.reply("❌ Invalid input. Please enter a non-negative number.")
    except ListenerTimeout:
        await prompt_message.edit("<b>Timeout! No changes were made.</b>")
    except ValueError:
        await prompt_message.reply("<b>❌ Invalid input. Please enter a valid number of seconds.</b>")
    
    dummy_message = await client.send_message(query.from_user.id, "Loading settings...")
    query.message = dummy_message
    await auto_del_panel(client, query)
    await dummy_message.delete()
