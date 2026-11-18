import os
import sys
import asyncio
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables from .env file (if present locally)
load_dotenv()

# ==========================================
# 1. ENVIRONMENT VARIABLE STARTUP CHECK
# ==========================================
REQUIRED_ENV_VARS = ["DISCORD_TOKEN", "MONGO_URI"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    print(f"❌ [CRITICAL ERROR] Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set them in your Railway variables dashboard or .env file before starting the bot.")
    sys.exit(1)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")


class MoguriBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=".",
            intents=intents,
            help_command=None  # We use our custom help cog
        )

    async def setup_hook(self):
        # ==========================================
        # 2. DATABASE CONNECTION STARTUP CHECK
        # ==========================================
        print("🔄 Verifying MongoDB connection...")
        try:
            # Initialize Motor client with a strict server selection timeout (5 seconds)
            db_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            
            # Ping the database to verify credentials & network connectivity
            await db_client.admin.command('ping')
            print("✅ MongoDB connection successful!")
        except Exception as e:
            print(f"❌ [CRITICAL ERROR] Failed to connect to MongoDB: {e}")
            print("Check your MONGO_URI string, IP whitelist restrictions, or network connection.")
            sys.exit(1)

        # Load extension cogs
        print("📦 Loading cogs...")
        try:
            await self.load_extension("cogs.economy")
            await self.load_extension("cogs.help")
            await self.load_extension("cogs.developer")
            print("✅ All cogs loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load cogs: {e}")
            sys.exit(1)

        # Sync command tree
        print("🔄 Syncing global command tree...")
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands globally.")
        except Exception as e:
            print(f"⚠️ Failed to sync command tree: {e}")

    async def on_ready(self):
        print(f"✨ Logged in as {self.user} (ID: {self.user.id})")
        print(f"🚀 Moguri is online and active across {len(self.guilds)} guilds!")
        
        # Dynamic Presence: Display server count
        guild_count = len(self.guilds)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{guild_count} servers | .help"
            )
        )


if __name__ == "__main__":
    bot = MoguriBot()
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ [CRITICAL ERROR] Invalid DISCORD_TOKEN provided. Please check your credentials.")
    except Exception as e:
        print(f"❌ An unexpected error occurred during startup: {e}")
