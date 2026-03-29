#  Developed by t.me/napaaextra
import asyncio
from pyrogram.errors import FloodWait, ChatWriteForbidden, ChannelPrivate, MessageIdInvalid
from pyrogram.types import Message
from pyrogram.enums import ParseMode

async def instant_backup_files(client, channel_id: int, message_ids: list, status_msg: Message = None):
    """
    Ultra-robust instant backup with FIXED flood handling and proper error recovery.
    """
    backup_db_id = client.databases.get('backup')
    if not backup_db_id:
        client.LOGGER(__name__, client.name).info("No backup database configured - skipping backup")
        return
    
    total = len(message_ids)
    backed_up = 0
    skipped = 0
    failed = 0
    failed_ids = []
    
    client.LOGGER(__name__, client.name).info(f"🔄 Starting instant backup of {total} files...")
    
    if status_msg:
        try:
            await status_msg.edit_text(
                f"<b>⚡ Instant Backup Started!</b>\n\n"
                f"📦 Total files: {total}\n"
                f"⏳ Backing up...",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Failed to update status: {e}")
    
    batch_size = 5
    last_status_update = 0
    
    for batch_idx in range(0, len(message_ids), batch_size):
        batch = message_ids[batch_idx:batch_idx + batch_size]
        
        for idx, msg_id in enumerate(batch, start=batch_idx + 1):
            try:
                try:
                    if await client.mongodb.is_backed_up(channel_id, msg_id):
                        skipped += 1
                        client.LOGGER(__name__, client.name).info(f"⏭️ Skipped {msg_id} (already exists)")
                        continue
                except Exception as db_err:
                    client.LOGGER(__name__, client.name).warning(f"DB check failed for {msg_id}, proceeding: {db_err}")
                
                original_msg = None
                fetch_attempts = 0
                max_fetch_attempts = 10
                
                while fetch_attempts < max_fetch_attempts:
                    try:
                        original_msg = await client.get_messages(channel_id, msg_id)
                        break
                        
                    except FloodWait as e:
                        wait_time = min(e.x + 2, 120)
                        client.LOGGER(__name__, client.name).warning(
                            f"⏳ FloodWait {wait_time}s while fetching {msg_id} (attempt {fetch_attempts + 1})"
                        )
                        await asyncio.sleep(wait_time)
                        fetch_attempts += 1
                        continue
                        
                    except (ChatWriteForbidden, ChannelPrivate, MessageIdInvalid) as e:
                        client.LOGGER(__name__, client.name).error(f"❌ Cannot access {msg_id}: {e}")
                        failed += 1
                        failed_ids.append(msg_id)
                        break
                        
                    except Exception as e:
                        fetch_attempts += 1
                        client.LOGGER(__name__, client.name).warning(
                            f"⚠️ Fetch error for {msg_id} (attempt {fetch_attempts}/{max_fetch_attempts}): {e}"
                        )
                        if fetch_attempts >= max_fetch_attempts:
                            break
                        await asyncio.sleep(3)
                
                if not original_msg or original_msg.empty:
                    client.LOGGER(__name__, client.name).warning(f"❌ Message {msg_id} not found or empty after {fetch_attempts} attempts")
                    failed += 1
                    if msg_id not in failed_ids:
                        failed_ids.append(msg_id)
                    continue
                
                backup_success = False
                backup_attempts = 0
                max_backup_attempts = 10
                
                while backup_attempts < max_backup_attempts:
                    try:
                        backup_msg = await original_msg.copy(backup_db_id)
                        
                        await client.mongodb.add_backup_mapping(channel_id, msg_id, backup_msg.id)
                        
                        backed_up += 1
                        backup_success = True
                        client.LOGGER(__name__, client.name).info(f"✅ Backed up {msg_id} → {backup_msg.id}")
                        break
                        
                    except FloodWait as e:
                        wait_time = min(e.x + 2, 120)
                        client.LOGGER(__name__, client.name).warning(
                            f"⏳ FloodWait {wait_time}s while backing up {msg_id} (attempt {backup_attempts + 1})"
                        )
                        await asyncio.sleep(wait_time)
                        backup_attempts += 1
                        continue
                        
                    except (ChatWriteForbidden, ChannelPrivate) as e:
                        client.LOGGER(__name__, client.name).error(f"❌ No access to backup DB: {e}")
                        failed += 1
                        if msg_id not in failed_ids:
                            failed_ids.append(msg_id)
                        break
                        
                    except Exception as e:
                        backup_attempts += 1
                        client.LOGGER(__name__, client.name).warning(
                            f"⚠️ Backup error for {msg_id} (attempt {backup_attempts}/{max_backup_attempts}): {e}"
                        )
                        if backup_attempts >= max_backup_attempts:
                            break
                        await asyncio.sleep(3)
                
                if not backup_success and msg_id not in failed_ids:
                    failed += 1
                    failed_ids.append(msg_id)
                
                current_time = asyncio.get_event_loop().time()
                should_update = (
                    status_msg and 
                    (idx % 10 == 0 or idx == total) and 
                    (current_time - last_status_update) >= 5
                )
                
                if should_update:
                    try:
                        progress = (idx / total) * 100
                        status_text = (
                            f"<b>⚡ Instant Backup Progress</b>\n\n"
                            f"📊 Progress: {progress:.1f}%\n"
                            f"✅ Backed up: {backed_up}\n"
                            f"⏭️ Skipped: {skipped}\n"
                            f"❌ Failed: {failed}\n"
                            f"📦 Processed: {idx}/{total}"
                        )
                        await status_msg.edit_text(status_text, parse_mode=ParseMode.HTML)
                        last_status_update = current_time
                        
                    except FloodWait as e:
                        client.LOGGER(__name__, client.name).warning(f"FloodWait on status update, skipping: {e.x}s")
                        last_status_update = current_time + e.x
                        
                    except Exception as e:
                        client.LOGGER(__name__, client.name).warning(f"Failed to update progress: {e}")
                
                await asyncio.sleep(2.5)
                
            except Exception as e:
                client.LOGGER(__name__, client.name).error(f"❌ Critical error backing up {msg_id}: {e}")
                failed += 1
                if msg_id not in failed_ids:
                    failed_ids.append(msg_id)
                await asyncio.sleep(3)
        
        if batch_idx + batch_size < len(message_ids):
            pause_time = 8
            client.LOGGER(__name__, client.name).info(
                f"✅ Batch {batch_idx//batch_size + 1} complete ({backed_up + skipped + failed}/{total}), pausing {pause_time}s..."
            )
            await asyncio.sleep(pause_time)
    
    client.LOGGER(__name__, client.name).info(
        f"✅ Backup complete: {backed_up} backed up, {skipped} skipped, {failed} failed out of {total}"
    )
    
    if status_msg:
        try:
            final_text = (
                f"<b>✅ Instant Backup Complete!</b>\n\n"
                f"✅ Backed up: {backed_up}\n"
                f"⏭️ Already existed: {skipped}\n"
                f"❌ Failed: {failed}\n"
                f"📦 Total: {total}"
            )
            
            if failed_ids:
                if len(failed_ids) <= 10:
                    final_text += f"\n\n<b>Failed IDs:</b>\n<code>{', '.join(map(str, failed_ids))}</code>"
                else:
                    final_text += f"\n\n<b>Failed IDs:</b> {len(failed_ids)} files"
                    final_text += f"\n<code>{', '.join(map(str, failed_ids[:10]))}...</code>"
            
            await status_msg.edit_text(final_text, parse_mode=ParseMode.HTML)
            await asyncio.sleep(3)
            
        except FloodWait as e:
            client.LOGGER(__name__, client.name).warning(f"FloodWait on final summary: {e.x}s")
            await asyncio.sleep(e.x)
            try:
                await status_msg.edit_text(final_text, parse_mode=ParseMode.HTML)
            except:
                pass
                
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Failed to show final summary: {e}")
