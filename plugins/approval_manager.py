#  Developed by t.me/napaaextra

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired, ChatAdminInviteRequired
from pyrogram.raw.functions.messages import GetChatInviteImporters

@Client.on_message(filters.command('approveall') & filters.private)
async def approve_all_command(client: Client, message: Message):
    """
    Approves all pending join requests for a given channel/group.
    Usage: /approveall <channel_id>
    OR: /approveall (if used as reply to a forwarded message from the channel)
    """
    if message.from_user.id not in client.admins:
        return await message.reply(
            "❌ **You are not authorized to use this command.**",
            parse_mode=ParseMode.MARKDOWN
        )

    chat_id = None
    
    try:
        if len(message.command) == 2:
            chat_id = int(message.command[1])
        elif message.reply_to_message and message.reply_to_message.forward_from_chat:
            chat_id = message.reply_to_message.forward_from_chat.id
        else:
            raise ValueError("Missing chat ID")
    except (ValueError, IndexError):
        return await message.reply(
            "<b>❌ Invalid command format.</b>\n\n"
            "<b>Usage:</b>\n"
            "• <code>/approveall -1001234567890</code>\n"
            "• Reply to a forwarded message from the channel with <code>/approveall</code>",
            parse_mode=ParseMode.HTML
        )

    try:
        chat = await client.get_chat(chat_id)
        bot_member = await client.get_chat_member(chat_id, "me")
        
        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply(
                f"<b>❌ I am not an admin in {chat.title}.</b>\n\n"
                "Please make me an admin first.",
                parse_mode=ParseMode.HTML
            )
        
        if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
            if not bot_member.privileges or not bot_member.privileges.can_invite_users:
                return await message.reply(
                    f"<b>❌ Missing Permission in {chat.title}</b>\n\n"
                    "I need the <b>'Invite Users via Link'</b> permission to approve join requests.",
                    parse_mode=ParseMode.HTML
                )
    except ChatAdminRequired:
        return await message.reply(
            "<b>❌ I don't have permission to access admin info in this chat.</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        return await message.reply(
            f"<b>❌ An error occurred:</b>\n<code>{e}</code>",
            parse_mode=ParseMode.HTML
        )

    status_msg = await message.reply(
        f"<b>🔍 Fetching pending requests for:</b>\n"
        f"<b>{chat.title}</b> (<code>{chat_id}</code>)\n\n"
        "⏳ Please wait...",
        parse_mode=ParseMode.HTML
    )
    
    pending_users = []
    offset_date = None
    offset_user = None
    fetch_errors = []

    try:
        client.LOGGER(__name__, client.name).info(f"Starting to fetch pending requests for {chat_id}")
        
        while True:
            try:
                importers = await client.invoke(
                    GetChatInviteImporters(
                        peer=await client.resolve_peer(chat_id),
                        requested=True,
                        offset_date=offset_date or 0,
                        offset_user=offset_user or await client.resolve_peer('me'),
                        limit=200
                    )
                )
                
                if not importers.importers:
                    break
                
                pending_users.extend(importers.importers)
                client.LOGGER(__name__, client.name).info(f"Fetched {len(importers.importers)} requests (Total: {len(pending_users)})")
                
                if len(importers.importers) < 200:
                    break
                    
                last_importer = importers.importers[-1]
                offset_date = last_importer.date
                offset_user = await client.resolve_peer(last_importer.user_id)
                
                await asyncio.sleep(1)
                
            except FloodWait as e:
                client.LOGGER(__name__, client.name).warning(f"FloodWait during fetch: {e.x}s")
                await status_msg.edit(
                    f"⏳ <b>Rate limited while fetching.</b>\n"
                    f"Pausing for {e.x} seconds...",
                    parse_mode=ParseMode.HTML
                )
                await asyncio.sleep(e.x)
            except Exception as e:
                fetch_errors.append(str(e))
                client.LOGGER(__name__, client.name).error(f"Error fetching pending users: {e}")
                break
                
    except Exception as e:
        return await status_msg.edit(
            f"<b>❌ Could not fetch pending members.</b>\n\n"
            f"<b>Error:</b> <code>{e}</code>",
            parse_mode=ParseMode.HTML
        )

    if not pending_users:
        return await status_msg.edit(
            f"<b>🎉 No Pending Requests!</b>\n\n"
            f"There are no pending join requests in <b>{chat.title}</b>.",
            parse_mode=ParseMode.HTML
        )

    await status_msg.edit(
        f"<b>✅ Found {len(pending_users)} pending request(s)!</b>\n\n"
        f"<b>Channel:</b> {chat.title}\n"
        f"<b>Starting approval process...</b>",
        parse_mode=ParseMode.HTML
    )
    
    approved_count = 0
    failed_count = 0
    failed_users = []
    
    for idx, user in enumerate(pending_users, 1):
        try:
            await client.approve_chat_join_request(chat_id, user.user_id)
            approved_count += 1
            
        except FloodWait as e:
            client.LOGGER(__name__, client.name).warning(f"FloodWait during approval: {e.x}s")
            await status_msg.edit(
                f"⏳ <b>Rate Limited!</b>\n\n"
                f"Pausing for {e.x} seconds...\n"
                f"Progress: {idx}/{len(pending_users)}",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(e.x)
            
            try:
                await client.approve_chat_join_request(chat_id, user.user_id)
                approved_count += 1
            except Exception as retry_error:
                failed_count += 1
                failed_users.append((user.user_id, str(retry_error)))
                
        except Exception as e:
            failed_count += 1
            failed_users.append((user.user_id, str(e)))
            client.LOGGER(__name__, client.name).error(f"Failed to approve {user.user_id}: {e}")

        if idx % 25 == 0:
            await status_msg.edit(
                f"⚙️ <b>Processing...</b>\n\n"
                f"✅ Approved: <b>{approved_count}</b>\n"
                f"❌ Failed: <b>{failed_count}</b>\n"
                f"📊 Progress: <b>{idx}/{len(pending_users)}</b>",
                parse_mode=ParseMode.HTML
            )
        
        await asyncio.sleep(1.5)

    report_text = (
        f"<b>✅ Approval Process Complete!</b>\n\n"
        f"<b>📊 Final Report:</b>\n"
        f"• Channel: <b>{chat.title}</b>\n"
        f"• Total Requests: <b>{len(pending_users)}</b>\n"
        f"• Successfully Approved: <b>{approved_count}</b> ✅\n"
        f"• Failed to Approve: <b>{failed_count}</b> ❌"
    )
    
    if failed_users and len(failed_users) <= 10:
        report_text += "\n\n<b>Failed Users:</b>\n"
        for user_id, error in failed_users[:10]:
            report_text += f"• <code>{user_id}</code> - {error[:50]}\n"
    elif len(failed_users) > 10:
        report_text += f"\n\n<b>⚠️ {len(failed_users)} users failed to approve.</b>"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Done", callback_data="close")]
    ])
    
    await status_msg.edit(report_text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    client.LOGGER(__name__, client.name).info(
        f"Approval complete: {approved_count} approved, {failed_count} failed for {chat_id}"
    )
