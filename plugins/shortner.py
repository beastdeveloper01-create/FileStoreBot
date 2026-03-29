#  Developed by t.me/napaaextra
import requests
import random
import string
from config import SHORT_URL, SHORT_API, MESSAGES
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import force_sub
from pyrogram.enums import ParseMode

shortened_urls_cache = {}

def generate_random_alphanumeric():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

def get_short(url, client):
    if not client.shortner_enabled or not client.short_url or not client.short_api or client.short_url.lower() in ["", "none"]:
        return url
    if url in shortened_urls_cache:
        return shortened_urls_cache[url]
    try:
        alias = generate_random_alphanumeric()
        api_url = f"https://{client.short_url}/api?api={client.short_api}&url={url}&alias={alias}"
        response = requests.get(api_url, timeout=5)
        rjson = response.json()
        if rjson.get("status") == "success" and response.status_code == 200:
            short_url = rjson.get("shortenedUrl", url)
            shortened_urls_cache[url] = short_url
            return short_url
    except Exception as e:
        print(f"[Shortener Error] {e}")
    return url

@Client.on_message(filters.command('shortner') & filters.private)
async def shortner_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    await shortner_panel(client, message)

async def shortner_panel(client, query_or_message):
    status = "✗ ᴅɪsᴀʙʟᴇᴅ"
    if client.shortner_enabled and client.short_api:
        try:
            test_response = requests.get(f"https://{client.short_url}/api?api={client.short_api}&url=https://google.com&alias=test", timeout=5)
            status = "✓ ᴡᴏʀᴋɪɴɢ" if test_response.status_code == 200 else "✗ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ"
        except: status = "✗ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ"
    elif not client.shortner_enabled: status = "✗ ᴅɪsᴀʙʟᴇᴅ"
    else: status = "✗ ɴᴏ ᴀᴘɪ sᴇᴛ"
    
    enabled_text = "✓ ᴇɴᴀʙʟᴇᴅ" if client.shortner_enabled else "✗ ᴅɪsᴀʙʟᴇᴅ"
    toggle_text = "✗ ᴏғғ" if client.shortner_enabled else "✓ ᴏɴ"
    api_display = f"`{client.short_api[:20]}...`" if client.short_api and len(client.short_api) > 20 else (f"`{client.short_api}`" if client.short_api else "`Not Set`")
    
    msg = f"""<blockquote>✦ 𝗦𝗛𝗢𝗥𝗧𝗡𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦</blockquote>
**<u>ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢꜱ:</u>**
<blockquote>›› **ꜱʜᴏʀᴛɴᴇʀ ꜱᴛᴀᴛᴜꜱ:** {enabled_text}
›› **ꜱʜᴏʀᴛɴᴇʀ ᴜʀʟ:** `{client.short_url}`
›› **ꜱʜᴏʀᴛɴᴇʀ ᴀᴘɪ:** {api_display}
›› **ᴘʀᴇᴍɪᴜᴍ ᴄᴏɴᴛᴀᴄᴛ:** `{client.messages.get("PREMIUM_CONTACT")}`</blockquote> 
<blockquote>›› **ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ:** `{client.tutorial_link}`
›› **ᴀᴘɪ ꜱᴛᴀᴛᴜꜱ:** {status}</blockquote>
<blockquote>**≡ ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴꜰɪɢᴜʀᴇ!**</blockquote>"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'• {toggle_text} ꜱʜᴏʀᴛɴᴇʀ •', 'toggle_shortner'), InlineKeyboardButton('• ᴀᴅᴅ ꜱʜᴏʀᴛɴᴇʀ •', 'add_shortner')],
        [InlineKeyboardButton('• ꜱᴇᴛ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ •', 'set_tutorial_link'), InlineKeyboardButton('• ꜱᴇᴛ ᴘʀᴇᴍɪᴜᴍ ᴄᴏɴᴛᴀᴄᴛ •', 'set_premium_contact')],
        [InlineKeyboardButton('• ᴛᴇꜱᴛ ꜱʜᴏʀᴛɴᴇʀ •', 'test_shortner')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ ᴛᴏ ꜱᴇᴛᴛɪɴɢꜱ', 'settings_pg2')]
    ])
    
    image_url = MESSAGES.get("SHORT", "https://graph.org/file/a7ef527466c5603e35200-902c9a04f46b1e06ca.jpg")
    is_callback = hasattr(query_or_message, 'message')
    message = query_or_message.message if is_callback else query_or_message

    if is_callback and message.photo:
        await message.edit_media(media=InputMediaPhoto(media=image_url, caption=msg), reply_markup=reply_markup)
    else:
        if is_callback: await message.delete()
        await client.send_photo(chat_id=message.chat.id, photo=image_url, caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^shortner$"))
async def shortner_callback(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    await query.answer()
    await shortner_panel(client, query)

@Client.on_callback_query(filters.regex("^set_premium_contact$"))
async def set_premium_contact(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    await query.message.delete()
        
    prompt = await client.send_message(query.from_user.id, "<blockquote>Please send the new premium contact link.</blockquote>", parse_mode=ParseMode.HTML)
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        new_link = res.text.strip()
        if new_link.startswith("https://t.me/"):
            client.messages['PREMIUM_CONTACT'] = new_link
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await res.reply(f"✅ Premium contact link updated!")
        else:
            await res.reply("❌ Invalid format. Please send a valid Telegram link.")
    except ListenerTimeout:
        await prompt.edit("<b>⏰ Timeout! No changes were made.</b>")
    
    dummy_message = await client.send_message(query.from_user.id, "Loading...")
    await shortner_panel(client, dummy_message)
    await dummy_message.delete()

@Client.on_callback_query(filters.regex("^toggle_shortner$"))
async def toggle_shortner(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    client.shortner_enabled = not client.shortner_enabled
    await client.mongodb.save_bot_setting('shortner_enabled', client.shortner_enabled)
    await query.answer(f"✓ ꜱʜᴏʀᴛɴᴇʀ {'ᴇɴᴀʙʟᴇᴅ' if client.shortner_enabled else 'ᴅɪsᴀʙʟᴇᴅ'}!")
    await shortner_panel(client, query)

@Client.on_callback_query(filters.regex("^add_shortner$"))
async def add_shortner(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    await query.message.delete()
        
    prompt = await client.send_message(query.from_user.id, "<blockquote>**Format:** `url api`</blockquote>", parse_mode=ParseMode.HTML)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        parts = res.text.strip().split()
        if len(parts) >= 2:
            client.short_url = parts[0].replace('https://', '').replace('http://', '').strip('/')
            client.short_api = ' '.join(parts[1:])
            await client.mongodb.save_bot_setting('short_url', client.short_url)
            await client.mongodb.save_bot_setting('short_api', client.short_api)
            await res.reply(f"**✓ ꜱʜᴏʀᴛɴᴇʀ ꜱᴇᴛᴛɪɴɢꜱ ᴜᴘᴅᴀᴛᴇᴅ!**")
        else:
            await res.reply("**✗ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!**")
    except ListenerTimeout:
        await prompt.edit("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**")

    dummy_message = await client.send_message(query.from_user.id, "Loading...")
    await shortner_panel(client, dummy_message)
    await dummy_message.delete()

@Client.on_callback_query(filters.regex("^set_tutorial_link$"))
async def set_tutorial_link(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    await query.message.delete()
        
    prompt = await client.send_message(query.from_user.id, "<blockquote>Please send the new tutorial link.</blockquote>", parse_mode=ParseMode.HTML)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_tutorial = res.text.strip()
        if new_tutorial.startswith(('https://', 'http://')):
            client.tutorial_link = new_tutorial
            await client.mongodb.save_bot_setting('tutorial_link', new_tutorial)
            await res.reply(f"**✓ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ ᴜᴘᴅᴀᴛᴇᴅ!**")
        else:
            await res.reply("**✗ ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ!**")
    except ListenerTimeout:
        await prompt.edit("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**")

    dummy_message = await client.send_message(query.from_user.id, "Loading...")
    await shortner_panel(client, dummy_message)
    await dummy_message.delete()

@Client.on_callback_query(filters.regex("^test_shortner$"))
async def test_shortner(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    await query.message.edit_caption("**🔄 ᴛᴇꜱᴛɪɴɢ ꜱʜᴏʀᴛɴᴇʀ...**")
    
    if not client.short_api:
        return await query.message.edit_caption("**❌ ɴᴏ ᴀᴘɪ ᴋᴇʏ ꜱᴇᴛ!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'shortner')]]))
    
    try:
        api_url = f"https://{client.short_url}/api?api={client.short_api}&url=https://google.com&alias={generate_random_alphanumeric()}"
        response = requests.get(api_url, timeout=10)
        rjson = response.json()
        
        if rjson.get("status") == "success" and response.status_code == 200:
            msg = f"""**✅ ꜱʜᴏʀᴛɴᴇʀ ᴛᴇꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!**\n\n**ꜱʜᴏʀᴛ ᴜʀʟ:** `{rjson.get("shortenedUrl", "")}`"""
        else:
            msg = f"""**❌ ꜱʜᴏʀᴛɴᴇʀ ᴛᴇꜱᴛ ꜰᴀɪʟᴇᴅ!**\n\n**ᴇʀʀᴏʀ:** `{rjson.get('message', 'Unknown error')}`"""
    except Exception as e:
        msg = f"**❌ ꜱʜᴏʀᴛɴᴇʀ ᴛᴇꜱᴛ ꜰᴀɪʟᴇᴅ!**\n\n**ᴇʀʀᴏʀ:** `{str(e)}`"
    
    await query.message.edit_caption(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'shortner')]]))

