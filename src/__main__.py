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

import traceback

import discord

from hyena import Bot

bot = Bot()  # dont pass in things here, pass in ./hyena.py


@bot.command(name="load")
async def load(ctx, cog):
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "load")


@bot.command(name="unload")
async def unload(ctx, cog):
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "unload")


@bot.command(name="reload")
async def reload(ctx, cog):
    if ctx.author.id not in bot.owner_ids:
        return await ctx.send("You are not the developer!")

    await bot.handle_cog_update(ctx, cog, "reload")


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
