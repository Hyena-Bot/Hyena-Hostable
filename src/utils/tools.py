import math
import traceback

import discord


def error_to_embed(error: Exception = None):
    traceback_text: str = (
        "".join(traceback.format_exception(type(error), error, error.__traceback__))
        if error
        else traceback.format_exc()
    )
    print(traceback.format_exc())

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
