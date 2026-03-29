#  Developed by t.me/napaaextra

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout

CREDIT_SETTINGS_PHOTO = "https://graph.org/file/70d0861e70a16a0b9631f-dd092107b7b4ae6e17.jpg"

@Client.on_callback_query(filters.regex("^credit_settings$"))
async def credit_settings_entry(client: Client, query: CallbackQuery):
    """Main entry point for the Credit System settings panel."""
    if query.from_user.id not in client.admins:
        return await query.answer("Admin only!", show_alert=True)
    await query.answer()
    await credit_panel(client, query)

async def credit_panel(client: Client, query: CallbackQuery):
    """Generates and displays the Credit System settings panel."""
    is_enabled = getattr(client, 'credit_system_enabled', False)
    credits_per_visit = getattr(client, 'credits_per_visit', 1)
    credits_per_file = getattr(client, 'credits_per_file', 1)
    max_limit = getattr(client, 'max_credit_limit', 100)
    
    status_text = "Eɴᴀʙʟᴇᴅ ✅" if is_enabled else "Dɪꜱᴀʙʟᴇᴅ ❌"
    toggle_button_text = "Dɪꜱᴀʙʟᴇ Sʏꜱᴛᴇᴍ ❌" if is_enabled else "Eɴᴀʙʟᴇ Sʏꜱᴛᴇᴍ ✅"
    max_limit_text = f"{max_limit} credits" if max_limit > 0 else "Unlimited"

    caption = f"""<blockquote><b>✧ ᴄʀᴇᴅɪᴛ ꜱʏꜱᴛᴇᴍ ꜱᴇᴛᴛɪɴɢꜱ</b></blockquote>
<b><blockquote>🚦 ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛᴜꜱ: {status_text}</blockquote></b>
<b><blockquote>💰 ᴄʀᴇᴅɪᴛꜱ ᴇᴀʀɴᴇᴅ ᴘᴇʀ ʟɪɴᴋ: {credits_per_visit}</blockquote></b>
<b><blockquote>💸 ᴄᴏꜱᴛ ᴘᴇʀ ꜰɪʟᴇ ᴀᴄᴄᴇꜱꜱ: {credits_per_file}</blockquote></b>
<b><blockquote>⚡️ ᴍᴀx ᴄʀᴇᴅɪᴛ ʟɪᴍɪᴛ: {max_limit_text}</blockquote></b>

<i>Configure the credit system for non-admin/non-premium users. When enabled, this overrides the default shortener for file access.</i>"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_button_text, callback_data="credit_toggle")],
        [InlineKeyboardButton("💰 Sᴇᴛ Eᴀʀɴ Aᴍᴏᴜɴᴛ", callback_data="credit_set_visit"), InlineKeyboardButton("💸 Sᴇᴛ Fɪʟᴇ Cᴏꜱᴛ", callback_data="credit_set_cost")],
        [InlineKeyboardButton("⚡️ Sᴇᴛ Mᴀx Lɪᴍɪᴛ", callback_data="credit_set_limit")],
        [InlineKeyboardButton("‹ Bᴀᴄᴋ", callback_data="settings_pg2")]
    ])
    
    try:
        if query.message.photo:
            await query.message.edit_media(media=InputMediaPhoto(media=CREDIT_SETTINGS_PHOTO, caption=caption), reply_markup=reply_markup)
        else:
            await query.message.delete()
            await client.send_photo(chat_id=query.message.chat.id, photo=CREDIT_SETTINGS_PHOTO, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in credit_panel: {e}")
        await query.message.edit_text(caption, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^credit_toggle$"))
async def credit_toggle(client: Client, query: CallbackQuery):
    current_status = getattr(client, 'credit_system_enabled', False)
    client.credit_system_enabled = not current_status
    await client.mongodb.save_bot_setting('credit_system_enabled', client.credit_system_enabled)
    await query.answer(f"Credit System has been {'Enabled' if client.credit_system_enabled else 'Disabled'}", show_alert=True)
    await credit_panel(client, query)

async def set_credit_value(client: Client, query: CallbackQuery, setting_key: str, prompt_text: str, attribute_name: str):
    await query.message.delete()
    prompt = await client.send_message(query.from_user.id, prompt_text)
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        value = int(res.text.strip())
        if value >= 0:
            setattr(client, attribute_name, value)
            await client.mongodb.save_bot_setting(setting_key, value)
            await res.reply(f'✅ Value has been updated to {value}.')
        else:
            await res.reply("❌ Please enter a non-negative number.")
    except (ListenerTimeout, ValueError):
        await prompt.reply("<b>Timeout or invalid input! No changes were made.</b>")
    
    dummy_msg = await client.send_message(query.from_user.id, "Loading...")
    query.message = dummy_msg
    await credit_panel(client, query)
    await dummy_msg.delete()

@Client.on_callback_query(filters.regex("^credit_set_visit$"))
async def set_credits_per_visit_cb(client: Client, query: CallbackQuery):
    await set_credit_value(client, query, 'credits_per_visit', "Please send the number of credits a user earns per link visit.", 'credits_per_visit')

@Client.on_callback_query(filters.regex("^credit_set_cost$"))
async def set_credits_per_cost_cb(client: Client, query: CallbackQuery):
    await set_credit_value(client, query, 'credits_per_file', "Please send the credit cost for accessing a file link.", 'credits_per_file')

@Client.on_callback_query(filters.regex("^credit_set_limit$"))
async def set_max_credit_limit_cb(client: Client, query: CallbackQuery):
    await set_credit_value(client, query, 'max_credit_limit', "Please send the maximum credit limit for users.\n\nSet to `0` for unlimited.", 'max_credit_limit')
