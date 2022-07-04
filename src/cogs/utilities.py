import os
import platform
import time

import discord
import psutil
from discord import app_commands
from discord.ext import commands


class Utilities(commands.Cog):
    """Utilities manager cog"""

    def __init__(self, bot):
        self.bot = bot
        self.category = ["utilities"]

    @app_commands.command(
        name="server-info", description="All the information about the guild."
    )
    @app_commands.checks.cooldown(1, 3)
    async def _server_info(self, interaction: discord.Interaction):
        """
        **Description:**
        All the information about the guild.

        **Args:**
        • None

        **Syntax:**
        ```
        /server-info
        ```
        """
        embed = discord.Embed(
            color=self.bot._gen_colors(),
            timestamp=interaction.created_at,
            description=(interaction.guild.description or "Guild has no description"),
        )
        embed.set_thumbnail(url=self.bot.tools._get_guild_icon(interaction))
        embed.set_author(name=interaction.guild.name)
        embed.add_field(
            name="Owner",
            value=f"{interaction.guild.owner} ( {interaction.guild.owner.id} )",
            # inline=False,
        )
        embed.add_field(
            name="Verification level",
            value=str(interaction.guild.verification_level).title(),
            # inline=False,
        )
        embed.add_field(
            name="Members",
            value=f"""
Total members: {interaction.guild.member_count};
Humans: {len([m for m in interaction.guild.members if not m.bot])}
Bots: {len([m for m in interaction.guild.members if m.bot])}
""",
            # inline=False,
        )
        embed.add_field(
            name="Icon Url",
            value=f"[PNG]({interaction.guild.icon.with_format('png')}), \
[JPG]({interaction.guild.icon.with_format('jpg')})",
            # inline=False,
        )
        if interaction.guild.banner:
            embed.set_image(url=interaction.guild.banner.url)
        if interaction.guild.splash:
            embed.add_field(
                name="Invite splash",
                value=interaction.guild.splash.url,  # inline=False
            )
        if interaction.guild.rules_channel:
            embed.add_field(
                name="Rules channel",
                value=interaction.guild.rules_channel.mention,
                # inline=False,
            )
        embed.add_field(
            name="Channels",
            value=f"""
Total channels: {len(interaction.guild.text_channels)+len(interaction.guild.voice_channels)+len(interaction.guild.stage_channels)}
• Text Channels: {len(interaction.guild.text_channels)}
• Voice channels: {len(interaction.guild.voice_channels)}
• Stage Channels: {len(interaction.guild.stage_channels)}
""",
        )
        embed.add_field(
            name="Boosts",
            value=f"""
Booster role: {interaction.guild.premium_subscriber_role or 'No booster role'}
Boosts: {interaction.guild.premium_subscription_count if interaction.guild.premium_subscription_count != 0 else "No boosts"}
Boost level: {'Level '+str(interaction.guild.premium_tier) if interaction.guild.premium_tier != 0 else "No boosts"}
""",
            # inline=False,
        )
        embed.add_field(
            name="Roles",
            value=f"""
Total roles: {len(interaction.guild.roles)-1}
Bot Roles: {len([r for r in interaction.guild.roles if r.is_bot_managed()])}
""",
        )
        embed.add_field(
            name="Emojis",
            value=f"Limit: {interaction.guild.emoji_limit*2}\nNo. of emojis: {len(interaction.guild.emojis)}",
            # inline=False,
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="user-info", description="All the information about a user."
    )
    @app_commands.checks.cooldown(1, 3)
    @app_commands.describe(member="The target user")
    async def _user_info(
        self, interaction: discord.Interaction, member: discord.Member = None
    ):
        """
        **Description:**
        All the information about a user.

        **Args:**
        • [member] - The target user

        **Syntax:**
        ```
        /user-info [member]
        ```
        """
        if not member:
            member = interaction.user

        roles = [
            role.mention
            for role in member.roles
            if role != interaction.guild.default_role
        ]
        roles = " ".join(roles)

        key_perms = [
            "administrator",
            "manage_guild",
            "manage_roles",
            "manage_channels",
            "manage_messages",
            "manage_webhooks",
            "manage_emojis_and_stickers",
            "kick_members",
            "ban_members",
            "mention_everyone",
            "manage_threads",
            "moderate_members",
            "priority_speaker",
        ]
        user_key_perms = []
        has_key_perms = True

        for perm in key_perms:
            if getattr(member.guild_permissions, perm):
                user_key_perms.append(" ".join([x.title() for x in perm.split("_")]))

        if not user_key_perms:
            has_key_perms = False
        else:
            user_key_perms = ", ".join(user_key_perms)

        embed = discord.Embed(
            title="User information",
            color=self.bot._gen_colors(),
            timestamp=interaction.created_at,
        )
        embed.set_author(name=member, icon_url=member.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}", icon_url=member.avatar.url)

        embed.add_field(
            name="**Created at: **",
            value=member.created_at.strftime("%d/%m/%Y %H:%M:%S")
            + f"\n (<t:{int(member.created_at.timestamp())}:R>)",
        )
        embed.add_field(
            name="**Joined at: **",
            value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S")
            + f"\n (<t:{int(member.joined_at.timestamp())}:R>)",
        )
        embed.add_field(
            name=f"Roles [{len(member.roles) - 1}]", value=roles, inline=False
        )
        if has_key_perms:
            embed.add_field(name=f"Key Permissions", value=user_key_perms, inline=False)

        has_an_ack = False
        if member.guild_permissions.manage_messages:
            ack = "Server Moderator"
            has_an_ack = True
        if member.guild_permissions.administrator:
            ack = "Server Administrator"
            has_an_ack = True
        if member.id == interaction.guild.owner.id:
            ack = "Server owner"
            has_an_ack = True

        if has_an_ack:
            embed.add_field(name=f"Server Acknowledgements", value=ack, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bot-info", description="Check the stats of the bot!")
    @app_commands.checks.cooldown(1, 3)
    async def _bot_info(self, interaction: discord.Interaction):
        """
        **Description:**
        Check the stats of the bot!

        **Args:**
        • None

        **Syntax:**
        ```
        /bot-info
        ```
        """
        embed = discord.Embed(
            color=self.bot._gen_colors(),
            timestamp=interaction.created_at,
        )
        embed.set_author(
            name=f"Hello there, I am {self.bot.config['bot_config']['bot_name']}",
            icon_url=self.bot.tools._get_mem_avatar(self.bot.user),
        )
        embed.set_thumbnail(url=self.bot.tools._get_mem_avatar(self.bot.user))

        os_name = "Not recognized"
        kernel = platform.system()

        if kernel == "Windows":
            os_name = "Windows " + platform.release()
        if kernel == "Darwin":
            _raw_release = os.popen("/usr/bin/sw_vers").read().split("\n")
            release = {}
            for inf in _raw_release:
                inf = inf.split(":")
                try:
                    release[inf[0]] = inf[1].strip()
                except IndexError:
                    pass

            os_name = "MacOS " + str(release.get("ProductVersion"))
        if kernel == "Linux":
            os_name = (
                os.popen("grep '^NAME' /etc/os-release").read().replace("NAME=", "")
            )

        embed.description = f"""
> **What is Hyena?** ```{self.bot.config['bot_config']['bot_description']}```
> **Hyena Version:** `{self.bot.config['bot_config']['bot_version']}`
> **Total Users:** `{len(self.bot.users)}`
> **Guild Prefix:** `{self.bot.config['bot_config']['bot_prefix']}`
> **Owners:** `{", ".join([str(self.bot.get_user(x)) for x in self.bot.owner_ids])}`
```yaml
Ram Usage: {psutil.virtual_memory().used / 1_000_000} / {psutil.virtual_memory().total / 1_000_000}
Cpu Usage: {psutil.cpu_percent()}%
Discord.py Version: {discord.__version__}
Kernel: {kernel}
Kernel Version: {platform.version()}
OS Name: {os_name}
Python Version: Python {platform.python_version()}
```
"""

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="slowmode", description="Set the slow mode delay for a specific channel"
    )
    @app_commands.checks.cooldown(1, 5)
    @app_commands.describe(
        time="The delay with proper units, s|m|h ['remove' to remove slowmode]",
        channel="The channel to set slowmode",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def _slowmode(
        self,
        interaction: discord.Interaction,
        time: str,
        channel: discord.TextChannel = None,
    ):
        """
        **Description:**
        Set the slow mode delay for a specific channel

        **Args:**
        • <time> - The delay with proper units, s|m|h ['remove' to remove slowmode]
        • [channel] - The channel to set slowmode

        **Syntax:**
        ```
        /slowmode <time> [channel]
        ```
        """
        if not channel:
            channel = interaction.channel

        if time in ["reset", "remove"]:
            time = "0s"

        _seconds = int(self.bot.tools.convert_time(time).total_seconds())

        if _seconds > 21600:
            return await interaction.response.send_message(
                "Time cannot be greater than 6 hours you fool :|"
            )

        await channel.edit(slowmode_delay=_seconds)
        if _seconds == 0:
            desc = f"Successfully removed {channel.mention}'s slowmode!"
        else:
            desc = f"Successfully set {channel.mention}'s slowmode to `{_seconds}` seconds!"
        await interaction.response.send_message(desc)

    @app_commands.command(name="ping", description="Check the ping of the bot.")
    @app_commands.checks.cooldown(1, 3)
    async def _ping(self, interaction: discord.Interaction):
        """
        **Description:**
        Check the ping of the bot.

        **Args:**
        • None

        **Syntax:**
        ```
        /ping
        ```
        """
        start = time.perf_counter()
        await interaction.response.send_message("🏓 Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await interaction.edit_original_message(
            content="**🏓 Pong!**\n```yaml\nMessage: {:.2f}ms\nWebsocket: {:.2f}ms```".format(
                duration, self.bot.latency * 1000
            )
        )


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(
        Utilities(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
