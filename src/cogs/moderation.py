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
#
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
<<<<<<< HEAD
from utils.embed_utils import success_embed
=======

from utils import checks

>>>>>>> f50b6f790b2229e63b8f41ce1b45a10d85f9c68d

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

<<<<<<< HEAD
    @commands.command(name="ping")
    async def ping(self, ctx):
        emb = success_embed(ctx.bot, title = "test")
        return await ctx.send("pong", embed = emb)
=======
    @app_commands.command(name="ban", description="Yeet someone out of the server!")
    @app_commands.describe(
        member="The member to ban",
        delete_message="How much of their message history to delete",
        reason="The reason to ban the member",
    )
    @app_commands.choices(
        delete_message=[
            app_commands.Choice(name="Don't delete any", value=0),
            app_commands.Choice(name="Previous 24 hours", value=1),
            app_commands.Choice(name="Previous 7 days", value=7),
        ]
    )
    @checks._has_interaction_permission(ban_members=True)
    async def _ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        delete_message: app_commands.Choice[int],
        reason: Optional[str] = "Not provided",
    ):
        if (
            (
                interaction.user.top_role > member.top_role
                or interaction.guild.owner == interaction.user
            )
            and member != interaction.user
            and member.top_role < interaction.guild.me.top_role
        ):
            try:
                await member.send(
                    f"**{interaction.guild.name}:** You have been 🔨 Banned \n**Reason:** {reason}"
                )
            except:
                pass

            await member.ban(
                delete_message_days=delete_message.value,
                reason=f"Banned by: {interaction.user}, Reason: {reason}.",
            )

            await interaction.response.send_message(
                f"🔨 Banned `{member}` \n**Reason:** {reason}"
            )
        else:
            if member == interaction.user:
                return await interaction.response.send_message(
                    "You can't ban yourself. 🤦🏻‍"
                )
            elif member.top_role > interaction.guild.me.top_role:
                return await interaction.response.send_message(
                    f"Hmmm, I do not have permission to ban {member}."
                )
            else:
                return await interaction.response.send_message(
                    "Error, this person has a higher or equal role to you"
                )

    @app_commands.command(
        name="kick", description="Kick someone out of the server temporarily!"
    )
    @app_commands.describe(
        member="The member to kick",
        reason="The reason to kick the member",
    )
    @checks._has_interaction_permission(kick_members=True)
    async def _kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "Not provided",
    ):
        if (
            (
                interaction.user.top_role > member.top_role
                or interaction.guild.owner == interaction.user
            )
            and member != interaction.user
            and member.top_role < interaction.guild.me.top_role
        ):
            try:
                await member.send(
                    f"**{interaction.guild.name}:** You have been 🦿 Kicked \n**Reason:** {reason}"
                )
            except:
                pass

            await member.kick(
                reason=f"Kicked by: {interaction.user}, Reason: {reason}."
            )
            await interaction.response.send_message(
                f"🦿 Kicked `{member}` \n**Reason:** {reason}"
            )
        else:
            if member == interaction.user:
                return await interaction.response.send_message(
                    "You can't kick yourself. 🤦🏻‍"
                )
            elif member.top_role > interaction.guild.me.top_role:
                return await interaction.response.send_message(
                    f"Hmmm, I do not have permission to kick {member}."
                )
            else:
                return await interaction.response.send_message(
                    "Error, this person has a higher or equal role to you"
                )

    @app_commands.command(name="unban", description="Revoke someone's ban")
    @app_commands.describe(
        member="The member to unban", reason="Reason for unbanning user"
    )
    @checks._has_interaction_permission(ban_members=True)
    async def _unban(
        self,
        interaction: discord.Interaction,
        member: str,
        reason: Optional[str] = "Not provided",
    ):
        member = str(member).strip()
        bans = await interaction.guild.bans()
        unbanned_user = None
        success = False

        if member.isnumeric():
            for ban_entry in bans:
                if ban_entry.user.id == int(member):
                    await interaction.response.send_message("Found ban entry :)")
                    await interaction.guild.unban(ban_entry.user)
                    await interaction.edit_original_message(
                        content=f"🔓 Unbanned `{ban_entry.user}` \n**Reason:** {reason}"
                    )
                    success = True
                    unbanned_user = ban_entry.user

        else:
            for ban_entry in bans:
                if str(ban_entry.user).lower() == member.lower():
                    await interaction.response.send_message("Found ban entry :)")
                    await interaction.guild.unban(ban_entry.user)
                    await interaction.edit_original_message(
                        content=f"🔓 Unbanned `{ban_entry.user}` \n**Reason:** {reason}"
                    )
                    success = True
                    unbanned_user = ban_entry.user
>>>>>>> f50b6f790b2229e63b8f41ce1b45a10d85f9c68d

        if success:
            # ... modlogs and others to be added later
            pass
        if not success:
            await interaction.response.send_message(
                f"Cannot Find `{member}`, \nNOTE: You can send both IDs and their proper names whichever you like the most :)"
            )


async def setup(bot):
    await bot.add_cog(
        Moderation(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
