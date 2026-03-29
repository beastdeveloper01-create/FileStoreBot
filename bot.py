#  Developed by t.me/napaaextra

#  Developed by t.me/napaaextra
from aiohttp import web
from plugins import web_server

from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import LOGGER, PORT, OWNER_ID, SHORT_URL, SHORT_API
from helper import MongoDB, GofileManager

version = "v1.0.0"

class Bot(Client):
    def __init__(self, config):
        session = config["session"]
        workers = config["workers"]
        databases = config.get("databases", {"primary": config.get("db"), "secondary": [], "backup": None})
        fsub = config["fsubs"]
        token = config["token"]
        admins = config["admins"]
        messages = config.get("messages", {})
        auto_del = config["auto_del"]
        db_uri = config["db_uri"]
        db_name = config["db_name"]
        api_id = int(config["api_id"])
        api_hash = config["api_hash"]
        protect = config["protect"]
        disable_btn = config["disable_btn"]

        super().__init__(
            name=session, api_hash=api_hash, api_id=api_id,
            plugins={"root": "plugins"}, workers=workers, bot_token=token
        )
        self.LOGGER = LOGGER
        self.name = session
        self.databases = databases
        self.db = databases.get('primary')
        self.fsub = fsub
        self.owner = OWNER_ID
        self.fsub_dict = {}
        self.admins = admins + [OWNER_ID] if OWNER_ID not in admins else admins
        self.messages = messages
        self.auto_del = auto_del
        self.req_fsub = {}
        self.disable_btn = disable_btn
        self.reply_text = messages.get('REPLY', 'Do not send any useless message in the bot.')
        self.mongodb = MongoDB(db_uri, db_name)
        self.req_channels = []
        self.all_db_ids = []
        
        self.gofile_enabled = config.get("gofile_enabled", False)
        gofile_tokens = config.get("gofile_tokens", [])
        self.gofile_manager = GofileManager(gofile_tokens, self.LOGGER(__name__, self.name))
        self.active_uploads = set()

        self.protect = protect
        self.shortner_enabled = True
        self.short_url = SHORT_URL
        self.short_api = SHORT_API
        self.tutorial_link = "https://t.me/+zYJNXKoRIGs5YmY1"
        self.auto_approval_enabled = False
        self.approval_delay = 5
        self.autobatch_template = ""
        self.hide_caption = False
        self.channel_button_enabled = False
        self.button_name = "Join Updates"
        self.button_url = "https://t.me/realm_bots"
        self.credit_system_enabled = False
        self.credits_per_visit = 1
        self.credits_per_file = 1
        self.max_credit_limit = 100
    
    def get_current_settings(self):
        """Returns the dictionary for the legacy settings system."""
        return {
            "admins": self.admins,
            "messages": self.messages,
            "auto_del": self.auto_del,
            "disable_btn": self.disable_btn,
            "reply_text": self.reply_text,
            "fsub": self.fsub,
            "databases": self.databases
        }

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        from plugins.autobatch_settings import DEFAULT_AUTOBATCH_TEMPLATE
        self.autobatch_template = await self.mongodb.load_bot_setting('autobatch_template', DEFAULT_AUTOBATCH_TEMPLATE)
        self.protect = await self.mongodb.load_bot_setting('protect_content', self.protect)
        self.hide_caption = await self.mongodb.load_bot_setting('hide_caption', False)
        self.channel_button_enabled = await self.mongodb.load_bot_setting('channel_button_enabled', False)
        self.button_name = await self.mongodb.load_bot_setting('button_name', self.button_name)
        self.button_url = await self.mongodb.load_bot_setting('button_url', self.button_url)
        self.auto_approval_enabled = await self.mongodb.load_bot_setting('auto_approval_enabled', False)
        self.approval_delay = await self.mongodb.load_bot_setting('approval_delay', 5)
        
        self.shortner_enabled = await self.mongodb.load_bot_setting('shortner_enabled', True)
        self.short_url = await self.mongodb.load_bot_setting('short_url', SHORT_URL)
        self.short_api = await self.mongodb.load_bot_setting('short_api', SHORT_API)
        self.tutorial_link = await self.mongodb.load_bot_setting('tutorial_link', self.tutorial_link)
        
        self.credit_system_enabled = await self.mongodb.load_bot_setting('credit_system_enabled', False)
        self.credits_per_visit = await self.mongodb.load_bot_setting('credits_per_visit', 1)
        self.credits_per_file = await self.mongodb.load_bot_setting('credits_per_file', 1)
        self.max_credit_limit = await self.mongodb.load_bot_setting('max_credit_limit', 100)
        
        self.gofile_enabled = await self.mongodb.load_bot_setting('gofile_enabled', self.gofile_enabled)
        db_gofile_tokens = await self.mongodb.load_bot_setting('gofile_tokens')

        if db_gofile_tokens is not None:
            self.gofile_manager = GofileManager(db_gofile_tokens, self.LOGGER(__name__, self.name))
            self.LOGGER(__name__, self.name).info(f"Loaded {len(db_gofile_tokens)} Gofile tokens from the database.")
        elif self.gofile_manager and self.gofile_manager.tokens:
            self.LOGGER(__name__, self.name).info(f"Using {self.gofile_manager.token_count} Gofile tokens from setup.json.")
        
        if not self.short_url or self.short_url.lower() in ["none", ""]:
            self.short_url = SHORT_URL
        if not self.short_api or self.short_api.lower() in ["none", ""]:
            self.short_api = SHORT_API
            
        self.LOGGER(__name__, self.name).info("All modern settings loaded and validated.")
        
        saved_settings = await self.mongodb.load_settings(self.name)
        if saved_settings:
            self.LOGGER(__name__, self.name).info("Found legacy saved settings, merging them.")
            base_messages = self.messages.copy()
            saved_messages = saved_settings.get("messages", {})
            for key, value in saved_messages.items():
                if value: base_messages[key] = value
            self.messages = base_messages
            
            saved_admins = saved_settings.get("admins", [])
            self.admins = list(set(self.admins + saved_admins + [OWNER_ID]))
            
            if saved_fsub := saved_settings.get("fsub"): self.fsub = saved_fsub
            if saved_databases := saved_settings.get("databases"):
                self.databases = saved_databases
                self.db = self.databases.get('primary')
            
            self.auto_del = saved_settings.get("auto_del", self.auto_del)
            self.disable_btn = saved_settings.get("disable_btn", self.disable_btn)
            self.reply_text = saved_settings.get("reply_text", self.reply_text)
        
        self.fsub_dict = {}
        if self.fsub:
            for channel_id, needs_request, timer in self.fsub:
                try:
                    chat = await self.get_chat(channel_id)
                    invite_link = chat.invite_link
                    if not invite_link and timer <= 0:
                        invite_link = (await self.create_chat_invite_link(channel_id, creates_join_request=needs_request)).invite_link
                    self.fsub_dict[channel_id] = [chat.title, invite_link, needs_request, timer]
                    if needs_request: self.req_channels.append(channel_id)
                except Exception as e:
                    self.LOGGER(__name__, self.name).error(f"Error processing FSub channel {channel_id}: {e}.")
            await self.mongodb.set_channels(self.req_channels)

        if not self.db:
            self.LOGGER(__name__, self.name).warning("No Primary Database channel is set!")
        else:
            try:
                db_channel = await self.get_chat(self.db)
                self.db_channel = db_channel
                test = await self.send_message(chat_id=db_channel.id, text="Bot is online.")
                await test.delete()
            except Exception as e:
                self.LOGGER(__name__, self.name).warning(e)
                self.LOGGER(__name__, self.name).warning(f"Make sure bot is Admin in Primary DB Channel. Current Value {self.db}")

        self.all_db_ids = [db_id for db_id in [self.databases.get('primary')] + self.databases.get('secondary', []) if db_id]
        self.LOGGER(__name__, self.name).info(f"Loaded {len(self.all_db_ids)} DB channels.")
        self.LOGGER(__name__, self.name).info(f"Bot Started on @{usr_bot_me.username} !!")
        self.username = usr_bot_me.username

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__, self.name).info("Bot stopped.")

async def web_app():
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
