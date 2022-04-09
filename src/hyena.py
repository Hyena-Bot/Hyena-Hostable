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

import logging
import os
import random
import traceback
from random import choice

import aiohttp
import aiosqlite
import discord
import yaml
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils import action_logger, automod_class, checks, sra, tools

load_dotenv()


class Bot(commands.Bot):
    """
    Base subclass of  commands.Bot, with custom methods added.
    """

    def __init__(self, *args, **kwargs):
        self.config = self._load_config()
        super().__init__(
            command_prefix=self._bot_command_prefix,
            owner_ids=self.config["bot_config"]["owners_id"],
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=False
            ),
            description=self.config["bot_config"]["bot_description"],
            *args,
            **kwargs,
        )

        self.help_command = None
        self.secrets = {
            x: y for x, y in os.environ.items() if x in ["TOKEN", "DEEPAI_API_KEY"]
        }
        self.get_commands = self._get_total_commands
        self.version = "1.0.0a"
        self.colors = []
        self._cogs = [
            f"cogs.{cog[:-3]}"
            for cog in os.listdir("cogs")
            if cog.endswith(".py")
            and not cog.startswith("_")
            and not (cog in self.config["bot_config"]["cogs_not_to_load"])
        ]
        self.success_emoji = self.config["bot_config"]["success_emoji"]
        self.failure_emoji = self.config["bot_config"]["failure_emoji"]
        self.logger = self._configure_logging()
        self._gen_colors = lambda: choice(
            [int(x, 16) for x in self.config["bot_config"]["colors"]]
        )

        self.tools = tools
        self.checks = checks
        self._action_logs_db = None
        self._action_logger = None
        self.AutomodHandler = None
        self.SRA = sra.SRA

    def _bot_command_prefix(self, bot, _):
        base = [f"<@!{bot.user.id}> ", f"<@{bot.user.id}> "]
        return [self.config["bot_config"]["bot_prefix"], *base]

    async def setup_hook(self):
        await self._connect_databases()
        self.session = aiohttp.ClientSession()
        self.console = await self.fetch_channel(
            self.config["bot_config"]["errors_channel"]
        )
        self.AutomodHandler = automod_class.Automod

        try:
            for cog in self._cogs:
                try:
                    await self.load_extension(cog)
                    print(f"Loaded {cog[5:]}")
                    self.logger.info(f"Loaded {cog[5:]}")
                except Exception as e:
                    raise e
        except Exception as e:
            raise e
        self._action_logger = action_logger.ModLogs(self)

    async def _connect_databases(self):
        self._action_logs_db = await aiosqlite.connect("./data/action-logs.sqlite")
        self._warns_db = await aiosqlite.connect("./data/warns.sqlite")

    async def close(self):
        await self.session.close()
        await super().close()

    def run(self):
        super().run(self.secrets["TOKEN"])

    async def on_ready(self):
        self.change_status.start()
        print(f"\nLogged in as {self.user} (ID: {self.user.id})")
        print("------")

        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        self.logger.error(traceback.format_exc())
        embeds = self.tools.error_to_embed(self)
        context_embed = discord.Embed(
            title="Context",
            description=f"**Event**: {event_method}",
            color=discord.Color.red(),
        )
        await self.console.send(embeds=[*embeds, context_embed])

    async def _get_bot_prefix(self):
        return self.config["bot_config"]["bot_config"]

    def _load_config(self):
        with open("../config.yml", "r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                self.logger.critical(str(exc))

        return config

    def _get_total_commands(self, bot):
        total = 0
        for command in bot.commands:
            if type(command).__name__ == "Group":
                total += len(command.commands) + 1
                continue
            total += 1

        return total

    def get_cog_aliases(self, term: str):
        aliases = {
            ("moderation", "mod"): "moderation",
            ("handlers", "core", "core-handlers"): "core-handler",
            ("timeout", "mute", "to"): "timeout",
            ("action-logs", "actions", "alogs"): "action-logs",
            ("warns", "warn", "warnings"): "warns",
            ("file-system", "files", "filesys", "file"): "file-system",
            ("afk",): "afk",
            ("fun", "fun-commands"): "fun",
            ("images", "image", "gen", "image-gen"): "image-gen",
        }

        for alias, cog in aliases.items():
            if term.lower() in alias:
                return cog
        return term

    async def process_commands(self, message):
        if message.guild is None or message.author.bot:
            return

        await super().process_commands(message)

    async def on_message(self, message):
        await self.process_commands(message)

    def _configure_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler("bot_logs.log", mode="w")
        file_handler.setFormatter(
            logging.Formatter(
                "%(levelname)s:%(filename)s:%(lineno)d:%(asctime)s:%(message)s"
            )
        )
        logger.addHandler(file_handler)

        return logger

    async def handle_cog_update(self, ctx, cog, _type):
        if cog in ["*", "all"]:
            errored_out = []
            for cog in self._cogs:
                try:
                    if _type == "load":
                        await self.load_extension(cog)
                    elif _type == "unload":
                        await self.unload_extension(cog)
                    else:
                        await self.reload_extension(cog)
                except (
                    commands.errors.ExtensionAlreadyLoaded,
                    commands.errors.ExtensionNotLoaded,
                ):
                    error_type = None
                    if _type == "load":
                        error_type = "is already loaded"
                    if _type in ["unload", "reload"]:
                        error_type = "was not loaded"
                    errored_out.append((cog[5:], f"This extension {error_type}"))
                except commands.errors.ExtensionNotFound:
                    errored_out.append((cog[5:], "This extension was not found"))
            if errored_out == []:
                return await ctx.send("Successfully completed the operation.")
            newline = "\n"

            return await ctx.send(
                f"""
Successfully completed the operation. 
```
Errored out : {newline.join([f"{x[0]} : {x[1]}" for x in errored_out])}
```
"""
            )

        if cog.endswith(".py"):
            cog = cog[:-3]
        cog = self.get_cog_aliases(cog)

        try:
            if _type == "load":
                await self.load_extension("cogs." + cog)
            elif _type == "unload":
                await self.unload_extension("cogs." + cog)
            else:
                await self.reload_extension("cogs." + cog)
            await ctx.message.add_reaction(self.success_emoji)
        except (
            commands.errors.ExtensionAlreadyLoaded,
            commands.errors.ExtensionNotLoaded,
        ):
            error_type = None
            if _type == "load":
                error_type = "is already loaded"
            if _type in ["unload", "reload"]:
                error_type = "was not loaded"
            await ctx.send(f"The cog `{cog}` {error_type}")
        except commands.errors.ExtensionNotFound:
            await ctx.send(f"The cog `{cog}` was not found...")
        except:
            embed = discord.Embed(
                title=f"Error while loading ext: {cog}", color=discord.Colour.red()
            )
            embed.description = f"""
```py
{traceback.format_exc()}
```
        """
            await ctx.send(embed=embed)

    @tasks.loop(seconds=60)
    async def change_status(self):
        """
        Changing the bot status loop,

        In decorator, seconds refer toafter how many second do you want the bot's status to update,
        minimum is 20 seconds or your bot will get rate-limited, this is optimal
        """
        await self.change_presence(
            activity=discord.Game(
                name=random.choice(self.config["bot_config"]["statuses"])
            ),
            status=discord.Status.dnd,
        )
