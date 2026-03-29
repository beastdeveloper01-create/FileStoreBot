#  Developed by t.me/napaaextra

#  Developed by t.me/napaaextra

import asyncio
import json
from bot import Bot, web_app
from pyrogram import compose

async def main():
    app = []

    try:
        with open("setup.json", "r") as f:
            setups = json.load(f)
    except FileNotFoundError:
        print("FATAL ERROR: setup.json not found. Please create it before running.")
        return
    except json.JSONDecodeError:
        print("FATAL ERROR: Could not parse setup.json. Please ensure it is a valid JSON file.")
        return

    for config in setups:
        app.append(
            Bot(config)
        )

    if not app:
        print("No valid bot configurations found in setup.json. Exiting.")
        return

    await compose(app)


async def runner():
    await asyncio.gather(
        main(),
        web_app()
    )

if __name__ == "__main__":
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
    except Exception as e:
        print(f"An unexpected error occurred during startup: {e}")
