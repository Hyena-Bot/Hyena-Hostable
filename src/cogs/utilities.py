import discord
from discord import app_commands
from discord.ext import commands


class Utilities(commands.Cog):
    """Utilities cog"""

    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(
        Utilities(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
