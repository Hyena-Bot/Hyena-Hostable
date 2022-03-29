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

import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="timeout",
        description="Timeout (Mute) a user so they cannot add reactions/speak/join voice channels.",
    )
    @app_commands.checks.cooldown(1, 3)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        member="The member to timeout/mute",
        time="how long to timeout the member [Max - 28 days] ex. /timeout <user> 10 days 5 seconds",
        reason="The reason to timeout/mute the member",
    )
    async def _timeout(
        self,
        interaction,
        member: discord.Member,
        time: str,
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        Timeout (Mute) a user so they cannot add reactions/speak/join voice channels.

        **Args:**
        • `<member>` - The member to timeout
        • `<time>` - how long to timeout the member [Max - 28 days] ex. `/timeout <user> 10 days 5 seconds`
        • `[reason]` - The reason to timeout the member

        **Syntax:**
        ```
        /timeout <member> <time> [reason]
        ```
        """
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message(
                f"Your top role `{interaction.user.top_role.name}` is lower or equal to {member}'s top role `{member.top_role.name}`"
            )

        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                f"My top role `{interaction.guild.me.top_role.name}` is lower or equal to {member}'s top role `{member.top_role.name}`"
            )

        delta = self.bot.tools.convert_time(time)

        if delta > datetime.timedelta(days=28):
            return await interaction.response.send_message(
                "> Timeout cannot be greater than 28 days!"
            )

        await member.timeout(delta, reason=reason)

        await interaction.response.send_message(
            f"🔇 Timed out `{member}` \n**Reason:** {reason}\n**Duration:** {delta}"
        )
        try:
            await member.send(
                f"**{interaction.guild.name}:** You have been 🔇 timed out (Duration : {delta})\n**Reason:** {reason}"
            )
        except:
            pass

    @app_commands.command(
        name="timeout-end", description="End timeout (Mute) of a user."
    )
    @app_commands.checks.cooldown(1, 3)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        member="The member to end timeout/mute of",
        reason="The reason to end the timeout of the member",
    )
    async def _end_timeout(
        self,
        interaction,
        member: discord.Member,
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        End timeout (Mute) of a user.

        **Args:**
        • `<member>` - The member to end the timeout of
        • `[reason]` - The reason to end the timeout of the member

        **Syntax:**
        ```
        /timeout-end <member> [reason]
        ```
        """

        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message(
                f"Your top role `{interaction.user.top_role.name}` is lower or equal to {member}'s top role `{member.top_role.name}`"
            )

        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                f"My top role `{interaction.guild.me.top_role.name}` is lower or equal to {member}'s top role `{member.top_role.name}`"
            )

        if not member.is_timed_out():
            return await interaction.response.send_message(
                "> That member is not timed out!"
            )

        await member.edit(timed_out_until=None, reason=reason)

        await interaction.response.send_message(
            f"🔊 Ended timeout of `{member}`\n**Reason:** {reason}"
        )
        try:
            await member.send(
                f"**{interaction.guild.name}:** 🔊 Your timeout has been ended\n**Reason:** {reason}"
            )
        except:
            pass


async def setup(bot):
    await bot.add_cog(
        Timeout(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
