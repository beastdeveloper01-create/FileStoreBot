#  Developed by t.me/napaaextra
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import OWNER_ID
import time
import os
import sys
import psutil
import shutil

async def admins(client, query):
    if not (query.from_user.id==client.owner):
        return await query.answer('This can only be used by owner.')
    msg = f"""<blockquote>**Admin Settings:**</blockquote>
**Admin User IDs:** {", ".join(f"`{a}`" for a in client.admins)}

__Use the appropriate button below to add or remove an admin based on your needs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings_pg1')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_message(filters.command("usage"))
async def usage_cmd(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    reply = await message.reply("`Extracting all Usage!!`")

    total, used, free = shutil.disk_usage("/")
    total_gb, used_gb, free_gb = total / (1024**3), used / (1024**3), free / (1024**3)

    ram = psutil.virtual_memory()
    total_ram, used_ram, free_ram = ram.total / (1024**3), ram.used / (1024**3), ram.available / (1024**3)

    swap = psutil.swap_memory()
    total_swap, used_swap, free_swap = swap.total / (1024**3), swap.used / (1024**3), swap.free / (1024**3)

    try:
        net_io = psutil.net_io_counters()
        bytes_sent, bytes_recv = net_io.bytes_sent / (1024**2), net_io.bytes_recv / (1024**2)
        net_msg = f"**📡 Network:** `↑ {bytes_sent:.2f} MB` | `↓ {bytes_recv:.2f} MB`\n"
    except (PermissionError, AttributeError):
        net_msg = ""

    process = psutil.Process()
    bot_cpu, bot_mem = process.cpu_percent(interval=1), process.memory_info().rss / (1024**2)

    msg = (
        f"<blockquote>**📊 System Usage Stats:**</blockquote>\n"
        f"**💾 Disk:** `{used_gb:.2f} GB / {total_gb:.2f} GB`\n"
        f"**🖥 RAM:** `{used_ram:.2f} GB / {total_ram:.2f} GB` ({ram.percent}%)\n"
        f"**🔄 Swap:** `{used_swap:.2f} GB / {total_swap:.2f} GB` ({swap.percent}%)\n"
        f"**⚡ CPU:** `{psutil.cpu_percent(interval=1):.2f}%`\n"
        f"{net_msg}"
        f"**🤖 Bot:** `CPU {bot_cpu:.2f}%` | `MEM {bot_mem:.2f} MB`"
    )

    await reply.edit_text(msg)
    
@Client.on_message(filters.command("reset") & filters.user(OWNER_ID))
async def reset_bot_settings(client: Client, message: Message):
    """
    Deletes cosmetic and basic configuration settings from the database,
    forcing a reload from setup.json while preserving important data.
    """
    await message.reply_text(
        "⚠️ **Cᴏɴꜰɪʀᴍ Cᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ Rᴇꜱᴇᴛ**\n\n"
        "ᴛʜɪꜱ ᴡɪʟʟ ʀᴇꜱᴇᴛ ꜱᴇᴛᴛɪɴɢꜱ ʟɪᴋᴇ **𝚖𝚎𝚜𝚜𝚊𝚐𝚎𝚜, 𝚙𝚑𝚘𝚝𝚘𝚜, 𝚊𝚍𝚖𝚒𝚗𝚜, 𝚊𝚗𝚍 𝙵𝚂𝚞𝚋 𝚌𝚑𝚊𝚗𝚗𝚎𝚕𝚜** ᴛᴏ ᴛʜᴇɪʀ ᴏʀɪɢɪɴᴀʟ ᴠᴀʟᴜᴇꜱ ꜰʀᴏᴍ `setup.json`.\n\n"
        "✅ **Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Dᴀᴛᴀ ᴡɪʟʟ ʙᴇ Pʀᴇꜱᴇʀᴠᴇᴅ:**\n"
        "• 𝚃𝚘𝚝𝚊𝚕 𝚄𝚜𝚎𝚛𝚜 & 𝙿𝚛𝚎𝚖𝚒𝚞𝚖 𝚄𝚜𝚎𝚛𝚜\n"
        "• 𝙰𝚕𝚕 𝙶𝚎𝚗𝚎𝚛𝚊𝚝𝚎𝚍 𝙻𝚒𝚗𝚔𝚜\n"
        "• 𝚂𝚑𝚘𝚛𝚝𝚎𝚗𝚎𝚛 𝙰𝙿𝙸 𝙺𝚎𝚢\n"
        "• **𝙰𝚞𝚝𝚘-𝙰𝚙𝚙𝚛𝚘𝚟𝚊𝚕 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 𝙻𝚒𝚜𝚝**\n\n"
        "ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ʀᴇꜱᴛᴀʀᴛ ᴛᴏ ᴀᴘᴘʟʏ ᴛʜᴇ ᴄʜᴀɴɢᴇꜱ.",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("✅ Yᴇꜱ", callback_data="confirm_safe_reset"),
                InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data="cancel_reset")
            ]]
        )
    )

@Client.on_callback_query(filters.regex("^confirm_safe_reset$"))
async def confirm_safe_reset_cb(client: Client, query: CallbackQuery):
    if query.from_user.id != client.owner:
        return await query.answer("This is not for you!", show_alert=True)
    
    await query.message.edit_text("🔥 **Resetting Configuration...**\n\nDeleting `bot_settings` collection. The bot will restart shortly.")
    
    try:
        await client.mongodb.db["bot_settings"].drop()
        client.LOGGER(__name__, client.name).info("`bot_settings` collection dropped by owner for config reset.")
            
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Failed to drop bot_settings during reset: {e}")
        return await query.message.edit_text(f"❌ **Error:** Could not delete settings from the database.\n\n`{e}`")
        
    await query.message.edit_text("✅ **Cᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ ꜱᴇᴛᴛɪɴɢꜱ ᴅᴇʟᴇᴛᴇᴅ.** 𝚁𝚎𝚜𝚝𝚊𝚛𝚝𝚒𝚗𝚐 𝚗𝚘𝚠...")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_callback_query(filters.regex("^cancel_reset$"))
async def cancel_reset_cb(client: Client, query: CallbackQuery):
    if query.from_user.id != client.owner:
        return await query.answer("This is not for you!", show_alert=True)
    await query.message.edit_text("**🥀 ʀᴇꜱᴇᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.**")

@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_new_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    try:
        ids_msg = await client.ask(query.from_user.id, "Send user ids seperated by a space in the next 60 seconds!\nEg: `838278682 83622928 82789928`", filters=filters.text, timeout=60)
        ids = ids_msg.text.split()
        
        for identifier in ids:
            if int(identifier) not in client.admins:
                client.admins.append(int(identifier))
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        await admins(client, query)
        await ids_msg.reply(f"__{len(ids)} admin {'id' if len(ids)==1 else 'ids'} have been promoted!!__")
    except Exception as e:
        await ids_msg.reply(f"Error: {e}")
    
@Client.on_callback_query(filters.regex("^rm_admin$"))
async def remove_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    try:
        ids_msg = await client.ask(query.from_user.id, "Send user ids seperated by a space in the next 60 seconds!\nEg: `838278682 83622928 82789928`", filters=filters.text, timeout=60)
        ids = ids_msg.text.split()
        
        for identifier in ids:
            if int(identifier) == client.owner:
                await client.send_message(query.from_user.id, "You cannot remove the owner from the admin list!")
                continue
            if int(identifier) in client.admins:
                client.admins.remove(int(identifier))
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        await admins(client, query)
        await ids_msg.reply(f"__{len(ids)} admin {'id' if len(ids)==1 else 'ids'} have been removed!!__")
    except Exception as e:
        await ids_msg.reply(f"Error: {e}")
