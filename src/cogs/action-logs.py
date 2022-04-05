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

import json
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class ActionLogs(commands.Cog):
    """Moderation action logs cog"""

    def __init__(self, bot):
        self.bot = bot
        self._db = self.bot._action_logs_db

    def _format_log(self, guild: discord.Guild, _action: dict, serial: int) -> str:
        """Format a given log record"""
        moderator = guild.get_member(_action["moderator"])
        others = [
            f"{x.title()}: `{y}`"
            for x, y in _action.items()
            if x not in ["action", "reason", "moderator", "at"]
        ]
        _str = (
            f"#{serial + 1}: **{_action['action']}**: <t:{int(_action['at'])}:f> - By: `{moderator}` ({_action['moderator']})"
            f"\n> **Reason:** {_action['reason']}"
            f"\n> **Others:** {' '.join(others)}"
        )

        return _str

    @app_commands.command(
        name="actions", description="Check moderation actions for a given user"
    )
    @app_commands.describe(
        member="The member to check the moderation actions for", page="The page number"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 3)
    async def _action(self, interaction, member: discord.User, page: Optional[int] = 1):
        """
        **Description:**
        Check moderation actions for a given user.

        **Args:**
        • `<member>` - The member to check the moderation actions for
        • `[page]` - The page number

        **Syntax:**
        ```
        /actions <member> [page]
        ```
        """

        if page < 1:
            return await interaction.response.send_message(
                "Breh, input an integer [not less than 1]."
            )

        cursor = await self._db.execute(
            "SELECT * FROM moderation_actions WHERE user_id = ?", (member.id,)
        )
        res = await cursor.fetchone()
        if not res:
            await interaction.response.send_message(
                f"I couldn't find any moderation actions for `{member}`."
            )
        if res:
            res = json.loads(res[1])
            if not res:
                return await interaction.response.send_message(
                    f"I couldn't find any moderation actions for `{member}`."
                )

            chunks = (lambda lst, n: [lst[i : i + n] for i in range(0, len(lst), n)])(
                res, 5
            )

            try:
                req = chunks[page - 1]
            except IndexError:
                return await interaction.response.send_message(
                    "Bruv, that page does not exist moron."
                )

            _desc_list = []
            for action in req:
                _desc_list.append(
                    self._format_log(interaction.guild, action, res.index(action))
                )
            desc = "\n\n".join(_desc_list)

            embed = discord.Embed(
                color=self.bot._gen_colors(), timestamp=interaction.created_at
            )
            embed.set_author(
                name=f"LOGS | {member}", icon_url=self.bot.tools._get_mem_avatar(member)
            )
            embed.description = f"Total: {len(res)}\n\n{desc}"
            embed.set_footer(text=f"Page {page}/{len(chunks)}")

            await interaction.response.send_message(embed=embed)

        await cursor.close()

    @app_commands.command(
        name="actions-clear", description="Clears the action logs for the given member"
    )
    @app_commands.describe(member="The member to clear the moderation actions for")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.cooldown(1, 3)
    async def _actions_clear(self, interaction, member: discord.User):
        """
        **Description:**
        Clears the action logs for the given member

        **Args:**
        • `<member>` - The member to clear the moderation actions for

        **Syntax:**
        ```
        /actions-clear <member>
        ```
        """

        cursor = await self._db.execute(
            "SELECT * FROM moderation_actions WHERE user_id = ?", (member.id,)
        )
        res = await cursor.fetchone()
        if not res:
            return await interaction.response.send_message(
                f"I couldn't find any moderation actions for `{member}`."
            )
        if res:
            await self._db.execute(
                "DELETE FROM moderation_actions WHERE user_id = ?", (member.id,)
            )
            await interaction.response.send_message(
                f"Cleared all action logs for {member}. \n**Note:** For warns & some others it will \
not clear the actual warns, just the logs."
            )

        await self._db.commit()
        await cursor.close()


async def setup(bot):
    await bot.add_cog(
        ActionLogs(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
