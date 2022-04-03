import discord
from discord import app_commands
from discord.ext import commands

from hyena import Bot
from utils.automod_class import Automod


class Automoderation(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def _get_emoji(self, status: bool):
        if status is True:
            return f"{self.bot.success_emoji} Enabled"
        else:
            return f"{self.bot.failure_emoji} Disabled"

    @app_commands.command(
        name="automod-configuration",
        description="Shows the bots automod configuration.",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def automod_config(self, interaction: discord.Interaction):
        automod = Automod(self.bot, interaction.message)

        embed = discord.Embed(color=discord.Color.green())
        embed.title = "Automod Setup For {}".format(interaction.guild.name)
        embed.description = "`Automod Message:` {}".format(
            str(self.bot.config["automod_config"]["warn_message"]).replace(
                "$mention", interaction.user.mention
            )
        )

        filters = ["spam", "badwords", "caps", "invites", "phish"]
        ignored_channels = [
            self.bot.get_channel(channel).mention
            for channel in self.bot.config["automod_config"]["ignored_channels"]
            if channel is not None
        ]

        for filter in filters:
            status = automod.is_enabled(filter)
            embed.add_field(
                name=f"{filter.title()} Filter",
                value=self._get_emoji(status),
                inline=False,
            )

        if ignored_channels:
            embed.add_field(name="Ignored Channels", value=", ".join(ignored_channels))

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        automod = Automod(self.bot, message)

        if automod.is_author_mod():
            return

        if automod.is_ignored_channel():
            return

        if await automod.is_badwords():
            await automod.take_action()

        elif await automod.is_caps():
            await automod.take_action()

        elif await automod.is_invite():
            await automod.take_action()

        elif await automod.is_spam():
            await automod.take_action()

        elif await automod.is_phish_url():
            await automod.take_action()

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        message = after

        if message.author.id == self.bot.user.id:
            return

        automod = Automod(self.bot, message)

        if automod.is_author_mod():
            return

        if automod.is_ignored_channel():
            return

        if await automod.is_badwords():
            await automod.take_action()

        elif await automod.is_caps():
            await automod.take_action()

        elif await automod.is_invite():
            await automod.take_action()

        elif await automod.is_spam():
            await automod.take_action()

        elif await automod.is_phish_url():
            await automod.take_action()


async def setup(bot):
    await bot.add_cog(
        Automoderation(bot),
        guild=discord.Object(id=bot.config["bot_config"]["guild_id"]),
    )
