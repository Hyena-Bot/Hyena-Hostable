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


from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class ImageGen(commands.Cog):
    """Cog for manipulating user images."""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.sra = self.bot.SRA(self.bot)
        self.category = ["fun"]

    # ------------------- SRA image gen cmds go below -------------------

    image_gen = app_commands.Group(
        name="image",
        description="Want to edit someones avatar through discord? this is it.",
    )

    @image_gen.command(
        name="wasted", description="Create a GTA inspired wasted image of the user."
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        member="The member whose image to edit, defaults to the cmd invoker."
    )
    async def _wasted(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """Manipulate the given users pfp via various api's."""
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_image_for(
            member=member, endpoint="wasted", name="gta_wasted"
        )

        file: discord.File = data[0]

        embed: discord.Embed = data[1]
        embed.title = "Wasted"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)

    @image_gen.command(
        name="passed",
        description="Create a GTA inspired mission passed image of the user.",
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        member="The member whose image to edit, defaults to the cmd invoker."
    )
    async def _passed(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """Manipulate the given users pfp via various api's."""
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_image_for(
            member=member, endpoint="passed", name="gta_passed"
        )

        file: discord.File = data[0]

        embed: discord.Embed = data[1]
        embed.title = "Passed"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(
        ImageGen(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
