from discord.ext import commands
from utils.embed_utils import success_embed

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        emb = success_embed(ctx.bot, title = "test")
        return await ctx.send("pong", embed = emb)

    # ...


async def setup(bot):
    await bot.add_cog(Moderation(bot))
