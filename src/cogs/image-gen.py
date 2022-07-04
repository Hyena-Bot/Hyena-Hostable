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
        """
        **Description:**
        Create a GTA inspired wasted image of the user.

        **Args:**
        • `[member]` -The member whose image to edit, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image wasted [member]
        ```
        """
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
        """
        **Description:**
        Create a GTA inspired mission passed image of the user.

        **Args:**
        • `[member]` -The member whose image to edit, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image passed [member]
        ```
        """
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

    @image_gen.command(
        name="triggered",
        description="A triggered meme of the given user.",
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        member="The member whose image to edit, defaults to the cmd invoker."
    )
    async def _triggered(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """
        **Description:**
        A triggered meme of the given user

        **Args:**
        • `[member]` -The member whose image to edit, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image triggered [member]
        ```
        """
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_image_for(
            member=member, endpoint="triggered", name="triggered"
        )

        file: discord.File = data[0]

        embed: discord.Embed = data[1]
        embed.title = "Triggered"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)

    @image_gen.command(
        name="jail",
        description="Put a given user in jail.",
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        member="The member whose image to edit, defaults to the cmd invoker."
    )
    async def _jail(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """
        **Description:**
        Put a given user in jail.

        **Args:**
        • `[member]` -The member whose image to edit, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image jail [member]
        ```
        """
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_image_for(member=member, endpoint="jail", name="jail")

        file: discord.File = data[0]

        embed: discord.Embed = data[1]
        embed.title = f"Put {member.name} in jail!"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)

    @image_gen.command(
        name="comrade",
        description="Make someone join the soviet union.",
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        member="The member whose image to edit, defaults to the cmd invoker."
    )
    async def _comrade(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """
        **Description:**
        Make someone join the soviet union.

        **Args:**
        • `[member]` -The member whose image to edit, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image comrade [member]
        ```
        """
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_image_for(
            member=member, endpoint="comrade", name="comrade"
        )

        file: discord.File = data[0]

        embed: discord.Embed = data[1]
        embed.title = f"Посмотрите на нас, все возможно"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)

    @image_gen.command(
        name="pixelate",
        description="Pixels, Gotta love em'.",
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        member="The member whose image to edit, defaults to the cmd invoker."
    )
    async def _pixelate(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ) -> None:
        """
        **Description:**
        Pixels, Gotta love em'.

        **Args:**
        • `[member]` -The member whose image to edit, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image pixels [member]
        ```
        """
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_image_for(
            member=member, endpoint="pixelate", name="pixelate"
        )

        file: discord.File = data[0]

        embed: discord.Embed = data[1]
        embed.title = f"144p"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)

    @image_gen.command(
        name="youtube",
        description="Comment something on youtube?",
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        comment="The comment to print.",
        member="The member who sent the comment, defaults to the cmd invoker.",
    )
    async def _yt_comment(
        self,
        interaction: discord.Interaction,
        comment: str,
        member: Optional[discord.Member] = None,
    ) -> None:
        """
        **Description:**
        Comment something on youtube?

        **Args:**
        • `<comment>` - The comment to print.
        • `[member]` - The member who sent the comment, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image youtube <comment> [member]
        ```
        """
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_data_for(
            endpoint=f"youtube-comment?avatar={self.bot.tools._get_mem_avatar(member)}&username={member.name}&comment={comment}",
            name="yt",
        )

        file: discord.File = data

        embed = discord.Embed(color=member.color)
        embed.set_image(url=f"attachment://yt.png")
        embed.title = f"{member.name} Just commented"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)

    @image_gen.command(
        name="tweet",
        description="Tweet something?",
    )
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        tweet="The tweet to print.",
        display_name="Display name for your tweet.",
        member="The member who sent the tweet. defaults to the cmd invoker.",
    )
    async def _tweet(
        self,
        interaction: discord.Interaction,
        tweet: str,
        display_name: str = None,
        member: Optional[discord.Member] = None,
    ) -> None:
        """
        **Description:**
        Tweet something on twitter?

        **Args:**
        • `<tweet>` - The tweet to print.
        • `[display_name]` - Display name for your tweet.
        • `[member]` - The member who sent the comment, defaults to the cmd invoker.

        **Syntax:**
        ```
        /image tweet <tweet> [display_name [member]
        ```
        """
        await interaction.response.defer()
        if not member:
            member = interaction.user

        data = await self.sra.get_data_for(
            endpoint=f"tweet?avatar={self.bot.tools._get_mem_avatar(member)}&displayname={display_name or ('@' + member.name)}&username={member.name}&comment={tweet}",
            name="tweet",
        )

        file: discord.File = data

        embed = discord.Embed(color=member.color)
        embed.set_image(url=f"attachment://tweet.png")
        embed.title = f"{member.name} Just tweeted"

        embed.set_footer(text=f"Requested by: {interaction.user}")

        await interaction.followup.send(embed=embed, file=file)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(
        ImageGen(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
