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
        intents.guilds = True  # Required to track server count accurately
        super().__init__(command_prefix=prefix, intents=intents)

    async def update_presence(self):
        """Update presence dynamically with total server count."""
        server_count = len(self.guilds)
        activity_name = f".help | {server_count} {'server' if server_count == 1 else 'servers'}"
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=activity_name
            )
        )

    async def setup_hook(self):
        await self.load_extension("cogs.economy")
        
        print("Syncing slash command tree...")
        await self.tree.sync()
        print("Command tree synced.")

    async def on_ready(self):
        print(f"Moguri is online as {self.user} (ID: {self.user.id})")
        await self.update_presence()

    async def on_guild_join(self, guild: discord.Guild):
        """Update presence when joining a new server."""
        await self.update_presence()

    async def on_guild_remove(self, guild: discord.Guild):
        """Update presence when leaving a server."""
        await self.update_presence()

async def main():
    bot = MoguriBot()
    token = os.getenv("DISCORD_TOKEN")
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
