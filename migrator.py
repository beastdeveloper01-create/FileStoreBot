#  Developed by t.me/napaaextra
#  Developed by t.me/napaaextra
from pyrogram import Client, filters, idle
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import LOGGER
import os


TOKEN = "8785842653:AAH-ksMbomVfdIdM4PB8vXXTfSWhE-uFYqY"
API_ID = int(os.getenv("API_ID", 33461228))
API_HASH = os.getenv("API_HASH", "52850b8b740b1f87bb55329cce4d65a0")

BOT_FLEET = {
    "〶 Bot 1": "File_S_Demobot",
    "〶 Bot 2": "KomiAMBot",
    "〶 Bot 3": "HinataAMbot",
}

ACTIVE_BOT_KEY = "〶 Bot 1" 
ADMIN_IDS = [8704133698]
REDIRECT_PHOTO = "https://graph.org/file/720725f0cb4e2975cd4f8-4fee1fc19b395c1dce.jpg"


CURRENT_MODE = "single"

os.makedirs("sessions", exist_ok=True)
app = Client("sessions/migrator", API_ID, API_HASH, bot_token=TOKEN, workers=4, sleep_threshold=60)
logger = LOGGER(__name__, "migrator")

def get_active_bot_username():
    return BOT_FLEET.get(ACTIVE_BOT_KEY, next(iter(BOT_FLEET.values())))


def generate_mode_panel(current_mode: str):
    """Creates the text and buttons for the dynamic mode settings panel."""
    
    single_status = "✓ 𝙴𝚗𝚊𝚋𝚕𝚎𝚍" if current_mode == "single" else "✗ 𝙳𝚒𝚜𝚊𝚋𝚕𝚎𝚍"
    multiple_status = "✓ 𝙴𝚗𝚊𝚋𝚕𝚎𝚍" if current_mode == "multiple" else "✗ 𝙳𝚒𝚜𝚊𝚋𝚕𝚎𝚍"
    
    text = f"""<b><blockquote>✧ ᴍɪɢʀᴀᴛᴏʀ ᴍᴏᴅᴇ ꜱᴇᴛᴛɪɴɢꜱ</blockquote></b>

<b>›› ꜱɪɴɢʟᴇ ʙᴏᴛ ᴍᴏᴅᴇ - </b> {single_status}

<b>›› ᴍᴜʟᴛɪᴘʟᴇ ʙᴏᴛ ᴍᴏᴅᴇ - </b> {multiple_status}
"""
    
    single_button_text = "✔️ ꜱɪɴɢʟᴇ ʙᴏᴛ" if current_mode == "single" else "ꜱɪɴɢʟᴇ ʙᴏᴛ"
    multiple_button_text = "✔️ ᴍᴜʟᴛɪᴘʟᴇ ʙᴏᴛ" if current_mode == "multiple" else "ᴍᴜʟᴛɪᴘʟᴇ ʙᴏᴛ"

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(single_button_text, callback_data="set_mode_single"),
            InlineKeyboardButton(multiple_button_text, callback_data="set_mode_multiple")
        ],
        [InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close_mode_panel")]
    ])
    
    return text, reply_markup


@app.on_message(filters.command('mode') & filters.private)
async def mode_command_handler(client: Client, message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("❌ <b>Admin Only!</b>", parse_mode=ParseMode.HTML)
    
    text, markup = generate_mode_panel(CURRENT_MODE)
    await message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)

@app.on_callback_query(filters.regex("^set_mode_(single|multiple)$"))
async def set_mode_callback(client: Client, query: CallbackQuery):
    global CURRENT_MODE
    
    if query.from_user.id not in ADMIN_IDS:
        return await query.answer("Admin only!", show_alert=True)
        
    new_mode = query.data.split("_")[-1]
    
    if new_mode == CURRENT_MODE:
        return await query.answer(f"{new_mode.title()} mode is already active.", show_alert=True)
        
    CURRENT_MODE = new_mode
    logger.info(f"Mode switched to '{CURRENT_MODE}' by admin {query.from_user.id}")
    
    text, markup = generate_mode_panel(CURRENT_MODE)
    await query.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await query.answer(f"✓ 𝚂𝚠𝚒𝚝𝚌𝚑𝚎𝚍 𝚝𝚘 {new_mode.title()} 𝙱𝚘𝚝 𝙼𝚘𝚍𝚎")

@app.on_callback_query(filters.regex("^close_mode_panel$"))
async def close_mode_panel_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in ADMIN_IDS:
        return await query.answer("Admin only!", show_alert=True)
    await query.message.delete()


@app.on_message(filters.command('start') & filters.private)
async def redirect_handler(client: Client, message: Message):
    text = message.text
    user = message.from_user
    
    if len(text) > 7:
        param = text.split(" ", 1)[1]
        buttons = []
        
        if CURRENT_MODE == "single":
            active_username = get_active_bot_username()
            active_link = f"https://t.me/{active_username}?start={param}"
            buttons.append([InlineKeyboardButton("• ᴄʟɪᴄᴋ ʜᴇʀᴇ ꜰᴏʀ ꜰɪʟᴇꜱ •", url=active_link)])
        else:
            button_list = [InlineKeyboardButton(key, url=f"https://t.me/{username}?start={param}") for key, username in BOT_FLEET.items()]
            buttons = [button_list[i:i + 2] for i in range(0, len(button_list), 2)]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        
        caption = (
            f"<blockquote><b>›› ʜɪ ᴛʜᴇʀᴇ... {user.mention} ››</b></blockquote>\n\n"
            f"<b>ʏᴏᴜʀ ꜰɪʟᴇꜱ ᴀʀᴇ ʀᴇᴀᴅʏ!</b>\n"
            f"<b>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇᴍ.</b>\n\n"
            f"<b>ꜰᴀᴄɪɴɢ ᴀɴʏ ɪꜱꜱᴜᴇ?</b>\n"
            f"<b>ᴄᴏɴᴛᴀᴄᴛ ᴜꜱ ᴏɴ @WeebsCloud</b>"
        )
        
        if CURRENT_MODE == "single":
            active_username = get_active_bot_username()
            caption += f"\n\n<b><blockquote>✲ ɴᴏᴡ ᴡᴏʀᴋɪɴɢ ꜰᴏʀ: @{active_username}</blockquote></b>"
            
        await message.reply_photo(photo=REDIRECT_PHOTO, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        active_username = get_active_bot_username()
        await message.reply_photo(
            photo=REDIRECT_PHOTO,
            caption=(
                f"<blockquote><b>›› ʜɪ ᴛʜᴇʀᴇ... {user.mention} ››</b></blockquote>\n\n"
                f"<b>ɪ ᴀᴍ ᴀ ꜱᴍᴀʀᴛ ʟɪɴᴋ ʀᴇᴅɪʀᴇᴄᴛᴏʀ.</b>\n"
                f"<b>ɪ ᴇɴꜱᴜʀᴇ ʏᴏᴜʀ ꜰɪʟᴇ ʟɪɴᴋꜱ ᴀʟᴡᴀʏꜱ ᴡᴏʀᴋ!</b>\n\n"
                f"<b><blockquote>✲ ɴᴏᴡ ᴡᴏʀᴋɪɴɢ ꜰᴏʀ: @{active_username}</blockquote></b>"
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/Naapaextraa"), InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close_mode_panel")]]),
            parse_mode=ParseMode.HTML
        )


@app.on_message(filters.command('status') & filters.private)
async def status_handler(client: Client, message: Message):
    mode_text = "Single Bot (Active)" if CURRENT_MODE == "single" else "Multiple Bots (Fleet)"
    status_text = f"<b>⚙️ Current Mode:</b> {mode_text}\n\n<b>🤖 Bot Fleet Status:</b>\n\n"
    for key, username in BOT_FLEET.items():
        if key == ACTIVE_BOT_KEY and CURRENT_MODE == "single":
            status_text += f"✅ <b>{username}</b> - ACTIVE\n"
        else:
            status_text += f"▶️ <code>{username}</code> - Online\n"
    status_text += f"\n<b>🎯 Active Bot for Single Mode:</b> @{get_active_bot_username()}"
    await message.reply(status_text, parse_mode=ParseMode.HTML)

@app.on_message(filters.command('switch') & filters.private)
async def switch_handler(client: Client, message: Message):
    global ACTIVE_BOT_KEY
    if message.from_user.id not in ADMIN_IDS: return await message.reply("❌ <b>Admin Only!</b>", parse_mode=ParseMode.HTML)
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot_list = "\n".join([f"• `{k}`" for k in BOT_FLEET.keys()])
        await message.reply(f"<b>🔄 Switch Active Bot</b>\n\n<b>Current:</b> {ACTIVE_BOT_KEY}\n\n<b>Available:</b>\n{bot_list}\n\n<b>Usage:</b> <code>/switch \"🤖 Bot 1\"</code>", parse_mode=ParseMode.HTML)
        return
    new_key = parts[1]
    if new_key not in BOT_FLEET: return await message.reply(f"❌ Invalid key! Use one of: `{', '.join(BOT_FLEET.keys())}`", parse_mode=ParseMode.HTML)
    old_username, ACTIVE_BOT_KEY = get_active_bot_username(), new_key
    new_username = get_active_bot_username()
    logger.info(f"Switched active bot: {old_username} -> {new_username}")
    await message.reply(f"<b>✅ Active Bot Switched!</b>\n\n<b>From:</b> @{old_username}\n<b>To:</b> @{new_username}\n\nIn Single Bot Mode, links will redirect to @{new_username}.", parse_mode=ParseMode.HTML)

@app.on_message(filters.command('help') & filters.private)
async def help_handler(client: Client, message: Message):
    help_text = "<b>📖 Help</b>\n\n• /start\n• /status\n• /help\n\n"
    if message.from_user.id in ADMIN_IDS:
        help_text += "<b>Admin:</b>\n• /mode - Open interactive mode settings.\n• /switch [key] - Set the active bot for single mode."
    await message.reply(help_text, parse_mode=ParseMode.HTML)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🔄 Starting Migrator Bot...")
    logger.info("=" * 60)
    try: app.run()
    except Exception as e: logger.error(f"Fatal error: {e}")
