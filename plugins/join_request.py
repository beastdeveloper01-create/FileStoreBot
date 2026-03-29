#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import asyncio

@Client.on_chat_join_request(filters.channel | filters.group)
async def handle_join_request(client, join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id
    
    await client.mongodb.add_channel_user(chat_id, user_id)
    
    is_global_enabled = getattr(client, 'auto_approval_enabled', False)
    is_channel_enabled = await client.mongodb.is_auto_approval_enabled(chat_id)

    if not (is_global_enabled and is_channel_enabled):
        return
        
    delay = getattr(client, 'approval_delay', 5)
    client.LOGGER(__name__, client.name).info(f"Unconditionally auto-approving {user_id} for {chat_id} after {delay} seconds.")
    
    await asyncio.sleep(delay)
    
    try:
        await client.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        
        photo = client.messages.get('APPROVAL_PHOTO')
        text_template = client.messages.get('APPROVAL_WELCOME_TEXT')
        buttons_config = client.messages.get('APPROVAL_BUTTONS', [])

        if text_template:
            try:
                text = text_template.format(
                    mention=join_request.from_user.mention,
                    chat_title=join_request.chat.title
                )
                
                buttons = []
                if buttons_config:
                    chat_id_numeric = str(chat_id).replace("-100", "")
                    for row_config in buttons_config:
                        button_row = []
                        for btn_config in row_config:
                            btn_text = btn_config["text"].format(chat_title=join_request.chat.title)
                            btn_url = btn_config["url"].format(chat_id=chat_id_numeric)
                            button_row.append(InlineKeyboardButton(text=btn_text, url=btn_url))
                        buttons.append(button_row)
                
                reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

                if photo:
                    await client.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await client.send_message(
                        chat_id=user_id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to send welcome message to {user_id}: {e}")

    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Could not approve join request for {user_id} in {chat_id}: {e}")
