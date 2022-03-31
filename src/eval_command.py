import asyncio

import discord


async def code(ctx, bot):
    mem = ctx.guild.get_member(748940917305770114)
    await ctx.send(bot.tools._get_mem_avatar(mem))
