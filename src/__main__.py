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

import discord
from discord import app_commands
from discord.ext.commands import BadArgument

from hyena import Bot

bot = Bot()  # dont pass in things here, pass in ./hyena.py


@bot.tree.error
async def app_command_error(
    interaction: discord.Interaction,
    command: typing.Union[
        discord.app_commands.Command, discord.app_commands.ContextMenu
    ],
    error: discord.app_commands.AppCommandError,
):
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
        bot.logger.error(str(error))
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

        traceback_embeds = bot.tools.error_to_embed(error)

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
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "load")
    bot.logger.info(f"Loaded {cog}")


@bot.command(name="unload")
async def unload(ctx, cog):
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "unload")
    bot.logger.info(f"Unloaded {cog}")


@bot.command(name="reload")
async def reload(ctx, cog):
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "reload")
    bot.logger.info(f"Reloaded {cog}")


@bot.command(name="sync")
async def _sync(ctx):
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.tree.sync(guild=discord.Object(bot.config["bot_config"]["guild_id"]))
    await ctx.message.add_reaction(bot.success_emoji)
    print("Synced slash commands, requested by", str(ctx.author))


@bot.command(name="eval")
async def eval_command(ctx, *, code='await ctx.send("Hello World")'):
    if ctx.author.id in bot.owner_ids:
        try:
            code = code.strip("`")
            code = code.strip("py")
            code = code.split("\n")

            if len(code) > 1:
                code_to_process = code[1:-1]
                code = code_to_process

            with open("eval_command.py", "w") as file:
                file.writelines(
                    """import asyncio, discord
async def code(ctx, bot): \n"""
                )

            with open("eval_command.py", "a") as file:
                for line in code:
                    file.writelines("   " + line + "\n")

            import importlib

            import eval_command

            importlib.reload(eval_command)
            await eval_command.code(ctx, bot)
        except Exception as e:
            embed = discord.Embed(
                title="Error Occurred in eval.", color=discord.Colour.red()
            )
            embed.description = f"""
```py
{traceback.format_exc()}
```
"""
            await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, this is a Developer only command!")


if __name__ == "__main__":
    bot.run()
