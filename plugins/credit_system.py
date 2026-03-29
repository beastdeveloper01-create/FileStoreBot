#  Developed by t.me/napaaextra

import uuid
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from helper.helper_func import encode
from plugins.shortner import get_short

async def handle_earn_credit_link(client: Client, message: Message):
    """Handles the logic when a user successfully completes a credit-earning link."""
    user_id = message.from_user.id
    credits_to_add = getattr(client, 'credits_per_visit', 1)
    await client.mongodb.update_credits(user_id, credits_to_add)
    new_balance = await client.mongodb.get_credits(user_id)
    await message.reply(
        f"<b>✅ You have successfully earned {credits_to_add} credit(s)!</b>\n\n"
        f"Your new balance is: <b>{new_balance}</b> credits.",
        parse_mode=ParseMode.HTML
    )

async def handle_credit_system(client: Client, message: Message, base64_string: str) -> bool:
    """
    Handles the entire credit check logic.
    Returns True if the user can proceed, False otherwise.
    """
    user_id = message.from_user.id
    is_admin = user_id in client.admins
    is_premium = await client.mongodb.is_pro(user_id)

    if is_admin or is_premium or not client.credit_system_enabled:
        return True

    current_credits = await client.mongodb.get_credits(user_id)
    cost = client.credits_per_file

    if current_credits >= cost:
        await client.mongodb.update_credits(user_id, -cost)
        await message.reply(f"💸 Used {cost} credit(s). Your new balance is {current_credits - cost}.")
        return True
    else:
        redirect_param = f"creditget_{base64_string}"
        direct_link_after_shortener = f"https://t.me/{client.username}?start={redirect_param}"
        shortened_url = get_short(direct_link_after_shortener, client)

        caption = (
            f"<b><blockquote>›› ʜᴇʏ {message.from_user.mention} ››</blockquote></b>\n\n"
            f"<b>⚠️ Iɴsᴜғғɪᴄɪᴇɴᴛ Cʀᴇᴅɪᴛs!</b>\n\n"
            f"Yᴏᴜ ɴᴇᴇᴅ <b>{cost}</b> ᴄʀᴇᴅɪᴛs ᴛᴏ ᴀᴄᴄᴇss ᴛʜɪs ғɪʟᴇ, ʙᴜᴛ ʏᴏᴜ ᴏɴʟʏ ʜᴀᴠᴇ <b>{current_credits}</b>.\n\n"
            f"Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ Sʜᴏʀᴛʟɪɴᴋ ᴛᴏ ᴇᴀʀɴ <b>{client.credits_per_visit}</b> ᴄʀᴇᴅɪᴛ ᴀɴᴅ ᴜɴʟᴏᴄᴋ ʏᴏᴜʀ ғɪʟᴇ ɪɴsᴛᴀɴᴛʟʏ!"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴇᴀʀɴ ᴄʀᴇᴅɪᴛs & ɢᴇᴛ ғɪʟᴇ", url=shortened_url)],
            [InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ", url=client.tutorial_link), InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]
        ])
        
        photo_url = client.messages.get("SHORTNER_PHOTO")
        if photo_url:
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_text(
                caption,
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
        return False

@Client.on_message(filters.command('credit') & filters.private)
async def credit_balance_command(client: Client, message: Message):
    """Shows the user their current credit balance."""
    if not await client.mongodb.present_user(message.from_user.id):
        await client.mongodb.add_user(message.from_user.id)
    
    balance = await client.mongodb.get_credits(message.from_user.id)
    
    await message.reply_text(
        f"<b><blockquote>✰ Yᴏᴜʀ Cʀᴇᴅɪᴛ ʙᴀʟᴀɴᴄᴇ</blockquote></b>\n\n"
        f"<b>›› Yᴏᴜ ᴄᴜʀʀᴇɴᴛʟʏ ʜᴀᴠᴇ: <code>{balance}</code> ᴄʀᴇᴅɪᴛs.</b>\n\n"
        f"<b>›› Usᴇ <code>/getcredit</code> ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ ᴄʀᴇᴅɪᴛs.</b>",
        parse_mode=ParseMode.HTML
    )

@Client.on_message(filters.command('getcredit') & filters.private)
async def get_credit_command(client: Client, message: Message):
    """Provides a shortener link for the user to earn credits."""
    if not client.credit_system_enabled:
        return await message.reply_text("The credit system is currently disabled.")
        
    if not client.shortner_enabled or not client.short_url or not client.short_api:
        return await message.reply_text("The credit earning system is not configured by the admin yet.")

    max_limit = getattr(client, 'max_credit_limit', 0)
    current_balance = await client.mongodb.get_credits(message.from_user.id)
    if max_limit > 0 and current_balance >= max_limit:
        return await message.reply_text(
            f"<b>⚠️ Lɪᴍɪᴛ Rᴇᴀᴄʜᴇᴅ!</b>\n\n"
            f"𝚈𝚘𝚞 𝚑𝚊𝚟𝚎 𝚛𝚎𝚊𝚌𝚑𝚎𝚍 𝚝𝚑𝚎 𝚖𝚊𝚡𝚒𝚖𝚞𝚖 𝚌𝚛𝚎𝚍𝚒𝚝 𝚕𝚒𝚖𝚒𝚝 𝚘𝚏 **{max_limit}** 𝚌𝚛𝚎𝚍𝚒𝚝𝚜 𝚊𝚗𝚍 𝚌𝚊𝚗𝚗𝚘𝚝 𝚎𝚊𝚛𝚗 𝚖𝚘𝚛𝚎 𝚊𝚝 𝚝𝚑𝚒𝚜 𝚝𝚒𝚖𝚎."
        )

    payload = f"earn_credit_{uuid.uuid4().hex[:10]}"
    encoded_payload = await encode(payload)
    
    direct_link_after_shortener = f"https://t.me/{client.username}?start={encoded_payload}"
    
    shortened_url = get_short(direct_link_after_shortener, client)
    
    credits_to_earn = getattr(client, 'credits_per_visit', 1)

    caption_text = (
        f"<b><blockquote>✧ Eᴀʀɴ {credits_to_earn} Cʀᴇᴅɪᴛs!</blockquote></b>\n\n"
        "<b>Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴀɴᴅ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ Sʜᴏʀᴛʟɪɴᴋ ɪɴ ᴏʀᴅᴇʀ ᴛᴏ ᴇᴀʀɴ Cʀᴇᴅɪᴛs.</b>\n\n"
        "<b>Aғᴛᴇʀ ᴛʜᴀᴛ ʏᴏᴜʀ ᴇᴀʀɴᴇᴅ Cʀᴇᴅɪᴛs ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ Bᴀʟᴀɴᴄᴇ.</b>"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴇᴀʀɴ {credits_to_earn} ᴄʀᴇᴅɪᴛs", url=shortened_url)],
        [InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ", url=client.tutorial_link), InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data="close")]
    ])
    
    photo_url = client.messages.get("SHORTNER_PHOTO")
    
    if photo_url:
        await message.reply_photo(
            photo=photo_url,
            caption=caption_text,
            reply_markup=buttons,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text(
            caption_text,
            reply_markup=buttons,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

@Client.on_callback_query(filters.regex("^check_balance$"))
async def check_balance_callback(client: Client, query: CallbackQuery):
    """Handles the 'Check Balance' button callback."""
    if not await client.mongodb.present_user(query.from_user.id):
        await client.mongodb.add_user(query.from_user.id)
        
    balance = await client.mongodb.get_credits(query.from_user.id)
    await query.answer(f"You currently have {balance} credit(s).", show_alert=True)
