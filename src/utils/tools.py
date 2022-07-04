import datetime
import math
import re
import traceback

import discord
from discord.ext import commands

TIME_RE_STRING = r"|".join(
    [
        r"((?P<weeks>\d+?)\s?(weeks?|w))",
        r"((?P<days>\d+?)\s?(days?|d))",
        r"((?P<hours>\d+?)\s?(hours?|hrs|hr?))",
        r"((?P<minutes>\d+?)\s?(minutes?|mins?|m(?!o)))",
        r"((?P<seconds>\d+?)\s?(seconds?|secs?|s))",
    ]
)
TIME_RE = re.compile(TIME_RE_STRING, re.I)


def convert_time(arg):
    time_data = {}
    for time in TIME_RE.finditer(arg):
        for k, v in time.groupdict().items():
            if v:
                time_data[k] = int(v)

    if time_data:
        try:
            res = datetime.timedelta(**time_data)
        except OverflowError:
            raise commands.BadArgument(
                "The time provided is too unreasonably big, use a reasonable time instead."
            )

    if not time_data:
        raise commands.BadArgument(
            "The time provided is not valid, use proper times with their corresponding units `[s|m|h|d|w]`.\
            \nex. `/timeout add @Donut 10 days 5 seconds`\
            \n      `/timeout add @Donut 1w`"
        )

    return res


def error_to_embed(bot, error: Exception = None):
    traceback_text: str = (
        "".join(traceback.format_exception(type(error), error, error.__traceback__))
        if error
        else traceback.format_exc()
    )
    print(traceback_text)
    bot.logger.error(traceback_text)

    length: int = len(traceback_text)
    chunks: int = math.ceil(length / 1990)

    traceback_texts = [traceback_text[l * 1990 : (l + 1) * 1990] for l in range(chunks)]
    return [
        discord.Embed(
            title="Traceback",
            description=("```py\n" + text + "\n```"),
            color=discord.Color.red(),
        )
        for text in traceback_texts
    ]


GRAYSCALE_NOICON_REVERT = "https://i.ibb.co/KjDkLQ8/image.png"


def _get_guild_icon(interaction: discord.Interaction):
    if not interaction.guild.icon:
        return GRAYSCALE_NOICON_REVERT
    return interaction.guild.icon.with_format("png").url


def _get_mem_avatar(user):
    if not user.avatar:
        return user.default_avatar
    return user.avatar.with_format("png").url
