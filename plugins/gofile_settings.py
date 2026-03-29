#  Developed by t.me/napaaextra

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, Message
from pyrogram.errors.pyromod import ListenerTimeout
from pyrogram.enums import ParseMode

GOFILE_SETTINGS_PHOTO = "https://graph.org/file/4028a09d790f4757c7e39-246b262e0dc2523cca.jpg"

@Client.on_callback_query(filters.regex("^gofile_settings$"))
async def gofile_settings_entry(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("Admin only!", show_alert=True)
    await query.answer()
    await gofile_panel(client, query.message)

async def gofile_panel(client, message: Message, edit=True):
    """
    Generates and displays the Gofile.io settings panel.
    Now correctly handles a Message object directly.
    """
    is_enabled = getattr(client, 'gofile_enabled', False)
    tokens = client.gofile_manager.tokens if client.gofile_manager else []
    
    status_text = "Eɴᴀʙʟᴇᴅ ✅" if is_enabled else "Dɪꜱᴀʙʟᴇᴅ ❌"
    toggle_button_text = "Dɪꜱᴀʙʟᴇ Gofile ❌" if is_enabled else "Eɴᴀʙʟᴇ Gofile ✅"

    token_lines = []
    if tokens:
        for i, token in enumerate(tokens):
            masked_token = f"{token[:5]}...{token[-5:]}" if len(token) > 10 else token
            token_lines.append(f"<b>•</b> <code>{masked_token}</code>")
    else:
        token_lines.append("<i>No tokens configured.</i>")
    
    token_display_text = "\n".join(token_lines)

    caption = f"""<blockquote><b>✧ ɢᴏꜰɪʟᴇ.ɪᴏ ꜱᴇᴛᴛɪɴɢꜱ</b></blockquote>
<b><blockquote>🚦 ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛᴜꜱ: {status_text}</blockquote></b>

<b>›› ᴄᴏɴғɪɢᴜʀᴇᴅ ᴀᴘɪ ᴛᴏᴋᴇɴs:</b>
{token_display_text}

<i>When enabled, a Gofile download button is added to files. The upload process runs in the background.</i>"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_button_text, callback_data="gofile_toggle")],
        [InlineKeyboardButton("➕ Aᴅᴅ Tᴏᴋᴇɴ", callback_data="gofile_add_token"), InlineKeyboardButton("➖ Rᴇᴍᴏᴠᴇ Tᴏᴋᴇɴ", callback_data="gofile_remove_token")],
        [InlineKeyboardButton("‹ Bᴀᴄᴋ", callback_data="settings_pg2")]
    ])
    
    try:
        if edit and message.photo:
            await message.edit_media(media=InputMediaPhoto(media=GOFILE_SETTINGS_PHOTO, caption=caption), reply_markup=reply_markup)
        elif edit and not message.photo:
             await message.edit_text(caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else: # Send as a new message if not editing
             await message.delete()
             await client.send_photo(chat_id=message.chat.id, photo=GOFILE_SETTINGS_PHOTO, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in gofile_panel: {e}")

@Client.on_callback_query(filters.regex("^gofile_toggle$"))
async def gofile_toggle(client: Client, query: CallbackQuery):
    client.gofile_enabled = not getattr(client, 'gofile_enabled', False)
    await client.mongodb.save_bot_setting('gofile_enabled', client.gofile_enabled)
    await query.answer(f"Gofile.io feature has been {'Enabled' if client.gofile_enabled else 'Disabled'}", show_alert=True)
    await gofile_panel(client, query.message)

@Client.on_callback_query(filters.regex("^gofile_add_token$"))
async def gofile_add_token(client: Client, query: CallbackQuery):
    await query.message.delete()
    prompt = await client.send_message(query.from_user.id, "Please send your new Gofile.io API token. Type `cancel` to abort.")
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=120)
        new_token = res.text.strip()
        
        if new_token.lower() == 'cancel':
            await res.reply("🚫 Action cancelled.")
        else:
            current_tokens = client.gofile_manager.tokens
            if new_token in current_tokens:
                await res.reply("⚠️ This token already exists.")
            else:
                current_tokens.append(new_token)
                client.gofile_manager.tokens = current_tokens
                client.gofile_manager.token_count = len(current_tokens)
                await client.mongodb.save_bot_setting('gofile_tokens', current_tokens)
                await res.reply("✅ New Gofile token added successfully!")

    except ListenerTimeout:
        await prompt.reply("<b>Timeout! No changes were made.</b>")
    
    await gofile_panel(client, await client.send_message(query.from_user.id, "Loading menu..."), edit=False)

@Client.on_callback_query(filters.regex("^gofile_remove_token$"))
async def gofile_remove_token_menu(client: Client, query: CallbackQuery):
    tokens = client.gofile_manager.tokens
    if not tokens:
        return await query.answer("There are no tokens to remove.", show_alert=True)

    buttons = []
    for i, token in enumerate(tokens):
        masked_token = f"{token[:5]}...{token[-5:]}"
        buttons.append([InlineKeyboardButton(f"❌ {masked_token}", callback_data=f"gofile_confirm_remove_{i}")])
    
    buttons.append([InlineKeyboardButton("‹ Back to Gofile Menu", callback_data="gofile_settings")])
    
    await query.message.edit_caption(
        caption="Select a token to remove:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^gofile_confirm_remove_(\d+)$"))
async def gofile_confirm_remove(client: Client, query: CallbackQuery):
    token_index = int(query.data.split("_")[-1])
    
    current_tokens = client.gofile_manager.tokens
    if token_index >= len(current_tokens):
        await query.answer("Invalid token selection. It might have been already removed.", show_alert=True)
        return await gofile_panel(client, query.message)
        
    removed_token = current_tokens.pop(token_index)
    client.gofile_manager.tokens = current_tokens
    client.gofile_manager.token_count = len(current_tokens)
    await client.mongodb.save_bot_setting('gofile_tokens', current_tokens)
    
    await query.answer(f"Token ending in ...{removed_token[-5:]} has been removed.", show_alert=True)
    await gofile_panel(client, query.message)
