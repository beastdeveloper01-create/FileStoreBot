#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from config import MSG_EFFECT


async def send_start_message(client: Client, message_or_query):
    """
    A single, robust function to send the start message.
    Handles both /start command (Message) and Home button (CallbackQuery)
    and correctly manages transitions between photo and text messages.
    """
    is_callback = isinstance(message_or_query, CallbackQuery)
    
    if is_callback:
        message = message_or_query.message
        user = message_or_query.from_user
        await message_or_query.answer()
    else:
        message = message_or_query
        user = message_or_query.from_user

    start_photo = client.messages.get('START_PHOTO', '')
    
    buttons = [[InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data="about"), InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]]
    if user.id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("⛩️ ꜱᴇᴛᴛɪɴɢꜱ ⛩️", callback_data="settings")])
    
    start_text = client.messages.get('START', 'No Start Message').format(
        first=user.first_name,
        last=user.last_name or "",
        username=f'@{user.username}' if user.username else 'None',
        mention=user.mention,
        id=user.id
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)

    if start_photo:
        if is_callback and message.photo:
            await message.edit_media(media=InputMediaPhoto(media=start_photo, caption=start_text), reply_markup=reply_markup)
        else:
            if is_callback: await message.delete()
            await client.send_photo(chat_id=message.chat.id, photo=start_photo, caption=start_text, reply_markup=reply_markup)
    else:
        if is_callback and not message.photo:
            await message.edit_text(text=start_text, reply_markup=reply_markup)
        else:
            if is_callback: await message.delete()
            await client.send_message(chat_id=message.chat.id, text=start_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex('^home$'))
async def home(client: Client, query: CallbackQuery):
    """Handles the 'Home' button by calling the master start message function."""
    await send_start_message(client, query)

@Client.on_callback_query(filters.regex('^about$'))
async def about(client: Client, query: CallbackQuery):
    await query.answer()
    
    buttons = [[InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="home"), InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]]
    
    about_text = client.messages.get('ABOUT', 'No About Message').format(
        owner_id=client.owner,
        bot_username=client.username,
        first=query.from_user.first_name,
        last=query.from_user.last_name or "",
        username=f'@{query.from_user.username}' if query.from_user.username else 'None',
        mention=query.from_user.mention,
        id=query.from_user.id
    )
    
    about_photo = client.messages.get('ABOUT_PHOTO', '')
    
    if about_photo:
        if query.message.photo:
            await query.message.edit_media(media=InputMediaPhoto(media=about_photo, caption=about_text), reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await query.message.delete()
            await client.send_photo(chat_id=query.message.chat.id, photo=about_photo, caption=about_text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        if query.message.photo:
            await query.message.delete()
            await client.send_message(query.message.chat.id, about_text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await query.message.edit_text(text=about_text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id_str in user_ids.split():
            user_id = int(user_id_str)
            c += 1
            if user_id in client.admins: continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, True)
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"__{c} users have been banned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id_str in user_ids.split():
            user_id = int(user_id_str)
            c += 1
            if user_id in client.admins: continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"__{c} users have been unbanned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

@Client.on_callback_query(filters.regex('^close$'))
async def close(client: Client, query: CallbackQuery):
    await query.message.delete()
    try:
        if query.message.reply_to_message:
            await query.message.reply_to_message.delete()
    except:
        pass
