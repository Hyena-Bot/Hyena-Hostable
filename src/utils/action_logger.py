import json

import discord


class ModLogs:
    def __init__(self, bot):
        self.bot = bot
        self._db = self.bot._action_logs_db

    async def _send_embed(
        self,
        moderator: discord.Member,
        member: discord.User,
        description: str,
        timestamp,
    ):
        _logs_channel = self.bot.get_channel(
            self.bot.config["bot_config"]["mod_action_logs_channel"]
        )
        embed = discord.Embed(
            color=self.bot._gen_colors(),
            timestamp=timestamp,
        )
        if isinstance(member, discord.Member):
            embed.set_author(
                name=f"ACTION | {member}",
                icon_url=self.bot.tools._get_mem_avatar(member),
            )
        if isinstance(member, discord.TextChannel):
            embed.set_author(
                name=f"ACTION | {member.name}",
                icon_url=self.bot.tools.GRAYSCALE_NOICON_REVERT,
            )
        embed.description = description
        embed.set_footer(
            text=f"Moderator: {moderator}",
            icon_url=self.bot.tools._get_mem_avatar(moderator),
        )

        try:
            await _logs_channel.send(embed=embed)
        except Exception as e:
            pass

    async def _log_action(self, action: dict):
        """
        {
            "user_id": 521640052195852298, # ID of the user against which the moderation action was take
            "data": {
                "action": "The moderation action", # eg. "warn" or "ban" etc.
                "reason": "reason for the action",
                "moderator": 918703165648539700 # the moderator who took the action
                # You can add as many keys as you want.
                # These three are mandoratory you could add any others
            }
        }
        """
        cursor = await self._db.execute(
            "SELECT * FROM moderation_actions WHERE user_id = ?", (action["user_id"],)
        )
        res = await cursor.fetchone()
        if not res:
            await self._db.execute(
                "INSERT INTO moderation_actions(user_id, actions) VALUES(?,?)",
                (action["user_id"], json.dumps([action["data"]])),
            )
        if res:
            _new_data = [*json.loads(res[1]), action["data"]]
            await self._db.execute(
                "UPDATE moderation_actions SET actions = ? WHERE user_id = ?",
                (json.dumps(_new_data), action["user_id"]),
            )

        await self._db.commit()
        await cursor.close()
