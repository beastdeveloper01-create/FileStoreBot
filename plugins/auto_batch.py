#  Developed by t.me/napaaextra
#  Developed by t.me/napaaextra
import re
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import encode, get_message_id, get_messages

MIGRATOR_BOT = "LelouchAMbot"

QUALITY_PATTERNS = {
    "4k": re.compile(r'2160p|4k', re.IGNORECASE),
    "1080p": re.compile(r'1080p', re.IGNORECASE),
    "720p": re.compile(r'720p', re.IGNORECASE),
    "480p": re.compile(r'480p', re.IGNORECASE),
    "hdrip": re.compile(r'HDRip', re.IGNORECASE),
    "bluray": re.compile(r'BluRay', re.IGNORECASE),
    "webdl": re.compile(r'WEB-DL|WEBRip', re.IGNORECASE),
    "hevc": re.compile(r'HEVC|x265', re.IGNORECASE),
}

QUALITY_DISPLAY_NAMES = {
    "4k": "2160p | 4K", "1080p": "1080p", "720p": "720p", "480p": "480p",
    "hdrip": "HDRip", "bluray": "BluRay", "webdl": "WEB-DL", "hevc": "HEVC x265", "other": "Other"
}

def get_file_quality(filename: str):
    if not isinstance(filename, str): return "other"
    for quality, pattern in QUALITY_PATTERNS.items():
        if pattern.search(filename): return quality
    return "other"
    
async def ask_for_message(client, user_id, prompt_text):
    prompt_message = await client.send_message(user_id, prompt_text, parse_mode=ParseMode.HTML)
    try:
        response = await client.listen(chat_id=user_id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=120)
        await prompt_message.delete()
        return response
    except ListenerTimeout:
        await prompt_message.edit("<b>⏰ Timeout!</b> Please try the command again.")
        return None

@Client.on_message(filters.private & filters.command('autobatch'))
async def auto_batch_range_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    logger = client.LOGGER(__name__, "autobatch")

    while True:
        first_message = await ask_for_message(client, message.from_user.id, "<b>📨 Forward the <u>First Message</u> from DB Channel</b>")
        if not first_message: return
        f_channel_id, f_msg_id = await get_message_id(client, first_message)
        if f_msg_id: break
        else: await first_message.reply("❌ <b>Invalid Message</b>: Not from a configured DB channel.", quote=True)
    while True:
        second_message = await ask_for_message(client, message.from_user.id, "<b>📨 Forward the <u>Last Message</u> from DB Channel</b>")
        if not second_message: return
        s_channel_id, s_msg_id = await get_message_id(client, second_message)
        if s_msg_id: break
        else: await second_message.reply("❌ <b>Invalid Message</b>: Not from a configured DB channel.", quote=True)
    if f_channel_id != s_channel_id:
        return await second_message.reply("❌ Both messages must be from the same DB channel.")
    if f_msg_id >= s_msg_id:
        return await second_message.reply("❌ The first message ID must be smaller than the last one.")
    msg_ids_range = list(range(f_msg_id, s_msg_id + 1))
    prompt = await second_message.reply_text(f"⏳ <b>Fetching {len(msg_ids_range)} messages...</b>")
    
    try:
        messages_to_process = await get_messages(client, f_channel_id, msg_ids_range)
        if not messages_to_process:
            return await prompt.edit_text("❌ Could not fetch any messages for the given range.")

        await prompt.edit_text(f"⚙️ <b>Processing {len(messages_to_process)} files...</b>")
        
        grouped_files = {}
        for msg in messages_to_process:
            file = getattr(msg, 'document', getattr(msg, 'video', None))
            filename = file.file_name if file else "Unknown"
            quality = get_file_quality(filename)
            if quality not in grouped_files:
                grouped_files[quality] = []
            grouped_files[quality].append(msg.id)

        if not grouped_files:
            return await prompt.edit_text("❌ No valid files could be grouped.")

        from plugins.autobatch_settings import DEFAULT_AUTOBATCH_TEMPLATE
        use_custom_template = client.autobatch_template != DEFAULT_AUTOBATCH_TEMPLATE and client.autobatch_template != ""

        final_text = ""
        generated_links = {}

        for quality, msg_ids in grouped_files.items():
            if not msg_ids: continue
            batch_key = await client.mongodb.save_batch(f_channel_id, msg_ids)
            base64_string = await encode(f"batch_{batch_key}")
            generated_links[quality] = {
                "migrator": f"https://t.me/{MIGRATOR_BOT}?start={base64_string}",
                "direct": f"https://t.me/{client.username}?start={base64_string}",
                "count": len(msg_ids)
            }
        
        if use_custom_template:
            placeholders = {"{totalfilecount}": str(len(messages_to_process))}
            for key in QUALITY_DISPLAY_NAMES.keys():
                link_data = generated_links.get(key)
                if link_data:
                    placeholders[f"{{{key}}}"] = QUALITY_DISPLAY_NAMES.get(key)
                    placeholders[f"{{{key}link}}"] = link_data["migrator"]
                    placeholders[f"{{{key}directlink}}"] = link_data["direct"]
                    placeholders[f"{{{key}filecount}}"] = str(link_data["count"])
                else:
                    placeholders.update({f"{{{key}}}": "", f"{{{key}link}}": "", f"{{{key}directlink}}": "", f"{{{key}filecount}}": ""})
            
            final_text = client.autobatch_template
            for key, value in placeholders.items():
                final_text = final_text.replace(key, value)
            
            final_text = "\n".join(line for line in final_text.split('\n') if line.strip() and '{' not in line)
        else:
            display_map = {"480p": "480p", "720p": "720p", "1080p": "1080p", "4k": "4K", "other": "Other"}
            quality_order = ["480p", "720p", "1080p", "4k", "hdrip", "bluray", "webdl", "hevc", "other"]
            sorted_qualities = [q for q in quality_order if q in generated_links]
            
            response_text = "<b>⬇️ ʙᴇʟᴏᴡ ɪꜱ ᴛʜᴇ ʙᴀᴛᴄʜ ʟɪɴᴋ:</b>\n\n<b>ʀᴇᴅɪʀᴇᴄᴛ ʙᴏᴛ ʟɪɴᴋꜱ:</b>\n<blockquote>"
            for qk in sorted_qualities:
                label = display_map.get(qk, QUALITY_DISPLAY_NAMES.get(qk))
                response_text += f"\n<b>{label}</b> ({generated_links[qk]['count']} files):\n<code>{generated_links[qk]['migrator']}</code>\n"
            
            response_text += "</blockquote>\n<b>ᴅɪʀᴇᴄᴛ ʟɪɴᴋꜱ:</b>\n<blockquote>"
            for qk in sorted_qualities:
                label = display_map.get(qk, QUALITY_DISPLAY_NAMES.get(qk))
                response_text += f"<b>{label}:</b> <code>{generated_links[qk]['direct']}</code>\n"
            response_text += "</blockquote>"
            final_text = response_text
        
        buttons = []
        button_order = ["480p", "720p", "1080p", "4k", "hdrip", "bluray", "webdl", "hevc", "other"]
        
        for quality_key in button_order:
            if quality_key in generated_links:
                button_text = QUALITY_DISPLAY_NAMES.get(quality_key).split(' | ')[-1]
                buttons.append(InlineKeyboardButton(text=button_text, url=generated_links[quality_key]['migrator']))
        
        reply_markup = InlineKeyboardMarkup([buttons[i:i + 2] for i in range(0, len(buttons), 2)]) if buttons else None

        await prompt.edit_text(
            final_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML
        )
        
    except Exception:
        logger.error(traceback.format_exc())
        await message.reply_text(f"<b>❌ An error occurred! Please check your template for formatting errors.</b>")
