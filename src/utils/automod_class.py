import contextlib
import datetime
import json
import os
import re

import aiohttp
import discord
from better_profanity import profanity

from hyena import Bot

# Constants
INVITE_REGEX = re.compile(
    r"(https://www\.|https://|www\.)?(discord.gg|discord.com/invite|dis.gd/invite|dsc.io|dsc.gg|invite.gg)/[a-zA-z0-9_-]"
)

# Tokens
anti_phish_token = os.getenv("AZRAEL_API_TOKEN")


# Helper Functions


def format_message(msg: str, user: discord.Member) -> str:
    msg = msg.replace("$mention", user.mention)  # more soon
    return msg


# Automod base class
class Automod:
    def __init__(self, bot: Bot, message: discord.Message):
        self.bot = bot
        self.message = message

    async def take_action(self) -> None:
        warn_message = str(self.bot.config["automod_config"]["warn_message"])
        delete_after = int(self.bot.config["automod_config"]["delete_message_after"])

        with contextlib.suppress(discord.Forbidden, discord.NotFound):
            await self.message.delete()
            await self.message.channel.send(
                format_message(warn_message, self.message.author),
                delete_after=delete_after,
            )

    async def is_badwords(self) -> bool:  # TODO add more stuff & docs
        if not self.is_enabled("badwords"):
            return False
        else:
            custom_badwords = self.bot.config["automod_config"]["custom_badwords"]
            if custom_badwords:
                try:
                    profanity.add_censor_words(custom_badwords)
                except:
                    pass

            badword = profanity.contains_profanity(self.message.content)
            if badword is True:
                return True
            else:
                return False

    async def is_caps(self) -> bool:  # TODO docs
        if not self.is_enabled("caps"):
            return False
        else:
            caps_threshold = int(self.bot.config["automod_config"]["caps_threshold"])
            count = 0
            length = len(self.message.content)

            if (
                length < 5
            ):  # if there are less then 5 words in our message we can ignore it.
                return False

            for word in self.message.content:
                if word.isupper():
                    count += 1

            try:
                percent = round(count / length * 100)
            except:
                return False

            if percent >= caps_threshold:
                return True
            else:
                return False

    async def is_invite(self) -> bool:
        if not self.is_enabled("invites"):
            return False
        else:
            detected = INVITE_REGEX.search(self.message.content)

            if detected:
                return True
            else:
                return False

    async def is_spam(self) -> bool:
        if not self.is_enabled("spam"):
            return False
        else:
            messages = list(
                filter(
                    lambda m: m.author == self.message.author
                    and (
                        datetime.datetime.now(datetime.timezone.utc) - m.created_at
                    ).seconds
                    < 10,
                    self.bot.cached_messages,
                )
            )

            current_message_interval = self.bot.config["automod_config"][
                "spam_messages_back_to_back"
            ]
            message_size = self.bot.config["automod_config"]["spam_message_word_limit"]

            if len(messages) >= current_message_interval:
                return True
            elif len(self.message.content) >= message_size:
                return True
            else:
                return False

    async def is_phish_url(self) -> bool:
        if not self.is_enabled("phish"):
            return False

        else:
            header = {
                "Authorization": anti_phish_token,
                "Content-Type": "application/json",
                "User-Agent": "Azrael Header", # replace with agent given by the api
            }
            data = json.dumps({"data": self.message.content})

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://phish.azrael.gg/check", headers=header, data=data
                ) as r:
                    results: dict = await r.json()
                    await session.close()
            if results and results.get("matched", None) is True:
                return True
            else:
                return False

    def dm_embed(self, reason: str = None) -> discord.Embed:
        """Returns a base embed for dm'ing the user."""
        embed = discord.Embed(
            title=f"You have been warned in {self.message.guild.name}",
            color=discord.Color.yellow(),
        )
        if reason:
            embed.description = reason
        embed.timestamp = self.message.created_at

        return embed

    def is_author_mod(self) -> bool:
        """Returns True when the user has moderation permissions."""
        member = self.message.author
        if isinstance(member, discord.User):
            return False
        if member.guild_permissions.administrator:
            return True
        elif member.guild_permissions.manage_guild:
            return True
        elif member.guild_permissions.manage_messages:
            return True
        elif member.id in self.bot.owner_ids:
            return True
        else:
            return False

    def is_ignored_channel(self) -> bool:
        ignored_channels = self.bot.config["automod_config"]["ignored_channels"]
        if ignored_channels:
            return self.message.channel.id in ignored_channels

    def is_enabled(self, filter: str):
        if filter.lower() not in ["badwords", "spam", "invites", "phish"]:
            return (None, "Invalid option supplied.")
        try:
            selected_filter = self.bot.config["automod_config"][filter]
        except KeyError:
            return False

        if selected_filter and selected_filter is True:
            return True
        else:
            return False
