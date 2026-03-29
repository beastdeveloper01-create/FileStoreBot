#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout

@Client.on_callback_query(filters.regex("^settings$"))
async def settings_main(client, query):
    await settings_page_1(client, query)

@Client.on_callback_query(filters.regex("^settings_pg1$"))
async def settings_page_1_cb(client, query):
    await settings_page_1(client, query)

async def settings_page_1(client, query):
    """Displays Page 1 of the settings menu, matching the video."""
    await query.answer()
    msg = """<blockquote><b>⚙️ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ (ᴘᴀɢᴇ 1/3)</b></blockquote>
ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴛʜᴇ ʙᴏᴛ'ꜱ ᴄᴏʀᴇ ꜰᴇᴀᴛᴜʀᴇꜱ.
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ", callback_data="fsub"), InlineKeyboardButton("ᴅʙ ᴄʜᴀɴɴᴇʟꜱ", callback_data="db_settings")],
        [InlineKeyboardButton("ᴀᴅᴍɪɴꜱ", callback_data="admins"), InlineKeyboardButton("ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="auto_del")],
        [InlineKeyboardButton("✨ ᴀᴜᴛᴏʙᴀᴛᴄʜ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="autobatch_settings")],
        [InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="home"), InlineKeyboardButton("›› ɴᴇxᴛ", callback_data="settings_pg2")]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("^settings_pg2$"))
async def settings_page_2(client, query):
    """Displays Page 2 of the settings menu with shortener."""
    await query.answer()
    protect_status_text = f"ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ: {'✅' if client.protect else '❌'}"
    msg = """<blockquote><b>⚙️ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ (ᴘᴀɢᴇ 2/3)</b></blockquote>
ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴛʜᴇ ʙᴏᴛ'ꜱ ᴄᴏʀᴇ ꜰᴇᴀᴛᴜʀᴇꜱ.
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Fɪʟᴇs Sᴇᴛᴛɪɴɢs", callback_data="file_settings")],
        [InlineKeyboardButton("ᴘʜᴏᴛᴏꜱ", callback_data="photos"), InlineKeyboardButton("ᴛᴇxᴛꜱ", callback_data="texts")],
        [InlineKeyboardButton("🔗 ꜱʜᴏʀᴛɴᴇʀ", callback_data="shortner"), InlineKeyboardButton("💰 ᴄʀᴇᴅɪᴛ ꜱʏꜱᴛᴇᴍ", callback_data="credit_settings")],
        [InlineKeyboardButton("✅ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ", callback_data="auto_approve"), InlineKeyboardButton("📂 ɢᴏꜰɪʟᴇ.ɪᴏ", callback_data="gofile_settings")],
        [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="settings_pg1"), InlineKeyboardButton("›› ɴᴇxᴛ", callback_data="settings_pg3")]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("^file_settings$"))
async def file_settings_cb(client, query):
    from plugins.file_settings import file_settings_panel
    await file_settings_panel(client, query)
    
@Client.on_callback_query(filters.regex("^settings_pg3$"))
async def settings_page_3(client, query):
    """Displays Page 3 of the settings menu with link sharing."""
    await query.answer()
    
    link_channels = await client.mongodb.get_link_channels()
    channel_count = len(link_channels)
    
    msg = f"""<blockquote><b>⚙️ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ (ᴘᴀɢᴇ 3/3)</b></blockquote>

<b>ʟɪɴᴋ ꜱʜᴀʀɪɴɢ ꜱʏꜱᴛᴇᴍ</b>

<b>ꜱᴛᴀᴛᴜꜱ:</b> {'✓ 𝙰𝚌𝚝𝚒𝚟𝚎' if channel_count > 0 else '✗ 𝙽𝚘 𝚌𝚑𝚊𝚗𝚗𝚎𝚕 𝚊𝚍𝚍𝚎𝚍'}
<b>ᴄᴏɴꜰɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟꜱ:</b> {channel_count}

<i>Manage your link sharing channels and generate temporary invite links.</i>
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴍᴀɴᴀɢᴇ ᴄʜᴀɴɴᴇʟꜱ", callback_data="link_manage"), InlineKeyboardButton("ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋꜱ", callback_data="link_generate")],
        [InlineKeyboardButton("ʟɪɴᴋ ʜᴇʟᴘ", callback_data="link_help_settings")],
        [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="settings_pg2"), InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="home")]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("^link_manage$"))
async def link_manage_callback(client, query):
    """Show link sharing channel management options"""
    await query.answer()
    
    link_channels = await client.mongodb.get_link_channels()
    
    if not link_channels:
        text = """<b>📋 Link Sharing Channels</b>

<i>No channels configured yet.</i>

<b>To add a channel:</b>
1. Make the bot admin in your channel
2. Use: <code>/addch {channel_id}</code>
3. Get the channel ID from @MissRose_bot

<b>Example:</b>
<code>/addch -1001234567890</code>"""
    else:
        text = "<b><blockquote>✧ʟɪɴᴋ ꜱʜᴀʀɪɴɢ ᴄʜᴀɴɴᴇʟꜱ</blockquote></b>\n<b>›› ᴄᴏɴꜰɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟꜱ:</b>\n"
        for idx, channel_id in enumerate(link_channels[:5], 1):
            try:
                chat = await client.get_chat(channel_id)
                text += f"<b>{idx}. {chat.title}</b>\n   <code>{channel_id}</code>\n\n"
            except:
                text += f"{idx}. <code>{channel_id}</code> (Error)\n\n"
        
        if len(link_channels) > 5:
            text += f"<i>...and {len(link_channels) - 5} more</i>\n\n"
        
        text += "<b>Commands:</b>\n"
        text += "• <code>/addch {id}</code> - Add channel\n"
        text += "• <code>/delch {id}</code> - Remove channel\n"
        text += "• <code>/channels</code> - View all"
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data="settings_pg3")
        ]]),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^link_generate$"))
async def link_generate_callback(client, query):
    """Show quick link generation info"""
    await query.answer()
    
    text = """<b>🔗 Link Generation</b>

<b>Available Commands:</b>

• <code>/links</code>
  Show all normal & request links

• <code>/reqlink</code>
  Show request links with buttons

• <code>/bulklink {id1} {id2}</code>
  Generate links for multiple channels

<b>Link Types:</b>
• <b>Normal Link:</b> Direct join
• <b>Request Link:</b> Requires approval

<b>Security:</b>
• Links auto-expire in 5 minutes
• New links generated on each click
• Protects from copyright issues

<b>Example:</b>
<code>/bulklink -1001234567890 -1009876543210</code>"""
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data="settings_pg3")
        ]]),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^link_help_settings$"))
async def link_help_settings_callback(client, query):
    """Show link sharing help from settings"""
    await query.answer()
    
    text = """<b>❓ Link Sharing Help</b>

<b>What is Link Sharing?</b>
A system to share temporary invite links that auto-expire after 5 minutes. Protects your channels from copyright strikes.

<b>Setup Steps:</b>
1. Add bot as admin in your channel
2. Use <code>/addch {channel_id}</code>
3. Bot generates 2 types of links
4. Share links in your posts
5. Links refresh automatically

<b>Key Features:</b>
✅ Auto-expiring links (5 min)
✅ Normal & request-to-join
✅ Bulk generation support
✅ Works with file sharing
✅ No conflicts with existing features

<b>Commands:</b>
• <code>/linkhelp</code> - Detailed help
• <code>/addch</code> - Add channel
• <code>/links</code> - Generate links
• <code>/channels</code> - View all

<b>Integration:</b>
Link sharing works independently alongside your file sharing bot. Both systems function simultaneously without any conflicts."""
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data="settings_pg3")
        ]]),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub_settings_cb(client, query):
    from plugins.force_sub import fsub
    await fsub(client, query)

@Client.on_callback_query(filters.regex("^db_settings$"))
async def db_settings_cb(client, query):
    from plugins.database_settings import db_settings
    await db_settings(client, query)

@Client.on_callback_query(filters.regex("^admins$"))
async def admins_settings_cb(client, query):
    from plugins.admins import admins
    await admins(client, query)

@Client.on_callback_query(filters.regex("^photos$"))
async def photos(client, query):
    msg = f"""<blockquote><b>🖼️ ᴍᴇᴅɪᴀ & ᴘʜᴏᴛᴏꜱ</b></blockquote>
𝚂𝚎𝚝 𝚘𝚛 𝚛𝚎𝚖𝚘𝚟𝚎 𝚝𝚑𝚎 𝚒𝚖𝚊𝚐𝚎𝚜 𝚞𝚜𝚎𝚍 𝚒𝚗 𝚝𝚑𝚎 𝚋𝚘𝚝'𝚜 𝚖𝚎𝚜𝚜𝚊𝚐𝚎𝚜.

<b>›› ꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ :</b> <code>{'𝙰𝚍𝚍𝚎𝚍' if client.messages.get('START_PHOTO') else '𝙽𝚘𝚝 𝚊𝚍𝚍𝚎𝚍'}</code>
<b>›› ꜰꜱᴜʙ ᴘʜᴏᴛᴏ :</b> <code>{'𝙰𝚍𝚍𝚎𝚍' if client.messages.get('FSUB_PHOTO') else '𝙽𝚘𝚝 𝚊𝚍𝚍𝚎𝚍'}</code>
"""
    reply_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            ('SET' if not client.messages.get("START_PHOTO") else 'ᴄʜᴀɴɢᴇ') + ' ꜱᴛᴀʀᴛ ᴘɪᴄ', 
            callback_data='add_start_photo'
        ),
        InlineKeyboardButton(
            ('SET' if not client.messages.get("FSUB_PHOTO") else 'ᴄʜᴀɴɢᴇ') + ' ꜰꜱᴜʙ ᴘɪᴄ', 
            callback_data='add_fsub_photo'
        )
    ],
    [
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ꜱᴛᴀʀᴛ ᴘɪᴄ', callback_data='rm_start_photo'),
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ꜰꜱᴜʙ ᴘɪᴄ', callback_data='rm_fsub_photo')
    ],
    [InlineKeyboardButton('‹ ʙᴀᴄᴋ', callback_data='settings_pg2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("^protect$"))
async def protect(client, query):
    client.protect = not client.protect
    await client.mongodb.save_settings(client.name, client.get_current_settings())
    await query.answer(f"Content Protection has been {'Enabled' if client.protect else 'Disabled'}")
    await settings_page_2(client, query)

@Client.on_callback_query(filters.regex("^texts$"))
async def texts_settings_cb(client, query):
    from plugins.texts import texts
    await texts(client, query)

@Client.on_callback_query(filters.regex('^rm_start_photo$'))
async def rm_start_photo(client, query):
    client.messages['START_PHOTO'] = ''
    await client.mongodb.save_settings(client.name, client.get_current_settings())
    await query.answer("Start Photo Removed!", show_alert=True)
    await photos(client, query)

@Client.on_callback_query(filters.regex('^rm_fsub_photo$'))
async def rm_fsub_photo(client, query):
    client.messages['FSUB_PHOTO'] = ''
    await client.mongodb.save_settings(client.name, client.get_current_settings())
    await query.answer("FSUB Photo Removed!", show_alert=True)
    await photos(client, query)

async def handle_photo_update(client, query, photo_key, prompt_text):
    await query.answer()
    prompt_message = await query.message.edit_text(prompt_text, parse_mode=ParseMode.HTML)
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=(filters.text | filters.photo), timeout=60)
        
        photo_val = ""
        if res.photo:
            photo_val = res.photo.file_id
        elif res.text and (res.text.startswith('https://') or res.text.startswith('http://')):
            photo_val = res.text
        
        if photo_val:
            client.messages[photo_key] = photo_val
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await query.message.edit_text(f"✅ <b>{photo_key.replace('_', ' ').title()}</b> has been updated!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'settings_pg2')]]), parse_mode=ParseMode.HTML)
        else:
            await query.message.edit_text("❌ Invalid input. Please send a photo or a valid URL.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'settings_pg2')]]), parse_mode=ParseMode.HTML)
    except ListenerTimeout:
        await prompt_message.edit_text("<b>Timeout! No changes were made.</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ Back', 'settings_pg2')]]), parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("^add_start_photo$"))
async def add_start_photo(client, query):
    await handle_photo_update(client, query, 'START_PHOTO', "<blockquote>Please send the photo for the <b>Start Message</b>.</blockquote>")

@Client.on_callback_query(filters.regex("^add_fsub_photo$"))
async def add_fsub_photo(client, query):
    await handle_photo_update(client, query, 'FSUB_PHOTO', "<blockquote>Please send the photo for the <b>Force Subscribe Message</b>.</blockquote>")
