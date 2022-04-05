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
import random
import string
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class Warnings(commands.Cog):
    """Warning systems"""
    def __init__(self, bot):
        self.bot = bot
        self._db = self.bot._warns_db

    # helper

    def _gen_id(self):
        """Generate a random warn indetifier"""
        return "".join(
            [
                random.choice(
                    [*string.ascii_letters, *string.digits, *string.hexdigits]
                )
                for i in range(10)
            ]
        )

    def _format_warning(self, guild: discord.Guild, warning: dict, serial: int) -> str:
        """Format the given warning record"""
        moderator = guild.get_member(warning["moderator"])
        _str = (
            f"#{serial + 1}: **{warning['id']}**: - By: `{moderator}` ({moderator.id})"
            f"\n> **Reason:** {warning['reason']}"
        )

        return _str

    # commands

    warning = app_commands.Group(name="warning", description="Warning parent group.")

    @warning.command(name="give", description="Give warning to a given user.")
    @app_commands.describe(
        member="The member to give the warning to", reason="The reason for the warning"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 3)
    async def _warn_give(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        Give warning to a given user

        **Args:**
        • `<member>` - The member to warn
        • `[reason]` - The reason for the warning

        **Syntax:**
        ```
        /warning give <member> [reason]
        ```
        """
        if interaction.user.top_role < member.top_role:
            return await interaction.response.send_message(
                "You cannot do this action due to role-hierchery."
            )

        if len(reason) > 150:
            return await interaction.response.send_message(
                "Reason cannot be more than 150 characters. Optimization issues."
            )

        cursor = await self._db.execute(
            "SELECT * FROM warns WHERE user_id = ?", (member.id,)
        )
        res = await cursor.fetchone()

        _id = self._gen_id()
        _ordinal = "1st"

        if not res:
            await self._db.execute(
                "INSERT INTO warns(user_id, warn_data) VALUES(?,?)",
                (
                    member.id,
                    json.dumps(
                        [
                            {
                                "reason": reason,
                                "id": _id,
                                "moderator": interaction.user.id,
                            }
                        ]
                    ),
                ),
            )
        if res:
            old = json.loads(res[1])
            old.append({"reason": reason, "id": _id, "moderator": interaction.user.id})
            new = json.dumps(old)
            _ordinal = (
                lambda n: "%d%s"
                % (
                    n,
                    {1: "st", 2: "nd", 3: "rd"}.get(
                        n % 100 if n % 100 < 20 else n % 10, "th"
                    ),
                )
            )(len(old))

            await self._db.execute(
                "UPDATE warns SET warn_data = ? WHERE user_id = ?", (new, member.id)
            )

        await self._db.commit()
        await cursor.close()

        try:
            await member.send(
                f"**{interaction.guild.name}:** You have been ⚠️ warned\n"
                f"**Reason:** {reason}\n"
                f"**Identifier:** {_id}"
            )
        except:
            pass

        await interaction.response.send_message(
            f"Successfully warned `{member}`, this is their {_ordinal} warning \n> **Reason:** {reason}\n> **ID:** {_id}"
        )
        await self.bot._action_logger._send_embed(
            moderator=interaction.user,
            member=member,
            description=(
                f"**Action:** \nWarn\n"
                f"**User:** \n`{member}`\n"
                f"**Moderator:** \n`{interaction.user}`\n"
                f"**Reason:** \n{reason}\n"
                f"**ID:** \n{_id}\n"
            ),
            timestamp=interaction.created_at,
        )
        await self.bot._action_logger._log_action(
            {
                "user_id": member.id,
                "data": {
                    "action": "Warn",
                    "reason": reason,
                    "moderator": interaction.user.id,
                    "ID": str(_id),
                    "at": discord.utils.utcnow().timestamp(),
                },
            }
        )

    @warning.command(name="remove", description="Remove a warning from a given user.")
    @app_commands.describe(
        member="The member to remove the warning from",
        indentifier="The ID of the warning, use view to find it out!",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 3)
    async def _warn_remove(self, interaction, member: discord.Member, indentifier: str):
        """
        **Description:**
        Remove a warning from a given user.

        **Args:**
        • `<member>` - The member to remove the warning from
        • `<indentifier>` - The ID of the warning, use view to find it out!

        **Syntax:**
        ```
        /warning remove <member> <indetifier>
        ```
        """
        if interaction.user.top_role < member.top_role:
            return await interaction.response.send_message(
                "You cannot do this action due to role-hierchery"
            )

        cursor = await self._db.execute(
            "SELECT * FROM warns WHERE user_id = ?", (member.id,)
        )
        res = await cursor.fetchone()

        if not res:
            return await interaction.response.send_message(
                "Brev, there are no current warnings for this user"
            )
        if res:
            warnings = json.loads(res[1])

            currwarn = None
            for warn in warnings:
                if warn.get("id") == indentifier:
                    currwarn = warn
                    break

            if not currwarn:
                return await interaction.response.send_message(
                    f"{member} has no warns with the ID `{indentifier}`\n**Note:** Capitalisation matters."
                )
            warnings.remove(currwarn)

            await self._db.execute(
                "UPDATE warns SET warn_data = ? WHERE user_id = ?",
                (json.dumps(warnings), member.id),
            )
            await interaction.response.send_message(
                f"Successfully revoked warn `{indentifier}` from `{member}`"
            )

        await self._db.commit()
        await cursor.close()

        try:
            await member.send(
                f"**{interaction.guild.name}:** Your warn `{indentifier}` has been removed\n"
                f"**Identifier:** {indentifier}"
            )
        except:
            pass

        await self.bot._action_logger._send_embed(
            moderator=interaction.user,
            member=member,
            description=(
                f"**Action:** \nWarn remove\n"
                f"**User:** \n`{member}`\n"
                f"**Moderator:** \n`{interaction.user}`\n"
                f"**ID:** \n{indentifier}\n"
            ),
            timestamp=interaction.created_at,
        )
        await self.bot._action_logger._log_action(
            {
                "user_id": member.id,
                "data": {
                    "action": "Revoke warn",
                    "reason": f"warning remove command by `{interaction.user}`",
                    "moderator": interaction.user.id,
                    "ID": str(indentifier),
                    "at": discord.utils.utcnow().timestamp(),
                },
            }
        )

    @warning.command(name="view", description="View the warnings of a given user.")
    @app_commands.describe(
        member="The member to view the warnings of", page="The page number"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 3)
    async def _warn_view(
        self, interaction, member: discord.Member, page: Optional[int] = 1
    ):
        """
        **Description:**
        View the warnings of a given user.

        **Args:**
        • `<member>` - The member to view the warnings of
        • `[page]` - The page number

        **Syntax:**
        ```
        /warning view <member> [page]
        ```
        """
        if page < 1:
            return await interaction.response.send_message(
                "Breh, input an integer [not less than 1]."
            )

        cursor = await self._db.execute(
            "SELECT * FROM warns WHERE user_id = ?", (member.id,)
        )
        res = await cursor.fetchone()

        if not res:
            return await interaction.response.send_message(
                "Brev, there are no current warnings for this user"
            )
        if res:
            warnings = json.loads(res[1])
            chunks = (lambda lst, n: [lst[i : i + n] for i in range(0, len(lst), n)])(
                warnings, 5
            )

            try:
                req = chunks[page - 1]
            except IndexError:
                return await interaction.response.send_message(
                    "Bruv, that page does not exist moron."
                )

            _desc_list = []
            for warning in req:
                _desc_list.append(
                    self._format_warning(
                        interaction.guild, warning, warnings.index(warning)
                    )
                )
            desc = "\n\n".join(_desc_list)

            embed = discord.Embed(
                color=self.bot._gen_colors(), timestamp=interaction.created_at
            )
            embed.set_author(
                name=f"WARNINGS | {member}",
                icon_url=self.bot.tools._get_mem_avatar(member),
            )
            embed.description = f"Total: {len(warnings)}\n\n{desc}"
            embed.set_footer(text=f"Page {page}/{len(chunks)}")

            await interaction.response.send_message(embed=embed)

        await cursor.close()

    @warning.command(
        name="remove-all", description="Remove all the warnings of a given user."
    )
    @app_commands.describe(
        member="The member to remove the warnings of",
        reason="The reason to remove all the warnings",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 3)
    async def _warn_view(
        self,
        interaction,
        member: discord.Member,
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        Remove all the warnings of a given user.

        **Args:**
        • `<member>` - The member to remove the warnings of
        • `[reason]` - The reason to remove all the warnings

        **Syntax:**
        ```
        /warning remove-all <member> [reason]
        ```
        """
        if interaction.user.top_role < member.top_role:
            return await interaction.response.send_message(
                "You cannot do this action due to role-hierchery"
            )
        cursor = await self._db.execute(
            "SELECT * FROM warns WHERE user_id = ?", (member.id,)
        )
        res = await cursor.fetchone()

        if not res:
            return await interaction.response.send_message(
                "Brev, there are no current warnings for this user"
            )
        if res:
            await self._db.execute("DELETE FROM warns WHERE user_id = ?", (member.id,))
            await interaction.response.send_message(
                f"Cleared all `({len(json.loads(res[1]))})` warnings for `{member}`"
            )

        await self._db.commit()
        await cursor.close()

        try:
            await member.send(
                f"**{interaction.guild.name}:** Your all warnings have been removed!\n"
                f"**Reason:** {reason}"
            )
        except:
            pass

        await self.bot._action_logger._send_embed(
            moderator=interaction.user,
            member=member,
            description=(
                f"**Action:** \nAll warnings removed\n"
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
                    "action": "All warnings removed",
                    "reason": reason,
                    "moderator": interaction.user.id,
                    "at": discord.utils.utcnow().timestamp(),
                },
            }
        )


async def setup(bot):
    await bot.add_cog(
        Warnings(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
