import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class Afk(commands.Cog):
    """Away from Keyboard manager cog"""

    def __init__(self, bot):
        self.bot = bot
        self._afk = {}
        self.category = ["utilities"]

    # @property
    # def category():
    #     return ["utilities"]

    @app_commands.command(
        name="afk",
        description="Set an AFK status to display when you are mentioned",
    )
    @app_commands.describe(reason="The AFK status")
    @app_commands.checks.cooldown(1, 5)
    async def _afk_command(
        self, interaction: discord.Interaction, reason: Optional[str] = "AFK"
    ):
        """
        **Description:**
        Set an AFK status to display when you are mentioned
        * you'll not be unafked with you start your message with `don't unafk`

        **Args:**
        • `reason` - The AFK status

        **Syntax:**
        ```
        /afk [reason]
        ```
        """

        self._afk[interaction.user.id] = [reason, time.time()]
        await interaction.response.send_message(
            f"{interaction.user.mention} I set your AFK: {reason}"
        )

        nick = interaction.user.display_name
        nick = nick[:24] + ".." if len(str(nick)) > 26 else nick

        try:
            if not "[AFK] " in str(interaction.user.display_name):
                await interaction.user.edit(nick=f"[AFK] {nick}")
        except:
            pass

    async def _remove_afk(self, message):
        if (
            list(
                filter(
                    message.content.lower().startswith,
                    [
                        "no unafk",
                        "do not unafk",
                        "don't unafk",
                    ],
                )
            )
            != []
        ):
            return

        if _data := self._afk.get(message.author.id):
            if time.time() - _data[1] < 10:
                # await message.channel.send(
                #     f"{message.author.mention}, A little too quick there!",
                #     delete_after=3,
                # )
                return
            self._afk.pop(message.author.id)

        await message.reply(f"Welcome back `{message.author}`")
        if message.author.display_name.startswith("[AFK]"):
            try:
                await message.author.edit(nick=message.author.display_name[6:])
            except:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot:
            return

        mentions = message.mentions

        if message.author.id in self._afk:
            return await self._remove_afk(message)

        if len(mentions) == 0:
            return
        for men in mentions:
            if men.id in self._afk:
                reason = "AFK"
                timestamp = None
                if _data := self._afk.get(men.id):
                    reason = _data[0]
                    timestamp = _data[1]
                await message.reply(
                    f"`{men}` is AFK: {reason} - <t:{int(timestamp)}:R>"
                )
                break


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(
        Afk(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
