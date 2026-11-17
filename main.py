import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class MoguriBot(commands.Bot):
    def __init__(self):
        prefix = os.getenv("PREFIX", ".")
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=prefix, intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.economy")
        
        print("Syncing slash command tree...")
        await self.tree.sync()
        print("Command tree synced.")

    async def on_ready(self):
        print(f"Moguri is online as {self.user} (ID: {self.user.id})")

async def main():
    bot = MoguriBot()
    token = os.getenv("DISCORD_TOKEN")
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
