#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, Message
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout

AUTOBATCH_SETTINGS_PHOTO = "https://graph.org/file/11aa63f629c6ac0e106c9-8684bc2fc7d28ab1ac.jpg"

DEFAULT_AUTOBATCH_TEMPLATE = """<b>Generated Links ({totalfilecount} files)</b>

<b><u>Video Quality:</u></b>
<blockquote>{4k} ({4kfilecount}): {4klink}
{1080p} ({1080pfilecount}): {1080plink}
{720p} ({720pfilecount}): {720plink}
{480p} ({480pfilecount}): {480plink}</blockquote>
<b><u>Source/Encoding:</u></b>
<blockquote>{hdrip} ({hdripfilecount}): {hdriplink}
{bluray} ({blurayfilecount}): {bluraylink}
{webdl} ({webdlfilecount}): {webdllink}
{hevc} ({hevcfilecount}): {hevclink}</blockquote>
<b><u>Other:</u></b>
<blockquote>{other} ({otherfilecount}): {otherlink}</blockquote>"""

PLACEHOLDERS_TEXT = """<b><blockquote>✧ Available Placeholders ✧</blockquote></b>
You can use these placeholders in your custom template. If a quality is not found, its line will be removed.

<b><u>General:</u></b>
• <code>{totalfilecount}</code> - Total number of files.

<b><u>For Each Quality:</u></b>
Use the **lowercase** name for the quality:
<code>4k</code>, <code>1080p</code>, <code>720p</code>, <code>480p</code>, <code>hdrip</code>, <code>bluray</code>, <code>webdl</code>, <code>hevc</code>, or <code>other</code>.

• <code>{{quality}}</code> - The label (e.g., "HDRip").
• <code>{{quality}link}</code> - The migrator bot link.
• <code>{{quality}directlink}</code> - The direct bot link.
• <code>{{quality}filecount}</code> - The number of files.

<b><u>Example for HDRip:</u></b>
<code>{hdrip} ({hdripfilecount} files) - {hdriplink}</code>"""

async def show_autobatch_panel(client: Client, message: Message):
    """Displays the Autobatch settings panel (photo or text)."""
    current_template = getattr(client, 'autobatch_template', DEFAULT_AUTOBATCH_TEMPLATE)
    caption = f"""<b><blockquote>✧ ᴀᴜᴛᴏʙᴀᴛᴄʜ ᴛᴇᴍᴘʟᴀᴛᴇ ꜱᴇᴛᴛɪɴɢꜱ</blockquote></b>
<b>›› Cᴜʀʀᴇɴᴛ Tᴇᴍᴘʟᴀᴛᴇ:</b>
<pre>{current_template}</pre>"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("››Sᴇᴛ ɴᴇᴡ Tᴇᴍᴘʟᴀᴛᴇ", callback_data="autobatch_set_template"), InlineKeyboardButton("››Vɪᴇᴡ Pʟᴀᴄᴇʜᴏʟᴅᴇʀꜱ", callback_data="autobatch_placeholders")],
        [InlineKeyboardButton("››Rᴇꜱᴇᴛ ᴛᴏ Dᴇꜰᴀᴜʟᴛ", callback_data="autobatch_reset")],
        [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="settings_pg1")]
    ])
    
    try:
        if message.photo:
            await message.edit_media(media=InputMediaPhoto(media=AUTOBATCH_SETTINGS_PHOTO, caption=caption), reply_markup=reply_markup)
        else:
            await message.delete()
            await client.send_photo(chat_id=message.chat.id, photo=AUTOBATCH_SETTINGS_PHOTO, caption=caption, reply_markup=reply_markup)
    except Exception:
        if message.photo:
             await message.delete()
             await client.send_message(message.chat.id, caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
             await message.edit_text(caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("^autobatch_settings$"))
async def autobatch_settings_cb(client: Client, query: CallbackQuery):
    await query.answer()
    await show_autobatch_panel(client, query.message)

@Client.on_callback_query(filters.regex("^autobatch_set_template$"))
async def set_autobatch_template(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.delete()

    prompt = await client.send_message(
        query.from_user.id,
        "Please send the new template for the autobatch command. You can use standard Telegram HTML formatting (e.g., `<b>`, `<code>`).\n\nType /cancel to abort.",
        parse_mode=ParseMode.HTML
    )
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=300)
        if res.text and res.text.lower() == "/cancel":
            await res.reply("🚫 Action cancelled.")
        else:
            client.autobatch_template = res.text
            await client.mongodb.save_bot_setting('autobatch_template', client.autobatch_template)
            await res.reply("✅ Autobatch template has been updated successfully!")
    except ListenerTimeout:
        await prompt.reply("<b>Timeout! No changes were made.</b>")
    
    await show_autobatch_panel(client, await client.send_message(query.from_user.id, "Loading menu..."))

@Client.on_callback_query(filters.regex("^autobatch_placeholders$"))
async def view_autobatch_placeholders(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_caption(
        caption=PLACEHOLDERS_TEXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("‹ Back", callback_data="autobatch_settings")]])
    )

@Client.on_callback_query(filters.regex("^autobatch_reset$"))
async def reset_autobatch_template(client: Client, query: CallbackQuery):
    client.autobatch_template = DEFAULT_AUTOBATCH_TEMPLATE
    await client.mongodb.save_bot_setting('autobatch_template', client.autobatch_template)
    await query.answer("✅ Template has been reset to default.", show_alert=True)
    await show_autobatch_panel(client, query.message)
