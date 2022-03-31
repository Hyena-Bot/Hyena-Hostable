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


import asyncio
import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    @app_commands.checks.cooldown(1, 5)
    @app_commands.checks.has_permissions(ban_members=True)
    async def _ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        delete_message: app_commands.Choice[int],
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        Ban a user from the server.

        **Args:**
        • `<member>` - The member to ban
        • `<delete_message>` - How much of their message history to delete [0|1|7]
        • `[reason]` - The reason to ban the member

        **Syntax:**
        ```
        /ban <member> <delete_message - 0|1|7> [reason]
        ```
        """
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
        name="softban",
        description="Bans and immediately unbans a member to act as a purging kick.",
    )
    @app_commands.describe(
        member="The member to softban",
        delete_message="How much of their message history to delete",
        reason="The reason to softban the member",
    )
    @app_commands.choices(
        delete_message=[
            app_commands.Choice(name="Previous 24 hours", value=1),
            app_commands.Choice(name="Previous 7 days", value=7),
        ]
    )
    @app_commands.checks.cooldown(1, 5)
    @app_commands.checks.has_permissions(ban_members=True)
    async def _soft_ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        delete_message: app_commands.Choice[int],
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        Bans and immediately unbans a member to act as a purging kick.

        **Args:**
        • `<member>` - The member to softban
        • `<delete_message>` - How much of their message history to delete [1|7]
        • `[reason]` - The reason to softban the member

        **Syntax:**
        ```
        /softban <member> <delete_message - 1|7> [reason]
        ```
        """
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
                    f"**{interaction.guild.name}:** You have been 🔨 Softbanned (kicked) \n**Reason:** {reason}"
                )
            except:
                pass

            await member.ban(
                delete_message_days=delete_message.value,
                reason=f"Softbanned by: {interaction.user}, Reason: {reason}.",
            )
            await interaction.guild.unban(
                member, reason=f"Softbanned by: {interaction.user}, Reason: {reason}."
            )

            await interaction.response.send_message(
                f"🔨 Softbanned `{member}` \n**Reason:** {reason}"
            )
        else:
            if member == interaction.user:
                return await interaction.response.send_message(
                    "You can't softban yourself. 🤦🏻‍"
                )
            elif member.top_role > interaction.guild.me.top_role:
                return await interaction.response.send_message(
                    f"Hmmm, I do not have permission to softban {member}."
                )
            else:
                return await interaction.response.send_message(
                    "Error, this person has a higher or equal role to you"
                )

    @app_commands.command(name="kick", description="Kick someone out of the server!")
    @app_commands.describe(
        member="The member to kick",
        reason="The reason to kick the member",
    )
    @app_commands.checks.cooldown(1, 5)
    @app_commands.checks.has_permissions(kick_members=True)
    async def _kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        Kick someone out of the server!

        **Args:**
        • `<member>` - The member to kick
        • `[reason]` - The reason to kick the member

        **Syntax:**
        ```
        /kick <member> [reason]
        ```
        """
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
    @app_commands.checks.cooldown(1, 5)
    @app_commands.checks.has_permissions(ban_members=True)
    async def _unban(
        self,
        interaction: discord.Interaction,
        member: str,
        reason: Optional[str] = "Not provided",
    ):
        """
        **Description:**
        Revoke a user's man.

        **Args:**
        • `<member>` - The user to unban
        • `[reason]` - The reason to unban the member

        **Syntax:**
        ```
        /unban <member> [reason]
        ```
        """
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

        if success:
            # ... modlogs and others to be added later
            pass
        if not success:
            await interaction.response.send_message(
                f"Cannot Find `{member}`, \nNOTE: You can send both IDs and their proper names whichever you like the most :)"
            )

    @app_commands.command(name="purge", description="Clear messages from a channel")
    @app_commands.describe(
        amount="number of messages to purge, use [all | max] to clear maximum",
        member="the member whose messages to purge",
    )
    @app_commands.checks.cooldown(1, 3)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def _purge(
        self,
        interaction: discord.Interaction,
        amount: str,
        member: Optional[discord.Member] = None,
    ):
        """
        **Description:**
        Purge an amount of messages from a channel.

        **Args:**
        • `<amount>` - Number of messages to purge, use [all | max] to clear maximum
        • `[member]` - The member whose messages to purge

        **Syntax:**
        ```
        /purge <amount> [member]
        ```
        """
        await interaction.response.defer(thinking=True)
        hist_gen = interaction.channel.history(limit=2)
        hist = [m async for m in hist_gen]
        created_at = (
            datetime.datetime.now(datetime.timezone.utc) - hist[1].created_at
        ).days
        back = datetime.datetime.utcnow() - datetime.timedelta(days=14)

        if int(created_at) >= 14:
            return await interaction.followup.send(
                "Message is more than 2 weeks old! No messages were deleted :|"
            )

        if amount == "all" or amount == "max":
            amount = 1000

        try:
            amount = int(amount)
        except ValueError:
            return await interaction.followup.send(
                "Only `Integers (Numbers), all, nuke` will be accepted"
            )

        if amount > 1000:
            return await interaction.followup.send(
                "Smh so many messages :| Delete the channel instead dumb"
            )

        if member is not None:
            purged_messages = await interaction.channel.purge(
                limit=amount,
                after=back,
                check=lambda x: not x.pinned and x.author.id == member.id,
            )
            p = len(purged_messages)
            await interaction.channel.send(
                f"Successfully purged `{p}` messages from `{member.name}` in the last `{amount}` messages!",
                delete_after=2,
            )
        else:
            purged_messages = await interaction.channel.purge(
                limit=amount,
                after=back,
                check=lambda message_to_check: not message_to_check.pinned,
            )
            p = len(purged_messages)
            await interaction.channel.send(f"Purged `{p}` messages!", delete_after=2)

        await asyncio.sleep(2)

    @app_commands.command(
        name="nick", description="Change the nickname of a member/you"
    )
    @app_commands.describe(
        member="The member to rename", nickname="Reason for unbanning user"
    )
    @app_commands.checks.cooldown(1, 3)
    async def _nick(
        self, interaction, member: discord.Member, nickname: Optional[str] = None
    ):
        """
        **Description:**
        Change the nickname of a member/you.

        **Args:**
        • `<member>` - The member to rename
        • `[nickname]` - Reason for unbanning user

        **Syntax:**
        ```
        /nick <member> [nickname]
        ```
        """
        if nickname == None:
            nickname = member.name

        if interaction.user == member and member.guild_permissions.change_nickname:
            try:
                await member.edit(nick=nickname)
                return await interaction.response.send_message(
                    f"Changed {member.name}'s nickname to `{nickname}`"
                )
            except:
                return await interaction.response.send_message(
                    "Uh oh! Something went wrong, seems like the bot doesn't have the permissions"
                )

        if interaction.user == member and not member.guild_permissions.change_nickname:
            return await interaction.response.send_message(
                "> You are missing the `change_nicknames` permission(s)!"
            )

        if not interaction.user.guild_permissions.manage_nicknames:
            return await interaction.response.send_message(
                "> You are missing the `manage_nicknames` permission(s)!"
            )

        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(
                "You cannot do this action due to the role hierarchy"
            )

        try:
            await member.edit(nick=nickname)
        except:
            return await interaction.response.send_message(
                "Uh oh! Something went wrong, seems like the bot doesn't have the permissions"
            )
        await interaction.response.send_message(
            f"Changed {member.name}'s nickname to `{nickname}`"
        )

    @app_commands.command(
        name="lock", description="Lock a channel so that people can't talk in it"
    )
    @app_commands.checks.cooldown(1, 3)
    @app_commands.describe(channel="The channel to lock")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def _lock(self, interaction, channel: Optional[discord.TextChannel] = None):
        """
        **Description:**
        Lock a channel so that people can't talk in it.

        **Args:**
        • `[channel]` - The channel to lock

        **Syntax:**
        ```
        /lock [channel]
        ```
        """
        if channel is None:
            channel = interaction.channel

        try:
            await channel.set_permissions(
                interaction.guild.roles[0], send_messages=False
            )
            await interaction.response.send_message(
                f"🔒 The channel {channel.mention} has been locked"
            )
        except:
            return await interaction.response.send_message(
                "I dont seem to have the permissions to do this action!"
            )

        # modlogs ...

    @app_commands.command(
        name="unlock",
        description="Unlock channel to give access to the people to talk in the channel",
    )
    @app_commands.checks.cooldown(1, 3)
    @app_commands.describe(channel="The channel to unlock")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def _unlock(self, interaction, channel: Optional[discord.TextChannel] = None):
        """
        **Description:**
        Unlock channel to give access to the people to talk in the channel.

        **Args:**
        • `[channel]` - The channel to unlock

        **Syntax:**
        ```
        /unlock [channel]
        ```
        """
        if channel is None:
            channel = interaction.channel

        try:
            await channel.set_permissions(
                interaction.guild.roles[0], send_messages=True
            )
            await interaction.response.send_message(
                f"🔓 The channel {channel.mention} has been unlocked"
            )
        except:
            return await interaction.response.send_message(
                "I dont seem to have the permissions to do this action!"
            )


async def setup(bot):
    await bot.add_cog(
        Moderation(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
