#  Developed by t.me/napaaextra

import aiohttp
import os
import random
import asyncio
import requests
from functools import partial

FALLBACK_SERVERS = [f"store{i}.gofile.io" for i in range(1, 15)]

class GofileManager:
    """
    Manages Gofile.io uploads using the robust `requests` library in a separate
    thread to prevent blocking the bot's async event loop.
    """
    def __init__(self, tokens, logger):
        self.tokens = tokens or []
        self.token_count = len(self.tokens)
        self.current_index = 0
        self.logger = logger
        self.api_url = "https://api.gofile.io"

    def _get_token(self):
        """Rotates and returns the next available token."""
        if not self.tokens:
            return None
        token = self.tokens[self.current_index]
        self.current_index = (self.current_index + 1) % self.token_count
        return token

    async def _get_server(self):
        """Fetches the best available server asynchronously, with a fallback system."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.api_url}/servers", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "ok":
                            servers = data["data"]["servers"]
                            server_object = random.choice(servers)
                            server_name = server_object['name']
                            self.logger.info(f"Gofile API chose server: {server_name}")
                            return server_name
            except Exception as e:
                self.logger.error(f"Gofile /servers API request failed: {e}")

        self.logger.warning("Gofile API failed. Using fallback server.")
        return random.choice(FALLBACK_SERVERS)

    def _blocking_upload(self, upload_url, file_path, token):
        """
        This is the blocking part of the upload that will run in a thread.
        It uses `requests` for a reliable upload.
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'token': token if token else ''}
                response = requests.post(upload_url, files=files, data=data, timeout=7200)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Requests upload failed: {e}")
            return None

    async def upload_file(self, file_path: str) -> str | None:
        """
        Asynchronously orchestrates the upload by running the blocking part
        in a separate thread.
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found for Gofile upload: {file_path}")
            return None

        server = await self._get_server()
        if not server:
            self.logger.error("Could not determine an upload server for Gofile.")
            return None

        upload_url = f"https://{server}.gofile.io/uploadFile"
        token = self._get_token()

        try:
            loop = asyncio.get_running_loop()
            response_data = await loop.run_in_executor(
                None,
                partial(self._blocking_upload, upload_url, file_path, token)
            )

            if response_data and response_data.get("status") == "ok":
                return response_data["data"].get("downloadPage")
            else:
                self.logger.error(f"Gofile upload API returned an error: {response_data}")
                return None
        except Exception as e:
            self.logger.error(f"Gofile upload thread failed: {e}", exc_info=True)
            return None
