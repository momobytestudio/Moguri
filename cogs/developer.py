import io
import textwrap
import traceback
import contextlib
import discord
from discord.ext import commands
from utils.database import db

DEV_EMOJI = "<:general:1572398541349982219>"
STAR_EMOJI = "<:Star_Currency:1572392950460055574>"

def parse_dev_amount(amount_str: str) -> int:
    """Parse string inputs like '10k', '5.5m', '2b' into integer values."""
    import re
    amount_str = str(amount_str).strip().lower()

    match = re.match(r"^(\d+(?:\.\d+)?)\s*([a-z]+)?$", amount_str)
    if not match:
        raise ValueError("Invalid amount format.")

    val, suffix = match.groups()
    val = float(val)

    suffixes = {
        "k": 10**3,
        "m": 10**6,
        "b": 10**9,
        "t": 10**12,
        "qa": 10**15,
        "qi": 10**18,
        "sx": 10**21,
        "sp": 10**24,
        "oc": 10**27,
        "no": 10**30,
        "dc": 10**33,
    }

    if suffix:
        if suffix not in suffixes:
            raise ValueError(f"Unknown suffix: {suffix}")
        val *= suffixes[suffix]

    return int(val)


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.hybrid_command(name="admincmds", aliases=["ac", "devhelp"], description="[DEV] Display developer commands.")
    async def admincmds(self, ctx: commands.Context):
        """Displays short developer & admin command list."""
        embed = discord.Embed(
            title=f"{DEV_EMOJI} ᴍᴏɢᴜʀɪ • ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ",
            description="*ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ᴛᴏ ʙᴏᴛ ᴏᴡɴᴇʀ ᴏɴʟʏ.*",
            color=discord.Color.dark_embed()
        )

        embed.add_field(
            name="⚙️ Core & System",
            value=(
                "• **`.ac`** — Show admin command menu\n"
                "• **`.sy`** [guild] — Sync command tree\n"
                "• **`.rl`** [cog] — Reload extension cog\n"
                "• **`.ev`** [code] — Evaluate Python code"
            ),
            inline=False
        )

        embed.add_field(
            name=f"{STAR_EMOJI} Data & Economy",
            value=(
                "• **`.am`** [@user] [amt] [loc] — Add currency\n"
                "• **`.rm`** [@user] [amt] [loc] — Remove currency\n"
                "• **`.ru`** [@user] — Reset user data\n"
                "• **`.re`** CONFIRM — Wipe entire economy"
            ),
            inline=False
        )

        embed.set_footer(text="Moguri Bot • Dev Console", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="sync", aliases=["sy"], description="[DEV] Sync slash commands.")
    async def sync(self, ctx: commands.Context, spec: str = None):
        if spec == "guild":
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"Synced {len(synced)} commands to this guild.")
        else:
            synced = await self.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands globally.")

    @commands.hybrid_command(name="reload", aliases=["rl"], description="[DEV] Reload a specific cog.")
    async def reload(self, ctx: commands.Context, cog_name: str):
        try:
            await self.bot.reload_extension(f"cogs.{cog_name.lower()}")
            embed = discord.Embed(
                description=f"{DEV_EMOJI} Successfully reloaded `cogs.{cog_name.lower()}`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"Failed to reload `cogs.{cog_name.lower()}`:\n```py\n{e}\n```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="addmoney", aliases=["am", "addbal"], description="[DEV] Add currency to a user.")
    async def addmoney(self, ctx: commands.Context, target: discord.Member, amount: str, target_location: str = "wallet"):
        try:
            parsed_val = parse_dev_amount(amount)
        except ValueError:
            return await ctx.send("Invalid format. Examples: `.am @user 10m`, `.am @user 500k bank`")

        if target_location.lower() in ["bank", "b"]:
            await db.update_bank(target.id, parsed_val)
            loc = "bank"
        else:
            await db.update_balance(target.id, parsed_val)
            loc = "wallet"

        formatted_val = db.format_number(parsed_val)
        embed = discord.Embed(
            description=f"Added {STAR_EMOJI} **{formatted_val}** to {target.mention}'s {loc}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="removemoney", aliases=["rm", "rembal"], description="[DEV] Remove currency from a user.")
    async def removemoney(self, ctx: commands.Context, target: discord.Member, amount: str, target_location: str = "wallet"):
        try:
            parsed_val = parse_dev_amount(amount)
        except ValueError:
            return await ctx.send("Invalid format. Examples: `.rm @user 10m`, `.rm @user 500k bank`")

        if target_location.lower() in ["bank", "b"]:
            await db.update_bank(target.id, -parsed_val)
            loc = "bank"
        else:
            await db.update_balance(target.id, -parsed_val)
            loc = "wallet"

        formatted_val = db.format_number(parsed_val)
        embed = discord.Embed(
            description=f"Removed {STAR_EMOJI} **{formatted_val}** from {target.mention}'s {loc}.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="resetuser", aliases=["ru", "resetdata"], description="[DEV] Reset a user's economy data.")
    async def resetuser(self, ctx: commands.Context, target: discord.Member):
        await db.reset_user(target.id)

        embed = discord.Embed(
            description=f"{DEV_EMOJI} Successfully reset economy data for {target.mention}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="reseteconomy", aliases=["re"], description="[DEV] Reset the entire economy database.")
    async def reseteconomy(self, ctx: commands.Context, confirm: str = None):
        if confirm != "CONFIRM":
            return await ctx.send("⚠️ **WARNING:** This will reset the entire economy!\nType `.re CONFIRM` to proceed.")

        result = await db.reset_economy()

        embed = discord.Embed(
            title="⚠️ Economy Reset Executed",
            description=f"Successfully reset **{result.modified_count}** user profiles back to starting defaults.",
            color=discord.Color.dark_red()
        )
        await ctx.send(embed=embed)

    @commands.command(name="eval", aliases=["ev"], description="[DEV] Evaluate raw Python code.")
    async def eval_code(self, ctx: commands.Context, *, body: str):
        if body.startswith("```") and body.endswith("```"):
            body = "\n".join(body.split("\n")[1:-1])

        body = body.strip("` \n")
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, globals())

            func = globals()["func"]
            with contextlib.redirect_stdout(stdout):
                await func()

            out = stdout.getvalue()
            if out:
                await ctx.send(f"```py\n{out}\n```")
            else:
                await ctx.send("Execution finished with no output.")
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")


async def setup(bot):
    await bot.add_cog(Developer(bot))
