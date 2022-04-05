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

import contextlib
import traceback

import discord
from discord import app_commands
from discord.ext import commands


class CoreHandlers(commands.Cog):
    """Core handlers with basic events and commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)

        if isinstance(error, commands.errors.CommandNotFound):
            pass

        else:
            embed = discord.Embed(
                title="Error",
                description="An unknown error has occurred and my developer has been notified of it.",
                color=discord.Color.red(),
            )
            with contextlib.suppress(discord.NotFound, discord.Forbidden):
                await ctx.send(embed=embed)

            traceback_embeds = self.bot.tools.error_to_embed(self.bot, error)

            # Add message content
            info_embed = discord.Embed(
                title="Message content",
                description="```\n"
                + discord.utils.escape_markdown(ctx.message.content)
                + "\n```",
                color=discord.Color.red(),
            )
            # Guild information
            value = (
                (
                    "**Name**: {0.name}\n"
                    "**ID**: {0.id}\n"
                    "**Created**: {0.created_at}\n"
                    "**Joined**: {0.me.joined_at}\n"
                    "**Member count**: {0.member_count}\n"
                    "**Permission integer**: {0.me.guild_permissions.value}"
                ).format(ctx.guild)
                if ctx.guild
                else "None"
            )

            info_embed.add_field(name="Guild", value=value)
            if isinstance(ctx.channel, discord.TextChannel):
                value = (
                    "**Type**: TextChannel\n"
                    "**Name**: {0.name}\n"
                    "**ID**: {0.id}\n"
                    "**Created**: {0.created_at}\n"
                    "**Permission integer**: {1}\n"
                ).format(ctx.channel, ctx.channel.permissions_for(ctx.guild.me).value)
            else:
                value = (
                    "**Type**: DM\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
                ).format(ctx.channel)

            info_embed.add_field(name="Channel", value=value)

            # User info
            value = (
                "**Name**: {0}\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
            ).format(ctx.author)

            info_embed.add_field(name="User", value=value)

            await self.bot.console.send(embeds=[*traceback_embeds, info_embed])


async def setup(bot):
    await bot.add_cog(CoreHandlers(bot))
