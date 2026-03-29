#  Developed by t.me/napaaextra

import asyncio
import os
import shutil
from pyrogram.errors import FloodWait

async def background_upload_task(client, channel_id: int, message_id: int):
    """
    A background task to download a file from Telegram, upload it to Gofile.io,
    and store the resulting link in the database.
    """
    upload_identifier = (channel_id, message_id)
    logger = client.LOGGER(__name__, "GofileUploader")

    if upload_identifier in client.active_uploads:
        logger.info(f"Upload for {upload_identifier} is already in progress. Skipping.")
        return
    
    if await client.mongodb.get_gofile_link(channel_id, message_id):
        return

    client.active_uploads.add(upload_identifier)
    temp_dir = f"./downloads/{channel_id}_{message_id}/"
    
    try:
        logger.info(f"Starting Gofile background upload for {upload_identifier}...")
        
        tg_message = await client.get_messages(channel_id, message_id)
        if not tg_message or not tg_message.media:
            logger.warning(f"Message {upload_identifier} has no media. Aborting Gofile upload.")
            return

        file_path = await tg_message.download(file_name=temp_dir)
        if not file_path:
             logger.error(f"Failed to download {upload_identifier} from Telegram.")
             return

        gofile_url = await client.gofile_manager.upload_file(file_path)

        if gofile_url:
            await client.mongodb.save_gofile_link(channel_id, message_id, gofile_url)
            logger.info(f"✅ Successfully uploaded {upload_identifier} to Gofile: {gofile_url}")
        else:
            logger.error(f"❌ Failed to upload {upload_identifier} to Gofile.")

    except FloodWait as e:
        logger.warning(f"FloodWait of {e.x}s during Gofile task for {upload_identifier}. Task will not be retried.")
    except Exception as e:
        logger.error(f"An error occurred during Gofile background upload for {upload_identifier}: {e}", exc_info=True)
    finally:
        if upload_identifier in client.active_uploads:
            client.active_uploads.remove(upload_identifier)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
