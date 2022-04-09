import asyncio
import contextlib
import datetime
import json
import os
import re

import aiohttp
import discord
from better_profanity import profanity

# Constants
INVITE_REGEX = re.compile(
    r"(https://www\.|https://|www\.)?(discord.gg|discord.com/invite|dis.gd/invite|dsc.io|dsc.gg|invite.gg)/[a-zA-z0-9_-]"
)
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"


def default_filters():
    with open("./data/filtered-words.json") as f:
        return json.load(f)


class Automod:
    """Automod base class with all the required methods & functionality"""

    def __init__(self, bot, message: discord.Message):
        self.bot = bot
        self.message = message
        self.default_filters = default_filters()

    # ------------ HELPER ------------

    async def api_nsfw_detector(self, url):
        """Make request to the nsfw api with a given URL"""
        headers = {"Api-Key": self.bot.secrets["DEEPAI_API_KEY"]}
        data = {"image": url}

        try:
            async with self.bot.session.post(
                "https://api.deepai.org/api/nsfw-detector", headers=headers, data=data
            ) as r:
                return await r.json()
        except (
            asyncio.exceptions.TimeoutError,
            aiohttp.client_exceptions.ClientConnectorError,
        ):
            return False

    # ------------ HANDLERS ------------

    async def take_action(self) -> None:
        """Basically, delete the message"""
        with contextlib.suppress(discord.Forbidden, discord.NotFound):
            await self.message.delete()

    async def is_badwords(self) -> bool:
        """Checks for profanity words"""
        if not self.is_enabled("badwords"):
            return False
        else:
            custom_badwords = [
                x
                for x in self.bot.config["automod_config"]["custom_badwords"]
                if not x in [None, "", " "]
            ]
            if not custom_badwords:
                custom_badwords = self.default_filters
            try:
                profanity.add_censor_words(custom_badwords)
            except:
                pass

            badword = profanity.contains_profanity(self.message.content)
            if badword == True:
                return True
            else:
                return False

    async def is_caps(self) -> bool:  # TODO docs
        """Checks for too many capitals"""
        if not self.is_enabled("caps"):
            return False
        else:
            caps_threshold = int(self.bot.config["automod_config"]["caps_threshold"])
            count = 0
            length = len(self.message.content)

            if (
                length < 7
            ):  # if there are less then 7 words in our message we can ignore it.
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
        """Checks for invite links"""
        if not self.is_enabled("invites"):
            return False
        else:
            detected = INVITE_REGEX.search(self.message.content)

            if detected:
                return True
            else:
                return False

    async def is_spam(self) -> bool:
        """Anti spam system"""
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
        """Anti phishing systems"""
        if not self.is_enabled("phish"):
            return False

        if re.search(URL_REGEX, self.message.content):
            header = {
                "Content-Type": "application/json",
                "User-Agent": "Hyena-Hostable https://github.com/Hyena-Bot/Hyena-Hostable",
            }
            data = json.dumps({"message": self.message.content})

            try:
                async with self.bot.session.post(
                    "https://anti-fish.bitflow.dev/check", headers=header, data=data
                ) as r:
                    results: dict = await r.json()
                if results and results.get("match") is True:
                    return True, results["matches"]
                else:
                    return False
            except (
                asyncio.exceptions.TimeoutError,
                aiohttp.client_exceptions.ClientConnectorError,
            ):
                return False

    async def is_nsfw(self) -> bool:
        """Checks for nsfw attachments in message"""
        if not self.is_enabled("nsfw") or self.message.channel.is_nsfw():
            return False

        regex_result = re.findall(URL_REGEX, self.message.content)
        urls = [x[0] for x in regex_result]
        attachments = [x.url for x in self.message.attachments]
        image_urls = sorted(set([*urls, *attachments]))

        for url in image_urls:
            res = await self.api_nsfw_detector(url)
            if res.get("err") is not None:
                continue
            try:
                score = res["output"]["nsfw_score"]
                if score >= 0.8:
                    return True
            except KeyError:
                pass

    async def excess_mentions(self):
        """Checks for too many mentions in the message"""
        if not self.is_enabled("mentions"):
            return False

        dup = self.bot.config["automod_config"]["allow_duplicate_mentions"]
        mentions = []
        for i in self.message.raw_mentions:
            if i != self.message.author.id:
                mentions.append(i)

        if dup == True:
            mentions = sorted(set(mentions))

        limit = self.bot.config["automod_config"]["mention_limit"]
        if len(mentions) > limit:
            return True

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
        """Returns true or false considering if the channel of the message is ignored in the config"""
        ignored_channels = self.bot.config["automod_config"]["ignored_channels"]
        if ignored_channels:
            return self.message.channel.id in ignored_channels

    def is_enabled(self, _filter: str):
        """ "Returns true or false considering if the given handler is enabled in the config"""
        if _filter.lower() not in [
            "badwords",
            "spam",
            "invites",
            "phish",
            "nsfw",
            "mentions",
            "caps",
        ]:
            return (None, "Invalid option supplied.")
        try:
            selected_filter = self.bot.config["automod_config"][_filter]
        except KeyError:
            return False

        if selected_filter and selected_filter is True:
            return True
        else:
            return False
