import asyncio

import discord


async def code(ctx, bot):
    print(bot.get_channel(bot.config["bot_config"]["mod_action_logs_channel"]))
