import re
import discord
from discord.ext import commands
from utils.database import db

# Custom Currency Emoji
CURRENCY_EMOJI = "<:Star_Currency:1572392950460055574>"

def parse_amount(amount_str: str, current_balance: int) -> int:
    """Parse string inputs like 'all', 'half', '10k', '5.5m', '2b' into integer values."""
    amount_str = str(amount_str).strip().lower()

    if amount_str in ["all", "max"]:
        return current_balance
    if amount_str in ["half", "50%"]:
        return current_balance // 2

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


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="balance", aliases=["bal"], description="Check user balance.")
    async def balance(self, ctx: commands.Context, target: discord.Member = None):
        target_user = target or ctx.author
        user_data = await db.get_user(target_user.id)

        wallet_str = db.format_number(user_data["balance"])
        bank_str = db.format_number(user_data["bank"])

        embed = discord.Embed(
            title=f"{target_user.display_name}'s Balance",
            color=discord.Color.blue()
        )
        embed.add_field(name="Wallet", value=f"{CURRENCY_EMOJI} **{wallet_str}**", inline=True)
        embed.add_field(name="Bank", value=f"🏛️ **{bank_str}**", inline=True)
        embed.set_thumbnail(url=target_user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="work", description="Work to earn money.")
    async def work(self, ctx: commands.Context):
        earned = 250
        await db.update_balance(ctx.author.id, earned)

        earned_str = db.format_number(earned)
        embed = discord.Embed(
            description=f"You worked and earned {CURRENCY_EMOJI} **{earned_str}**!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="deposit", aliases=["dep"], description="Deposit money into bank.")
    async def deposit(self, ctx: commands.Context, amount: str):
        user_data = await db.get_user(ctx.author.id)
        wallet = user_data["balance"]

        try:
            parsed_amount = parse_amount(amount, wallet)
        except ValueError:
            return await ctx.send("Invalid amount. Example usage: `.dep 100`, `.dep 5m`, `.dep all`")

        if parsed_amount <= 0:
            return await ctx.send("Amount must be greater than 0.")
        if wallet < parsed_amount:
            return await ctx.send("You don't have enough money in your wallet.")

        await db.update_balance(ctx.author.id, -parsed_amount)
        await db.update_bank(ctx.author.id, parsed_amount)

        dep_str = db.format_number(parsed_amount)
        embed = discord.Embed(
            description=f"Deposited {CURRENCY_EMOJI} **{dep_str}** into your bank.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="withdraw", aliases=["with"], description="Withdraw money from bank.")
    async def withdraw(self, ctx: commands.Context, amount: str):
        user_data = await db.get_user(ctx.author.id)
        bank = user_data["bank"]

        try:
            parsed_amount = parse_amount(amount, bank)
        except ValueError:
            return await ctx.send("Invalid amount. Example usage: `.with 100`, `.with 5m`, `.with all`")

        if parsed_amount <= 0:
            return await ctx.send("Amount must be greater than 0.")
        if bank < parsed_amount:
            return await ctx.send("You don't have enough money in your bank.")

        await db.update_bank(ctx.author.id, -parsed_amount)
        await db.update_balance(ctx.author.id, parsed_amount)

        with_str = db.format_number(parsed_amount)
        embed = discord.Embed(
            description=f"Withdrew {CURRENCY_EMOJI} **{with_str}** from your bank.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
