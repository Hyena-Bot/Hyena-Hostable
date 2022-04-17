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
from random import choice
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class Timeout(commands.Cog):
    """Timeout (mute) cog"""

    def __init__(self, bot):
        self.bot = bot

    timeout = app_commands.Group(
        name="timeout", description="Controls for timing out a user"
    )

    @timeout.command(
        name="add",
        description="Timeout (Mute) a user so they cannot add reactions/speak/join voice channels.",
    )
    @app_commands.checks.cooldown(1, 3)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        member="The member to timeout/mute",
        time="how long to timeout the member [Max - 28 days] ex. /timeout add <user> 10 days 5 seconds",
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
        /timeout add <member> <time> [reason]
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

        # Action logs
        await self.bot._action_logger._send_embed(
            moderator=interaction.user,
            member=member,
            description=(
                f"**Action:** \nTimeout\n"
                f"**User:** \n`{member}`\n"
                f"**Moderator:** \n`{interaction.user}`\n"
                f"**Reason:** \n{reason}\n"
                f"**length:** \n{delta}\n"
            ),
            timestamp=interaction.created_at,
        )
        await self.bot._action_logger._log_action(
            {
                "user_id": member.id,
                "data": {
                    "action": "Timeout",
                    "reason": reason,
                    "moderator": interaction.user.id,
                    "delta": str(delta),
                    "at": discord.utils.utcnow().timestamp(),
                },
            }
        )

    @timeout.command(name="remove", description="End timeout (Mute) of a user.")
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
        /timeout remove <member> [reason]
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

        # Action logs
        await self.bot._action_logger._send_embed(
            moderator=interaction.user,
            member=member,
            description=(
                f"**Action:** \nTimeout remove\n"
                f"**User:** \n`{member}`\n"
                f"**Moderator:** \n`{interaction.user}`\n"
                f"**Reason:** \n{reason}\n"
            ),
            timestamp=interaction.created_at,
        )
        await self.bot._action_logger._log_action(
            {
                "user_id": member.id,
                "data": {
                    "action": "Timeout remove",
                    "reason": reason,
                    "moderator": interaction.user.id,
                    "at": discord.utils.utcnow().timestamp(),
                },
            }
        )

    @timeout.command(name="view", description="View all timed out users for the server")
    @app_commands.checks.cooldown(1, 3)
    @app_commands.checks.has_permissions(moderate_members=True)
    async def _view(self, interaction: discord.Interaction):
        """
        **Description:**
        View all timed out users for the server

        **Args:**
        • none

        **Syntax:**
        ```
        /timeout view
        ```
        """

        desc = []
        for user in interaction.guild.members:
            if user.is_timed_out():
                desc.append(
                    f"`{user}` : timed out until - `{user.timed_out_until.strftime('%d %b, %H:%M:%S')}`"
                )

        if not desc:
            return await interaction.response.send_message(
                "> There are no timed out members in the server!"
            )

        embed = discord.Embed(
            color=self.bot._gen_colors(), timestamp=interaction.created_at
        )
        embed.set_author(
            name="Timed out users", icon_url=self.bot.tools._get_guild_icon(interaction)
        )
        embed.description = "\n".join(desc)
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=self.bot.tools._get_mem_avatar(interaction.user),
        )

        await interaction.response.send_message(content="Here you go!", embed=embed)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(
        Timeout(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
