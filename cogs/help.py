import discord
from discord.ext import commands

# Custom Emojis
HELP_EMOJI = "<a:TealQuestionMark:1572396828932972676>"
CARD_EMOJI = "<a:card:1572399301403873281>"
GENERAL_EMOJI = "<:general:1572398541349982219>"
STAR_EMOJI = "<:Star_Currency:1572392950460055574>"


class HelpSelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        
        options = [
            discord.SelectOption(
                label="Economy",
                description="Manage your wallet, bank, work, and star currency.",
                emoji=CARD_EMOJI,
                value="Economy"
            ),
            discord.SelectOption(
                label="General",
                description="General bot utility and information commands.",
                emoji=GENERAL_EMOJI,
                value="General"
            )
        ]
        super().__init__(
            placeholder="Select a category to view commands...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]

        if selected == "Economy":
            embed = discord.Embed(
                title=f"{CARD_EMOJI} Economy Commands",
                description=(
                    "Here are the economy commands available for **Moguri**:\n\n"
                    f"• **`.balance`** (or `bal`) — Check your wallet and bank.\n"
                    f"• **`.work`** — Do work to earn {STAR_EMOJI}.\n"
                    f"• **`.deposit`** (or `dep`) — Deposit currency into your bank (`.dep all`, `.dep 5m`).\n"
                    f"• **`.withdraw`** (or `with`) — Withdraw currency from your bank (`.with all`, `.with 10k`)."
                ),
                color=discord.Color.blurple()
            )
        elif selected == "General":
            embed = discord.Embed(
                title=f"{GENERAL_EMOJI} General Commands",
                description=(
                    "Here are the general commands available for **Moguri**:\n\n"
                    f"• **`.help`** — Opens this interactive help menu."
                ),
                color=discord.Color.blurple()
            )

        embed.set_footer(
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(bot))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except Exception:
            pass


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Shows the interactive help menu.")
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(
            title=f"{HELP_EMOJI} Moguri Help Menu",
            description="Welcome to Moguri! Use the dropdown menu below to navigate through the command categories.",
            color=discord.Color.magenta()
        )
        embed.add_field(name="Command Prefix", value="`.` (or use Slash commands `/`)", inline=False)
        embed.set_footer(text="Select a category from the menu below.")

        view = HelpView(self.bot)
        message = await ctx.send(embed=embed, view=view)
        view.message = message


async def setup(bot):
    bot.remove_command("help")
    await bot.add_cog(Help(bot))
