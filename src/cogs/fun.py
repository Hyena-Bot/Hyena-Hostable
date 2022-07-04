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


import re

import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
    """Cog full of commands to entertain your community."""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.sra = self.bot.SRA(self.bot)
        self.category = ["fun"]

    # ---------------------------- General Fun cmds go below ------------------------------------

    @app_commands.command(name="pokedex", description="The official pokedex.")
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(pokemon="The pokemon whose data to show.")
    async def _pokedex(self, interaction: discord.Interaction, pokemon: str) -> None:
        """
        **Description:**
        Gets the info the given pokemon from the pokedex.

        **Args:**
        • `<pokemon>` - The pokemon name

        **Syntax:**
        ```
        /pokedex <pokemon>
        ```
        """
        results = await self.sra.get_data_for(
            f"https://some-random-api.ml/pokedex?pokemon={pokemon}", name="pokemon"
        )
        if results:
            if results.get("error") is not None:
                await interaction.response.send_message(results.get("error"))
                return
            else:
                # data
                name = results.get("name")
                desc = results.get("description")
                poke_type = results.get("type")  # list
                ht = results.get("height")
                weight = results.get("weight")
                _id = results.get("id")
                ability = results.get("abilities")
                eggs = results.get("egg_groups")
                stats = results.get("stats")
                url = (
                    f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/{_id}.png"
                )

                # embed
                embed = discord.Embed(color=discord.Color.random())
                embed.title = str(name).title()
                embed.description = str(desc)

                embed.add_field(name="Weight", value=str(weight), inline=True)
                embed.add_field(name="Height", value=str(ht), inline=True)
                embed.add_field(
                    name="Ability" if len(ability) == 1 else "Abilities",
                    value=", ".join(ability),
                    inline=True,
                )
                embed.add_field(
                    name="Stats",
                    value=f"Hp: {stats['hp']}\nAttack: {stats['attack']}\nDefense: {stats['defense']}",
                    inline=True,
                )
                embed.add_field(name="Type", value=", ".join(poke_type), inline=True)
                embed.add_field(
                    name="Egg" if len(eggs) == 1 else "Eggs",
                    value=", ".join(eggs),
                    inline=True,
                )

                embed.set_thumbnail(url=url)
                embed.set_footer(text=f"ID: {str(_id)}")

                await interaction.response.send_message(embed=embed)
                return

        else:
            await interaction.response.send_message(
                f"Could not fetch the results for `{pokemon}`, try again later."
            )

    @app_commands.command(
        name="animal-facts",
        description="Shows facts about animals with an image as well.",
    )
    @app_commands.choices(
        animal=[
            app_commands.Choice(name="panda", value="panda"),
            app_commands.Choice(name="fox", value="fox"),
            app_commands.Choice(name="cat", value="cat"),
            app_commands.Choice(name="bird", value="bird"),
            app_commands.Choice(name="koala", value="koala"),
        ]
    )
    @app_commands.describe(animal="The animal to view facts about")
    @app_commands.checks.cooldown(2, 5, key=lambda i: (i.guild_id, i.user.id))
    async def _fact(self, interaction: discord.Interaction, animal: str) -> None:
        """
        **Description:**
        Shows facts about animals with an image as well.

        **Args:**
        • `<animal>` - The animal [panda|fox|cat|bird|koala]

        **Syntax:**
        ```
        /animal-fact <animal panda|fox|cat|bird|koala>
        ```
        """
        _paths = {"panda": "red_panda", "bird": "birb"}

        name = f"{animal.title()} facts"
        results = await self.sra.get_data_for(
            f"https://some-random-api.ml/animal/{_paths.get(animal) or animal}",
            name=name,
        )

        if results:
            if results.get("error") is not None:
                return await interaction.response.send_message(results.get("error"))
            else:
                fact = results.get("fact")
                img_url = results.get("image")

                embed = discord.Embed(color=discord.Color.random())
                embed.title = name.title()
                embed.description = fact

                embed.set_image(url=img_url)

                return await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"Could not fetch the results for `{name}`, try again later."
            )

    @app_commands.command(name="embed", description="Generate an embed.")
    @app_commands.describe(
        title="Title of the embed",
        description="Description of the embed",
        color="Color in hex or defaults eg. '#FFFFFF' or 'white'",
        footer="Footer for the embed.",
        image_url="URL for a thumbnail.",
    )
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def _embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: str = None,
        footer: str = None,
        image_url: str = None,
    ):
        """
        **Description:**
        Generate an embed.

        **Args:**
        • `<title>` - Title of the embed
        • `<description>` - Description of the embed
        • `[color]` - Color in hex or defaults eg. '#FFFFFF' or 'white'
        • `[footer]` - Footer for the embed.
        • `[image_url]` - URL for a thumbnail.

        **Syntax:**
        ```
        /embed <title> <description> [color] [footer] [image_url]
        ```
        """
        embed = discord.Embed(title=title, description=description)
        if footer:
            embed.set_footer(text=footer)
        if image_url:
            embed.set_thumbnail(url=image_url)
        if color:
            if color[0] == "#":
                color = color.replace("#", "0x")
            try:
                color = int(color, 16)
            except ValueError as e:
                basic_colors = {
                    "blue": 0x0000FF,
                    "pink": 0xFFB6C1,
                    "purple": 0x800080,
                    "green": 0x00FF00,
                    "white": 0xFFFFFF,
                    "black": 0x000000,
                    "grey": 0x797373,
                    "red": 0xFF0000,
                }

                _color = basic_colors.get(color)
                if _color:
                    color = _color
                else:
                    return await interaction.response.send_message(
                        (
                            f"Your color `{color}` is not a valid hex code or a basic color.\n"
                            "Example of a valid hex code: `#FFFFFF`, `#000000`\n"
                            "Basic colors:\n`blue`, `pink`\n`purple`, `green`\n`white`, `black`\n`grey`, `red`"
                        )
                    )

        embed.color = color or self.bot._gen_colors()
        try:
            await interaction.response.send_message("Creating!")
            await interaction.delete_original_message()
            await interaction.channel.send(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    title=" ".join(
                        re.compile(r"[A-Z][a-z]*").findall(e.__class__.__name__)
                    ),
                    description=str(e),
                )
            )

    @app_commands.command(
        name="reply", description="Reply to a specific message using me."
    )
    @app_commands.checks.cooldown(1, 3, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        message_id="The message ID to reply to.", message="The reply"
    )
    async def _reply(
        self, interaction: discord.Interaction, message_id: str, message: str
    ):
        """
        **Description:**
        Reply to a specific message using me.

        **Args:**
        • `<message_id>` - The message ID to reply to.
        • `<message>` - The Reply

        **Syntax:**
        ```
        /reply <message_id> <message>
        ```
        """
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
        except (discord.errors.NotFound, ValueError):
            return await interaction.response.send_message(
                "Can't find your referenced message, use a correct ID."
            )

        await interaction.response.send_message("Okay!")
        await interaction.delete_original_message()
        await msg.reply(
            message, allowed_mentions=discord.AllowedMentions(replied_user=False)
        )


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(
        Fun(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
