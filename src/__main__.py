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
import typing
from contextlib import redirect_stdout
from io import StringIO
from textwrap import indent
from timeit import default_timer

import discord
from discord import app_commands
from discord.ext.commands import BadArgument

from hyena import Bot

bot = Bot()  # dont pass in things here, pass in ./hyena.py


@bot.tree.error
async def app_command_error(
    interaction: discord.Interaction,
    # command: typing.Union[
    #     discord.app_commands.Command, discord.app_commands.ContextMenu
    # ],
    error: discord.app_commands.AppCommandError,
):
    """Slash commands error handler"""
    error = getattr(error, "original", error)

    # if isinstance(error, bot.checks.CheckFailed):
    #     await interaction.response.send_message(str(error))

    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            f"> You are missing `{', '.join(error.missing_permissions)}` permission(s) to run this command"
        )

    elif isinstance(error, app_commands.errors.CommandOnCooldown):
        await interaction.response.send_message("> " + str(error))

    elif isinstance(error, BadArgument):
        await interaction.response.send_message("> " + str(error))

    else:
        embed = discord.Embed(
            title="Error",
            description="An unknown error has occurred and my developer has been notified of it.",
            color=discord.Color.red(),
        )
        with contextlib.suppress(discord.NotFound, discord.Forbidden):
            try:
                await interaction.response.send_message(embed=embed)
            except:
                pass

        traceback_embeds = bot.tools.error_to_embed(bot, error)

        info_embed = discord.Embed(
            title="Message content",
            description="```\n"
            + discord.utils.escape_markdown(interaction.command.name)
            + "\n```",
            color=discord.Color.red(),
        )

        value = (
            (
                "**Name**: {0.name}\n"
                "**ID**: {0.id}\n"
                "**Created**: {0.created_at}\n"
                "**Joined**: {0.me.joined_at}\n"
                "**Member count**: {0.member_count}\n"
                "**Permission integer**: {0.me.guild_permissions.value}"
            ).format(interaction.guild)
            if interaction.guild
            else "None"
        )

        info_embed.add_field(name="Guild", value=value)
        if isinstance(interaction.channel, discord.TextChannel):
            value = (
                "**Type**: TextChannel\n"
                "**Name**: {0.name}\n"
                "**ID**: {0.id}\n"
                "**Created**: {0.created_at}\n"
                "**Permission integer**: {1}\n"
            ).format(
                interaction.channel,
                interaction.channel.permissions_for(interaction.guild.me).value,
            )
        else:
            value = (
                "**Type**: DM\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
            ).format(interaction.channel)

        info_embed.add_field(name="Channel", value=value)

        # User info
        value = (
            "**Name**: {0}\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
        ).format(interaction.user)

        info_embed.add_field(name="User", value=value)

        await bot.console.send(embeds=[*traceback_embeds, info_embed])


@bot.command(name="load")
async def load(ctx, cog):
    """Load a given cog"""
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "load")
    bot.logger.info(f"Loaded {cog}")


@bot.command(name="unload")
async def unload(ctx, cog):
    """Unload a given cog"""
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "unload")
    bot.logger.info(f"Unloaded {cog}")


@bot.command(name="reload")
async def reload(ctx, cog):
    """Reload a given cog"""
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "reload")
    bot.logger.info(f"Reloaded {cog}")


@bot.command(name="sync")
async def _sync(ctx):
    """sync all the slash commands"""
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.tree.sync(guild=discord.Object(bot.config["bot_config"]["guild_id"]))
    await ctx.message.add_reaction(bot.success_emoji)
    print("Synced slash commands, requested by", str(ctx.author))


def cleanup_code(content):
    """Cleanup code blocks"""
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    return content.strip("` \n")


@bot.command(name="eval")
async def eval_command(ctx, *, code='await ctx.send("Hello World")'):
    """Evaluate a given code"""
    if ctx.author.id in bot.owner_ids:
        embed = discord.Embed(color=discord.Colour.green())
        embed.set_author(
            name="Evaluate code", icon_url=bot.tools._get_mem_avatar(bot.user)
        )

        start = default_timer()
        code = cleanup_code(code)
        code = f"async def code():\n{indent(code, '    ')}"
        _global_vars = {"bot": bot, "ctx": ctx, "discord": discord}
        buf = StringIO()

        try:
            exec(code, _global_vars)
        except Exception as e:
            embed.description = f"```py\n{e.__class__.__name__}: {e}\n```"
            embed.color = discord.Colour.red()
        else:
            func = _global_vars["code"]
            try:
                with redirect_stdout(buf):
                    resp = await func()
            except Exception as e:
                console = buf.getvalue()
                embed.description = f"```py\n{console}{traceback.format_exc()}\n```"
                embed.color = discord.Colour.red()
            else:
                console = buf.getvalue()
                if not resp and console:
                    embed.description = f"```py\n{console}\n```"
                elif not resp and not console:
                    embed.description = "```<No output>```"
                else:
                    embed.description = f"```py\n{console}{resp}\n```"
        stop = default_timer()

        embed.set_footer(
            text="Evaluated in: {:.5f} seconds".format(stop - start),
            icon_url=bot.tools._get_mem_avatar(ctx.author),
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, this is a Developer only command!")


if __name__ == "__main__":
    bot.run()
