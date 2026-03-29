#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout

FILES_SETTINGS_PHOTO = "https://graph.org/file/0712089d03d4fef3bf72e-b21a9c16e83805ddae.jpg"

@Client.on_callback_query(filters.regex("^file_settings$"))
async def file_settings_entry(client: Client, query: CallbackQuery):
    await query.answer()
    await file_settings_panel(client, query)

async def file_settings_panel(client: Client, query: CallbackQuery):
    """Generates and displays the Files Related Settings panel."""
    
    protect_enabled = getattr(client, 'protect', False)
    hide_caption_enabled = getattr(client, 'hide_caption', False)
    button_enabled = getattr(client, 'channel_button_enabled', False)
    button_name = getattr(client, 'button_name', "Not Set")
    button_url = getattr(client, 'button_url', "Not Set")

    protect_status = "Eɴᴀʙʟᴇᴅ ✔" if protect_enabled else "Dɪꜱᴀʙʟᴇᴅ ✘"
    caption_status = "Eɴᴀʙʟᴇᴅ ✔" if hide_caption_enabled else "Dɪꜱᴀʙʟᴇᴅ ✘"
    button_status = "Eɴᴀʙʟᴇᴅ ✔" if button_enabled else "Dɪꜱᴀʙʟᴇᴅ ✘"
    
    caption = f"""<blockquote><b>✧ ꜰɪʟᴇꜱ ʀᴇʟᴀᴛᴇᴅ ꜱᴇᴛᴛɪɴɢꜱ</b></blockquote>
<pre><b>🔒 ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ: {protect_status}</b></pre>
<pre><b>🫥 ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ: {caption_status}</b></pre>
<pre><b>🔘 ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ: {button_status}</b></pre>
<blockquote><b>›› ʙᴜᴛᴛᴏɴ ᴅᴇᴛᴀɪʟꜱ</b>\n
<b>›› ʙᴜᴛᴛᴏɴ ɴᴀᴍᴇ:</b> <code>{button_name}</code>
<b>›› ʙᴜᴛᴛᴏɴ ʟɪɴᴋ:</b> <code>{button_url}</code></blockquote>\n
<b>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs</b>"""

    protect_btn_text = f"Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ: {'✔' if not protect_enabled else '✘'}"
    caption_btn_text = f"Hɪᴅᴇ Cᴀᴘᴛɪᴏɴ: {'✔' if not hide_caption_enabled else '✘'}"
    button_btn_text = f"Cʜᴀɴɴᴇʟ Bᴜᴛᴛᴏɴ: {'✔' if not button_enabled else '✘'}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(protect_btn_text, callback_data="toggle_protect"), InlineKeyboardButton(caption_btn_text, callback_data="toggle_hide_caption")],
        [InlineKeyboardButton(button_btn_text, callback_data="toggle_channel_button"), InlineKeyboardButton("Sᴇᴛ Bᴜᴛᴛᴏɴ ➪", callback_data="set_button")],
        [InlineKeyboardButton("‹ Bᴀᴄᴋ", callback_data="settings_pg2"), InlineKeyboardButton("Cʟᴏꜱᴇ ✘", callback_data="close")]
    ])
    
    try:
        if query.message.photo:
            await query.message.edit_media(media=InputMediaPhoto(media=FILES_SETTINGS_PHOTO, caption=caption), reply_markup=reply_markup)
        else:
            await query.message.delete()
            await client.send_photo(chat_id=query.message.chat.id, photo=FILES_SETTINGS_PHOTO, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in file_settings_panel: {e}")


@Client.on_callback_query(filters.regex("^toggle_protect$"))
async def toggle_protect_content(client: Client, query: CallbackQuery):
    client.protect = not getattr(client, 'protect', False)
    await client.mongodb.save_bot_setting('protect_content', client.protect)
    await query.answer(f"Protect Content is now {'ENABLED' if client.protect else 'DISABLED'}")
    await file_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^toggle_hide_caption$"))
async def toggle_hide_caption(client: Client, query: CallbackQuery):
    client.hide_caption = not getattr(client, 'hide_caption', False)
    await client.mongodb.save_bot_setting('hide_caption', client.hide_caption)
    await query.answer(f"Hide Caption is now {'ENABLED' if client.hide_caption else 'DISABLED'}")
    await file_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^toggle_channel_button$"))
async def toggle_channel_button(client: Client, query: CallbackQuery):
    client.channel_button_enabled = not getattr(client, 'channel_button_enabled', False)
    await client.mongodb.save_bot_setting('channel_button_enabled', client.channel_button_enabled)
    await query.answer(f"Channel Button is now {'ENABLED' if client.channel_button_enabled else 'DISABLED'}")
    await file_settings_panel(client, query)


@Client.on_callback_query(filters.regex("^set_button$"))
async def set_button_details(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.delete()
    
    prompt = await client.send_message(
        query.from_user.id,
        "Please send the button details in the following format:\n\n`Button Name | https://your-link.com`",
        parse_mode=ParseMode.MARKDOWN
    )
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=120)
        parts = res.text.split('|', 1)
        if len(parts) == 2:
            button_name = parts[0].strip()
            button_url = parts[1].strip()
            if button_url.startswith("http"):
                client.button_name = button_name
                client.button_url = button_url
                await client.mongodb.save_bot_setting('button_name', button_name)
                await client.mongodb.save_bot_setting('button_url', button_url)
                await res.reply("✔ 𝙱𝚞𝚝𝚝𝚘𝚗 𝚍𝚎𝚝𝚊𝚒𝚕𝚜 𝚑𝚊𝚟𝚎 𝚋𝚎𝚎𝚗 𝚞𝚙𝚍𝚊𝚝𝚎𝚍 𝚜𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢!")
            else:
                await res.reply("❌ Invalid URL. Please make sure the link starts with `http` or `https`.")
        else:
            await res.reply("❌ Invalid format. Please use `Name | URL`.")
    except ListenerTimeout:
        await prompt.edit("<b>Timeout! No changes were made.</b>")
    
    dummy_msg = await client.send_message(query.from_user.id, "Loading...")
    query.message = dummy_msg
    await file_settings_panel(client, query)
    await dummy_msg.delete()
