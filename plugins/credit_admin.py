#  Developed by t.me/napaaextra

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import OWNER_ID

PAGE_SIZE = 10

async def send_credit_list_page(client: Client, message: Message, users_with_credits: list, page: int, edit: bool = False):
    """Sends a paginated list of users and their credits."""
    total_users = len(users_with_credits)
    total_pages = (total_users + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    text = "<b>📊 User Credit Balances</b>\n\n"
    
    page_users = users_with_credits[start_idx:end_idx]

    for idx, user_data in enumerate(page_users, start=start_idx + 1):
        user_id = user_data['_id']
        credits = user_data.get('credits', 0)
        
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
        except Exception:
            user_mention = f"User `{user_id}`"

        text += f"<b>{idx}.</b> {user_mention}\n   <code>{user_id}</code> - <b>{credits}</b> credits\n"

    text += f"\n📄 <b>Page {page + 1} of {total_pages}</b> | <b>Total Users:</b> {total_users}"

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"creditlist_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"creditlist_{page+1}"))
    
    buttons = [nav_buttons] if nav_buttons else []
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    reply_markup = InlineKeyboardMarkup(buttons)

    if edit:
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_message(filters.command('showcredit') & filters.private)
async def show_credit_command(client: Client, message: Message):
    """Shows a paginated list of users and their credits."""
    if message.from_user.id != OWNER_ID:
        return await message.reply("This command is for the owner only.")

    cursor = client.mongodb.user_data.find(
        {'credits': {'$exists': True, '$gt': 0}}
    ).sort('credits', -1)
    
    users_with_credits = await cursor.to_list(length=None)

    if not users_with_credits:
        return await message.reply_text("No users have any credits yet.")

    await send_credit_list_page(client, message, users_with_credits, page=0)

@Client.on_callback_query(filters.regex(r"^creditlist_(\d+)"))
async def paginate_credit_list(client: Client, query: CallbackQuery):
    """Handles pagination for the credit list."""
    if query.from_user.id != OWNER_ID:
        return await query.answer("This is not for you!", show_alert=True)
    
    page = int(query.data.split("_")[1])
    
    cursor = client.mongodb.user_data.find(
        {'credits': {'$exists': True, '$gt': 0}}
    ).sort('credits', -1)
    users_with_credits = await cursor.to_list(length=None)

    await send_credit_list_page(client, query.message, users_with_credits, page, edit=True)
