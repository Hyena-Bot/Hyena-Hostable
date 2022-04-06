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

from os import listdir, path, remove
from os.path import exists

import discord
from discord import app_commands, ui
from discord.ext import commands


class FileInput(ui.Modal):
    """The parent file input modal"""

    name = ui.TextInput(
        label="File name", placeholder="File name here...", max_length=20
    )
    text = ui.TextInput(
        label="File content",
        style=discord.TextStyle.paragraph,
        placeholder="Type your file content here...",
    )

    async def on_error(
        self, error: Exception, interaction: discord.Interaction
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
        raise error


class Create(FileInput, title="Create file..."):
    """Create file modal"""

    async def on_submit(self, interaction: discord.Interaction) -> None:
        with open("./assets/files/{}".format(self.name.value), "w") as f:
            f.write(self.text.value)
        file = discord.File(
            "./assets/files/{}".format(self.name.value), filename=self.name.value
        )
        await interaction.response.send_message("Here you go!", file=file)


class Edit(FileInput, title="Edit file..."):
    """Edit file modal"""

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not exists("./assets/files/{}".format(self.name.value)):
            return await interaction.response.send_message("This file does not exist!")

        with open("./assets/files/{}".format(self.name.value), "w") as f:
            f.write(self.text.value)
        file = discord.File(
            "./assets/files/{}".format(self.name.value), filename=self.name.value
        )
        await interaction.response.send_message("Edited the file for you!", file=file)


class Append(FileInput, title="Append to file..."):
    """Append to file modal"""

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not exists("./assets/files/{}".format(self.name.value)):
            return await interaction.response.send_message("This file does not exist!")

        with open("./assets/files/{}".format(self.name.value), "a") as f:
            f.write(self.text.value)
        file = discord.File(
            "./assets/files/{}".format(self.name.value), filename=self.name.value
        )
        await interaction.response.send_message("Append to file for you!", file=file)


delattr(FileInput, "text")


class Delete(FileInput, title="Delete a file..."):
    """Delete file modal"""

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not exists("./assets/files/{}".format(self.name.value)):
            return await interaction.response.send_message("This file does not exist!")

        remove("./assets/files/{}".format(self.name.value))
        await interaction.response.send_message(
            f"Deleted `{self.name.value}` successfully!"
        )


class View(FileInput, title="View a file..."):
    """View file modal"""

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not exists("./assets/files/{}".format(self.name.value)):
            return await interaction.response.send_message("This file does not exist!")

        file = discord.File(
            "./assets/files/{}".format(self.name.value), filename=self.name.value
        )
        await interaction.response.send_message("Here's the file!", file=file)


class FileSystem(commands.Cog):
    """Utilities cog"""

    def __init__(self, bot):
        self.bot = bot

    files = app_commands.Group(name="file", description="Make, edit and get files")

    @files.command(name="create", description="Create a new file")
    @app_commands.checks.cooldown(1, 5)
    async def _create_file(self, interaction: discord.Interaction):
        """
        **Description:**
        Create a new file

        **Args:**
        • None

        **Syntax:**
        ```
        /file create
        ```
        """
        await interaction.response.send_modal(Create())

    @files.command(name="edit", description="Edit an already existing file")
    @app_commands.checks.cooldown(1, 5)
    async def _create_file(self, interaction: discord.Interaction):
        """
        **Description:**
        Edit an already existing file

        **Args:**
        • None

        **Syntax:**
        ```
        /file edit
        ```
        """
        await interaction.response.send_modal(Edit())

    @files.command(
        name="append", description="Append (add) to an already existing file"
    )
    @app_commands.checks.cooldown(1, 5)
    async def _append_file(self, interaction: discord.Interaction):
        """
        **Description:**
        Append (add) to an already existing file

        **Args:**
        • None

        **Syntax:**
        ```
        /file append
        ```
        """
        await interaction.response.send_modal(Append())

    @files.command(name="delete", description="Delete an existing file")
    @app_commands.checks.cooldown(1, 5)
    async def _delete_file(self, interaction: discord.Interaction):
        """
        **Description:**
        Delete an existing file

        **Args:**
        • None

        **Syntax:**
        ```
        /file delete
        ```
        """
        await interaction.response.send_modal(Delete())

    @files.command(name="view", description="view an existing file")
    @app_commands.checks.cooldown(1, 5)
    async def _view_file(self, interaction: discord.Interaction):
        await interaction.response.send_modal(View())

    @files.command(
        name="view-names", description="View names of all the files that exist"
    )
    @app_commands.checks.cooldown(1, 5)
    async def _view_all_file(self, interaction: discord.Interaction):
        """
        **Description:**
        View names of all the files that exist

        **Args:**
        • None

        **Syntax:**
        ```
        /file view
        ```
        """
        await interaction.response.send_message(
            "\n".join(
                [
                    ", ".join(x)
                    for x in (
                        lambda lst, n: [lst[i : i + n] for i in range(0, len(lst), n)]
                    )([f"`{x}`" for x in listdir("./assets/files")], 4)
                ]
            )
        )


async def setup(bot):
    await bot.add_cog(
        FileSystem(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
