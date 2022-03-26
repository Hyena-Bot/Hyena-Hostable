import asyncio

import discord


async def code(ctx, bot):
    await ctx.send(bot._get_total_commands(bot))
