"""
Licensed under GNU General Public License v3.0


Permissions of this strong copyleft license are 
conditioned on making available complete source 
code of licensed works and modifications, which 
include larger works using a licensed work, 
under the same license. Copyright and license 
notices must be preserved. Contributors provide
an express grant of patent rights.

Permissions:
    Commercial use
    Modification
    Distribution
    Patent use
    Private use

Limitations:
    Liability
    Warranty

Conditions:
    License and copyright notice
    State changes
    Disclose source
    Same license

Kindly check out ../LICENSE
"""

import discord
from discord import app_commands
from discord.ext import commands


class Automoderation(commands.Cog):
    """Automoderation commands & handlers"""

    def __init__(self, bot):
        self.bot = bot
        self.caps_limit = self.bot.config["automod_config"]["caps_threshold"]
        self.delete_after = self.bot.config["automod_config"]["delete_message_after"]
        self.mention_limit = self.bot.config["automod_config"]["mention_limit"]

    def _get_emoji(self, status: bool):
        """Returns the emoji for the given status [True|False]"""
        if status is True:
            return f"{self.bot.success_emoji} Enabled"
        else:
            return f"{self.bot.failure_emoji} Disabled"

    @app_commands.command(
        name="automod-configuration",
        description="Shows the bot's automod configuration.",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def automod_config(self, interaction: discord.Interaction):
        """
        **Description:**
        Shows the bot's automod config

        **Args:**
        • None

        **Syntax:**
        ```
        /automod-configuration
        ```
        """
        automod = self.bot.AutomodHandler(self.bot, interaction.message)

        embed = discord.Embed(color=discord.Color.green())
        embed.title = "Automod Setup For {}".format(interaction.guild.name)
        embed.description = f"`Automod Config` for {interaction.guild.name}"
        filters = ["spam", "badwords", "caps", "invites", "phish", "nsfw", "mentions"]
        ignored_channels = [
            self.bot.get_channel(channel).mention
            for channel in self.bot.config["automod_config"]["ignored_channels"]
            if channel is not None
        ]

        for _filter in filters:
            status = automod.is_enabled(_filter)
            embed.add_field(
                name=f"{_filter.title()} Filter",
                value=self._get_emoji(status),
                inline=False,
            )

        if ignored_channels:
            embed.add_field(name="Ignored Channels", value=", ".join(ignored_channels))

        await interaction.response.send_message(embed=embed)

    async def _handler(self, message: discord.Message) -> None:
        """The main automod handler"""
        automod = self.bot.AutomodHandler(self.bot, message)
        member = message.guild.get_member(message.author.id)

        if (
            not message.guild
            or message.author.id == self.bot.user.id
            or automod.is_author_mod()
            or automod.is_ignored_channel()
        ):
            return

        if await automod.is_badwords():
            await message.channel.send(
                f"{member.mention}, that word is blacklisted.",
                delete_after=self.delete_after,
            )
            await automod.take_action()

        elif await automod.is_caps():
            await message.channel.send(
                f"{member.mention}, you exceeded the capitals limit : `{self.caps_limit}`% of your message length",
                delete_after=self.delete_after,
            )
            await automod.take_action()

        elif await automod.is_invite():
            await message.channel.send(
                f"{member.mention}, do not send invite links.",
                delete_after=self.delete_after,
            )
            await automod.take_action()

        elif await automod.is_spam():
            await message.channel.send(
                f"{member.mention}, stop spamming idiot.", delete_after=2
            )
            await automod.take_action()

        elif await automod.is_phish_url():
            await message.channel.send(
                f"{member.mention}, you really think you can phish people?",
                delete_after=self.delete_after,
            )
            await automod.take_action()

        elif await automod.is_nsfw():
            await message.channel.send(
                f"{member.mention}, bruv you are not allowed to send NSFW content here.",
                delete_after=self.delete_after,
            )
            await automod.take_action()

        elif await automod.excess_mentions():
            await message.channel.send(
                f"{member.mention}, too many mentions in a message. Maximum allowed: {self.mention_limit}",
                delete_after=self.delete_after,
            )
            await automod.take_action()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Moderate on message"""
        await self._handler(message)

    @commands.Cog.listener()
    async def on_message_edit(self, _: discord.Message, after: discord.Message):
        """Moderate on a message edit"""
        await self._handler(after)


async def setup(bot):
    await bot.add_cog(
        Automoderation(bot),
        guild=discord.Object(id=bot.config["bot_config"]["guild_id"]),
    )
