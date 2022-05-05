from inspect import cleandoc
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class HelpSelect(discord.ui.Select):
    def __init__(self, view):
        self._view = view
        options = [
            discord.SelectOption(label="Home", value=1, emoji="🏘️"),
            discord.SelectOption(
                label="Utility", value=2, emoji="<:tools:844508570813071400>"
            ),
            discord.SelectOption(
                label="Moderation", value=3, emoji="<:banthonk:832104988046000178>"
            ),
            discord.SelectOption(
                label="Fun", value=4, emoji="<:fun:844509126095929354>"
            ),
        ]
        super().__init__(
            custom_id="skip-to-page", placeholder="Skip to page", options=options, row=0
        )

    async def callback(self, interaction):
        self._view.cur_page = int(self.values[0])
        await self._view._update_embed(interaction)


class Right(discord.ui.Button):
    def __init__(self, view):
        self._view = view
        super().__init__(
            emoji="<:right:875244926688960533>",
            row=1,
            style=discord.ButtonStyle.blurple,
        )

    async def callback(self, interaction):
        self._view.cur_page += 1
        await self._view._update_embed(interaction)


class Left(discord.ui.Button):
    def __init__(self, view):
        self._view = view
        super().__init__(
            emoji="<:left:875244882799771699>", row=1, style=discord.ButtonStyle.blurple
        )

    async def callback(self, interaction):
        self._view.cur_page -= 1
        await self._view._update_embed(interaction)


class DoubleRight(discord.ui.Button):
    def __init__(self, view):
        self._view = view
        super().__init__(
            emoji="<:double_right:875244972318810133>",
            row=1,
            style=discord.ButtonStyle.blurple,
        )

    async def callback(self, interaction):
        self._view.cur_page = 4
        await self._view._update_embed(interaction)


class DoubleLeft(discord.ui.Button):
    def __init__(self, view):
        self._view = view
        super().__init__(
            emoji="<:double_left:875244843452989490>",
            row=1,
            style=discord.ButtonStyle.blurple,
        )

    async def callback(self, interaction):
        self._view.cur_page = 1
        await self._view._update_embed(interaction)


class Stop(discord.ui.Button):
    def __init__(self, view):
        self._view = view
        super().__init__(emoji="🔒", row=1, style=discord.ButtonStyle.red)

    async def callback(self, interaction):
        await interaction.response.edit_message(
            embed=self._view.embeds[str(self._view.cur_page)], view=None
        )


class HelpView(discord.ui.View):
    def __init__(self, user, embeds, timeout=60):
        super().__init__(timeout=timeout)
        self.user = user
        self.embeds = embeds
        self.cur_page = 1
        self.add_item(HelpSelect(self))
        self.add_item(DoubleLeft(self))
        self.add_item(Left(self))
        self.add_item(Stop(self))
        self.add_item(Right(self))
        self.add_item(DoubleRight(self))

    async def interaction_check(self, interaction) -> bool:
        return interaction.user.id == self.user.id

    async def _update_embed(self, interaction: discord.Interaction):
        if self.cur_page < 1:
            self.cur_page = int(len(self.embeds) / 2)
        if self.cur_page > int(len(self.embeds) / 2):
            self.cur_page = 1

        await interaction.response.edit_message(embed=self.embeds[str(self.cur_page)])


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = [None]

    @app_commands.command(name="help", description="Get bot help!")
    @app_commands.describe(
        command="The parent/command to look help for",
        subcommand="The subcommand to look help for",
    )
    @app_commands.checks.cooldown(1, 3, key=lambda i: (i.guild_id, i.user.id))
    async def help(
        self,
        interaction: discord.Interaction,
        command: Optional[str],
        subcommand: Optional[str],
    ):
        if command:
            all_commands = {
                cmd.qualified_name: cmd
                for cmd in self.bot.tree.walk_commands(
                    guild=discord.Object(id=self.bot.config["bot_config"]["guild_id"])
                )
            }

            _cmd_str = command.lower().strip()
            _cmd = all_commands.get(_cmd_str)
            if not _cmd:
                return await interaction.response.send_message(
                    f"I cannot find the command `{command}`."
                )

            if isinstance(_cmd, app_commands.Group):
                if not subcommand:
                    return await interaction.response.send_message(
                        "Please type in subcommand if looking for a group."
                    )
                _cmd = all_commands.get(f"{_cmd.name} {subcommand.lower().strip()}")
                if not _cmd:
                    return await interaction.response.send_message(
                        f"I cannot find the command `{command} {subcommand}`."
                    )

            embed = discord.Embed(
                color=self.bot._gen_colors(), timestamp=interaction.created_at
            )
            embed.set_thumbnail(url=self.bot.tools._get_mem_avatar(self.bot.user))
            embed.set_footer(
                text=f"Requested by {interaction.user} | Prefix: Use / before each command",
                icon_url=self.bot.tools._get_mem_avatar(interaction.user),
            )
            embed.description = f"""
**/{_cmd.qualified_name}**

**Cog & Category:**
{_cmd.binding.qualified_name.title()}
- `{_cmd.binding.category[0].title()}`

{cleandoc(_cmd.callback.__doc__)}
"""

            await interaction.response.send_message(embed=embed)
        else:
            cogs = [self.bot.get_cog(e) for e in self.bot.cogs]
            util_cogs = [e for e in cogs if "utilities" in e.category]
            fun_cogs = [e for e in cogs if "fun" in e.category]
            mod_cogs = [e for e in cogs if "moderation" in e.category]

            name = self.bot.config["bot_config"]["bot_name"].title()

            def _check_binding(cmd, cog):
                try:
                    return cmd.binding == cog
                except AttributeError:
                    return False

            embeds = [
                discord.Embed(
                    color=self.bot._gen_colors(), timestamp=interaction.created_at
                )
                .set_thumbnail(url=self.bot.tools._get_mem_avatar(self.bot.user))
                .set_footer(
                    text=f"Requested by {interaction.user} | Prefix: Use / before each command",
                    icon_url=self.bot.tools._get_mem_avatar(interaction.user),
                )
                for _ in range(4)
            ]

            # ------

            embeds[0].set_author(name=f"{name} Help", icon_url=self.bot.user.avatar.url)
            embeds[0].add_field(
                name="Navigating the pages:",
                value="""
                <:double_left:875244843452989490> Go to first page
                <:left:875244882799771699> Go back one page
                🔒 Lock the help screen.
                <:right:875244926688960533> Go Forward one page
                <:double_right:875244972318810133> Go to the last page
                """,
            )
            embeds[0].add_field(
                name=f"❓ | New To {name}?",
                value=f"`{self.bot.description}`",
                inline=False,
            )
            embeds[0].add_field(
                name="Contents:",
                value="**Page 1.** Introduction \n**Page 2.** Utilities \n**Page 3.** Moderation \n**Page 4.** Fun",
            )
            embeds[0].add_field(
                name="Useful Links",
                value=f"[Project](https://github.com/Hyena-Bot/Hyena-Hostable) | [Dev Server](https://discord.gg/cHYWdK5GNt)",
            )

            all_commands = [
                cmd
                for cmd in self.bot.tree.walk_commands(
                    guild=discord.Object(id=self.bot.config["bot_config"]["guild_id"])
                )
            ]

            # -------

            command_block = []

            for cog in util_cogs:
                commands = [x for x in all_commands if _check_binding(x, cog)]
                for command in commands:
                    desc = (
                        command.description.capitalize()[:31] + "..."
                        if len(command.description) > 34
                        else command.description
                    )
                    command_block.append(f"`/{command.qualified_name}:` {desc}")

            embeds[1].set_author(
                name="Tools and Utilities",
                icon_url="https://cdn.discordapp.com/emojis/844508570813071400.png?v=1",
            )
            embeds[1].add_field(
                name="Commands:", value="\n".join(command_block), inline=False
            )

            # -------

            command_block = []

            for cog in mod_cogs:
                commands = [x for x in all_commands if _check_binding(x, cog)]
                for command in commands:
                    desc = (
                        command.description.capitalize()[:31] + "..."
                        if len(command.description) > 34
                        else command.description
                    )
                    command_block.append(f"`/{command.qualified_name}:` {desc}")

            embeds[2].set_author(
                name="Moderation",
                icon_url="https://cdn.discordapp.com/emojis/832104988046000178.png?v=1",
            )
            embeds[2].add_field(
                name="Commands:", value="\n".join(command_block), inline=False
            )

            # -------

            command_block = []

            for cog in fun_cogs:
                commands = [x for x in all_commands if _check_binding(x, cog)]
                for command in commands:
                    desc = (
                        command.description.capitalize()[:31] + "..."
                        if len(command.description) > 34
                        else command.description
                    )
                    command_block.append(f"`/{command.qualified_name}:` {desc}")

            embeds[3].set_author(
                name="Fun",
                icon_url="https://cdn.discordapp.com/emojis/844509126095929354.png?v=1",
            )
            embeds[3].add_field(
                name="Commands:", value="\n".join(command_block), inline=False
            )

            # -------

            helps = {
                "1": embeds[0],
                "2": embeds[1],
                "3": embeds[2],
                "4": embeds[3],
                "home": embeds[0],
                "utils": embeds[1],
                "moderation": embeds[2],
                "fun": embeds[3],
            }

            view = HelpView(interaction.user, helps)
            await interaction.response.send_message(embed=helps["1"], view=view)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(
        Help(bot), guild=discord.Object(id=bot.config["bot_config"]["guild_id"])
    )
