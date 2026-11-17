import discord
from discord.ext import commands
from utils.database import db

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="balance", aliases=["bal"], description="Check user balance.")
    async def balance(self, ctx: commands.Context, target: discord.Member = None):
        target_user = target or ctx.author
        user_data = await db.get_user(target_user.id)

        embed = discord.Embed(
            title=f"{target_user.display_name}'s Balance",
            color=discord.Color.blue()
        )
        embed.add_field(name="Wallet", value=f"**{user_data['balance']:,}**", inline=True)
        embed.add_field(name="Bank", value=f"**{user_data['bank']:,}**", inline=True)
        embed.set_thumbnail(url=target_user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="work", description="Work to earn money.")
    async def work(self, ctx: commands.Context):
        earned = 250
        await db.update_balance(ctx.author.id, earned)

        embed = discord.Embed(
            description=f"You worked and earned **{earned:,}**!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="deposit", aliases=["dep"], description="Deposit money into bank.")
    async def deposit(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            return await ctx.send("Amount must be greater than 0.")

        user_data = await db.get_user(ctx.author.id)
        if user_data["balance"] < amount:
            return await ctx.send("You don't have enough money in your wallet.")

        await db.update_balance(ctx.author.id, -amount)
        await db.update_bank(ctx.author.id, amount)

        embed = discord.Embed(
            description=f"Deposited **{amount:,}** into your bank.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="withdraw", aliases=["with"], description="Withdraw money from bank.")
    async def withdraw(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            return await ctx.send("Amount must be greater than 0.")

        user_data = await db.get_user(ctx.author.id)
        if user_data["bank"] < amount:
            return await ctx.send("You don't have enough money in your bank.")

        await db.update_bank(ctx.author.id, -amount)
        await db.update_balance(ctx.author.id, amount)

        embed = discord.Embed(
            description=f"Withdrew **{amount:,}** from your bank.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
