#  Developed by t.me/napaaextra
"""
Help command for Link Sharing features
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('linkhelp') & filters.private)
async def link_help_command(client: Client, message: Message):
    """Show help for link sharing features"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    help_text = """<b>🔗 Link Sharing Features</b>

<b>➤ Channel Management:</b>
• <code>/addch {channel_id}</code> - Add a channel to link sharing
• <code>/delch {channel_id}</code> - Remove a channel from link sharing
• <code>/channels</code> - Show all configured channels (paginated)

<b>➤ Link Generation:</b>
• <code>/links</code> - Show all channel links (normal + request)
• <code>/reqlink</code> - Show request-to-join links with buttons
• <code>/bulklink {id1} {id2} {id3}</code> - Generate links for multiple channels

<b>➤ How It Works:</b>
1. Add a channel using <code>/addch -1001234567890</code>
2. Bot generates two types of links:
   • <b>Normal Link</b> - Direct join link
   • <b>Request Link</b> - Request-to-join link
3. Share these links in your posts/channels
4. Links auto-expire after 5 minutes for security
5. Users can regenerate fresh links anytime

<b>➤ Features:</b>
✅ Auto-revoke expired links
✅ Separate normal & request links
✅ Bulk link generation
✅ Paginated channel management
✅ Protected from copyright issues
✅ Works alongside file sharing bot

<b>➤ Example Usage:</b>
<code>/addch -1001234567890</code>
<code>/bulklink -1001234567890 -1009876543210</code>

<b>➤ Integration:</b>
• Link sharing works independently
• File sharing features remain unchanged
• Both systems work simultaneously
• No conflicts with existing commands

<b>Need help?</b> Contact @YourSupportGroup"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Show Channels", callback_data="link_show_channels")],
        [InlineKeyboardButton("🔗 Generate Links", callback_data="link_gen_links")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])
    
    await message.reply(help_text, reply_markup=buttons, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex("link_show_channels"))
async def show_channels_callback(client, callback_query):
    """Handle show channels callback"""
    await callback_query.answer()
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        await callback_query.answer(
            "No channels configured. Use /addch to add one.",
            show_alert=True
        )
        return
    
    text = "<b>📋 Configured Channels:</b>\n\n"
    for idx, channel_id in enumerate(channels, 1):
        try:
            chat = await client.get_chat(channel_id)
            text += f"{idx}. {chat.title} (<code>{channel_id}</code>)\n"
        except:
            text += f"{idx}. <code>{channel_id}</code> (Error)\n"
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data="link_help_back")
        ]]),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("link_gen_links"))
async def generate_links_callback(client, callback_query):
    """Handle generate links callback"""
    await callback_query.answer()
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        await callback_query.answer(
            "No channels configured. Use /addch to add one.",
            show_alert=True
        )
        return
    
    from helper.helper_func import encode
    
    text = "<b>🔗 Generated Links:</b>\n\n"
    for idx, channel_id in enumerate(channels[:3], 1):  # Show first 3
        try:
            chat = await client.get_chat(channel_id)
            base64_invite = await encode(f"lnk_{channel_id}")
            base64_request = await encode(f"req_{channel_id}")
            
            normal_link = f"https://t.me/{client.username}?start={base64_invite}"
            request_link = f"https://t.me/{client.username}?start={base64_request}"
            
            text += f"<b>{idx}. {chat.title}</b>\n"
            text += f"Normal: <code>{normal_link}</code>\n"
            text += f"Request: <code>{request_link}</code>\n\n"
        except:
            pass
    
    text += "<i>Use /links to see all links</i>"
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Back", callback_data="link_help_back")
        ]]),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("link_help_back"))
async def link_help_back(client, callback_query):
    """Go back to main help menu"""
    await callback_query.answer()
    await link_help_command(client, callback_query.message)
