from discord import Interaction, app_commands


class CheckFailed(app_commands.CheckFailure):
    pass


def _has_interaction_permission(**perms: bool):
    async def check(interaction: Interaction):
        permissions = interaction.channel.permissions_for(interaction.user)
        missing = [
            perm for perm, value in perms.items() if getattr(permissions, perm) != value
        ]

        if not missing:
            return True
        raise CheckFailed(
            f"> You are missing `{', '.join(missing)}` permission(s) to run this command"
        )

    return app_commands.check(check)
