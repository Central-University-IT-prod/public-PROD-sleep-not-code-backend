import asyncio
import os

from pyrogram import Client


async def main() -> None:
    async with Client(
        "bot",
        api_id=os.getenv("TELEGRAM_APP_ID"),
        api_hash=os.getenv("TELEGRAM_API_HASH"),
    ) as app:
        print("Exporting...")
        print(await app.export_session_string())


if __name__ == "__main__":
    asyncio.run(main())
