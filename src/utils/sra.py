import io

import discord
from discord import Embed, File

from hyena import Bot


class SRA:
    """Class with helper methods for getting/posting data from/to some random api."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_data_for(self, endpoint: str, *, name: str = "endpoint") -> dict:
        """Gets data from some random api for the given endpoint."""
        async with self.bot.session.get(endpoint) as r:
            if not 300 > r.status >= 200:
                error_msg = (
                    "API timed out with response code: `{r.status}`."
                    if r.status != 404
                    else f"The `{name}` you gave could not be found."
                )
                return {"error": error_msg}
            else:
                results: dict = await r.json()
                return results

    async def get_image_for(
        self, *, member: discord.Member, endpoint: str, name="image_endpoint"
    ) -> tuple:
        """Returns an embed and the file object containing the given members edited pfp."""
        member_pfp_url = (
            member.avatar.url
            if member.avatar is not None
            else member.default_avatar.url
        )

        async with self.bot.session.get(
            f"https://some-random-api.ml/canvas/{endpoint}?avatar={member_pfp_url}"
        ) as r:
            img_byte_object = io.BytesIO(await r.read())
            file = File(img_byte_object, f"{name}.png")

            embed = Embed(color=member.color)
            embed.set_image(url=f"attachment://{name}.png")

            return (file, embed)
