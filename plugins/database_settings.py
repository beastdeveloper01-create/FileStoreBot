#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import is_bot_admin

DB_SETTINGS_PHOTO_URL = "https://graph.org/file/7d25f187b033c8d31f29b-b2310e1fd72d0aca4c.jpg"

async def get_db_settings_panel(client: Client):
    """Generates the photo, text, and markup for the DB settings panel."""
    photo_url = DB_SETTINGS_PHOTO_URL
    
    databases = client.databases
    primary_db = databases.get('primary')
    secondary_dbs = databases.get('secondary', [])
    backup_db = databases.get('backup')

    async def get_chat_title(chat_id):
        if not chat_id: return "Not Set"
        try:
            chat = await client.get_chat(chat_id)
            return f"{chat.title} (<code>{chat_id}</code>)"
        except Exception:
            return f"Invalid Channel (<code>{chat_id}</code>)"

    primary_text = await get_chat_title(primary_db)
    backup_text = await get_chat_title(backup_db)
    
    secondary_lines = []
    if secondary_dbs:
        for db_id in secondary_dbs:
            secondary_lines.append(f"› {await get_chat_title(db_id)}")
    secondary_text = "\n".join(secondary_lines) if secondary_lines else "› <i>None</i>"

    caption_text = f"""<blockquote><b>✧ DATABASE CHANNEL SETTINGS</b></blockquote>
<b>❆ ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅᴀᴛᴀʙᴀꜱᴇ :</b>
›› {primary_text}

<b>❆ ꜱᴇᴄᴏɴᴅᴀʀʏ ᴅᴀᴛᴀʙᴀꜱᴇꜱ :</b>
›› {secondary_text}

<b>❆ ʙᴀᴄᴋᴜᴘ ᴅᴀᴛᴀʙᴀꜱᴇ :</b>
›› {backup_text}

<i>Use the buttons below to manage your database channels.</i>
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('››ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db'), InlineKeyboardButton('››ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db')],
        [InlineKeyboardButton('››ꜱᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db'), InlineKeyboardButton('››ꜱᴇᴛ ʙᴀᴄᴋᴜᴘ', 'set_backup_db')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings_pg1')]
    ])
    
    return photo_url, caption_text, reply_markup

@Client.on_message(filters.command('database') & filters.private)
async def db_settings_command(client: Client, message: Message):
    """Handles the /database command."""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    photo, caption, reply_markup = await get_db_settings_panel(client)
    
    if photo:
        await message.reply_photo(photo=photo, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def db_settings(client: Client, query: CallbackQuery):
    """
    Displays the main Database Channels settings menu from a callback.
    """
    await query.answer()
    photo, caption, reply_markup = await get_db_settings_panel(client)
    
    if photo and not query.message.photo:
        await query.message.delete()
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif photo and query.message.photo:
         await query.message.edit_caption(caption=caption, reply_markup=reply_markup)
    else:
        await query.message.edit_text(caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def update_db_channel(client, query, action):
    """Helper to add, remove, or set DB channels."""
    await query.answer()
    
    prompts = {
        "add_db": "Send the Channel ID for the new <b>Secondary</b> database.",
        "rm_db": "Send the Channel ID of the database to remove.",
        "set_primary_db": "Send the Channel ID to set as <b>Primary</b>.\n(Must already be a secondary channel)",
        "set_backup_db": "Send the Channel ID to set as <b>Backup</b>."
    }
    
    prompt_msg_text = f"<blockquote>{prompts[action]}</blockquote>"

    if query.message.photo:
        await query.message.edit_caption(caption=prompt_msg_text)
        prompt_msg = query.message
    else:
        prompt_msg = await query.message.edit_text(prompt_msg_text, reply_markup=None, parse_mode=ParseMode.HTML)


    try:
        response = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=90)
        channel_id = int(response.text.strip())

        if action == "add_db":
            is_admin, reason = await is_bot_admin(client, channel_id)
            if not is_admin:
                return await response.reply(f"<b>Error:</b> {reason}", parse_mode=ParseMode.HTML)
            if 'secondary' not in client.databases: client.databases['secondary'] = []
            if channel_id in client.databases['secondary']:
                return await response.reply("This channel is already a secondary database.", parse_mode=ParseMode.HTML)
            client.databases['secondary'].append(channel_id)
            await response.reply(f"✅ Channel <code>{channel_id}</code> added as a secondary database.", parse_mode=ParseMode.HTML)

        elif action == "rm_db":
            found = False
            if client.databases.get('primary') == channel_id:
                return await response.reply("Cannot remove the primary database. Set a new primary first.", parse_mode=ParseMode.HTML)
            if client.databases.get('backup') == channel_id:
                client.databases['backup'] = None
                found = True
            if channel_id in client.databases.get('secondary', []):
                client.databases['secondary'].remove(channel_id)
                found = True
            
            if found:
                await response.reply(f"✅ Channel <code>{channel_id}</code> has been removed.", parse_mode=ParseMode.HTML)
            else:
                await response.reply("❌ Channel not found in any database configuration.", parse_mode=ParseMode.HTML)
        
        elif action == "set_primary_db":
            if channel_id not in client.databases.get('secondary', []):
                return await response.reply("This channel must be a secondary database first.", parse_mode=ParseMode.HTML)
            old_primary = client.databases.get('primary')
            client.databases['primary'] = channel_id
            client.databases['secondary'].remove(channel_id)
            if old_primary:
                client.databases['secondary'].append(old_primary)
            await response.reply(f"✅ <code>{channel_id}</code> is now the primary database.", parse_mode=ParseMode.HTML)

        elif action == "set_backup_db":
            is_admin, reason = await is_bot_admin(client, channel_id)
            if not is_admin:
                return await response.reply(f"<b>Error:</b> {reason}", parse_mode=ParseMode.HTML)
            client.databases['backup'] = channel_id
            await response.reply(f"✅ <code>{channel_id}</code> is now the backup database.", parse_mode=ParseMode.HTML)

        client.db = client.databases.get('primary')
        client.all_db_ids = [db_id for db_id in [client.databases.get('primary')] + client.databases.get('secondary', []) if db_id]
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        
    except ListenerTimeout:
         pass
    except (ValueError, TypeError):
        await query.message.reply("<b>Invalid ID format.</b> Please send a correct Channel ID.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await query.message.reply(f"An error occurred: <code>{e}</code>", parse_mode=ParseMode.HTML)
    
    await db_settings(client, query)

@Client.on_callback_query(filters.regex("^(add|rm|set_primary|set_backup)_db$"))
async def db_callbacks(client: Client, query: CallbackQuery):
    await update_db_channel(client, query, query.data)
