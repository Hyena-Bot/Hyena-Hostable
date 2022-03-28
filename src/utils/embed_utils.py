import random
from discord import Embed, Color
from hyena import Bot


def success_embed(bot: Bot, *, title: str = None, desc: str = None, pfp_url: str = None, color = None) -> Embed:
    """
    Creates an embed for moderation actions.\n
    Accepts the following kwargs:
        `title`: str - the title of embed.
        `desc`: str - the description of embed.
        `pfp_url`: str - the users profile picture's url.
    """
    if title is None and desc is None:
        raise RuntimeError("Neither Mod embed title nor description was provided.")

    else:
        if not color:
            color = Color.green()

        embed = Embed(color = color)

        if title:
            embed.title = f"{bot.success_emoji} {title}"
        if desc:
            embed.description = desc
        
        if pfp_url:
            embed.set_thumbnail(url = pfp_url)
        
        return embed

