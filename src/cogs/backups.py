import json
import os

import disnake
from disnake.ext import commands

from src.utils import backups
from src.utils.backup import (
    Backup as BackupDB,
)
from src.utils.misc import is_owner, has_bot_permissions


class Backup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super(Backup, self).__init__()
        self.bot = bot
        self.backups = backups
        self.CHANNEL_TYPES = {
            "0": disnake.ChannelType.text,
            "2": disnake.ChannelType.voice,
            "4": disnake.ChannelType.category,
            "5": disnake.ChannelType.news,
            "13": disnake.ChannelType.stage_voice,
            "15": disnake.ChannelType.forum,
        }

    async def cog_load(self) -> None:
        await self.backups.fetch_and_cache_all()

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def backup(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = disnake.Embed(
                title="<:backup:1168599276520226826> Backup commands",
                color=0x2F3136,
                description=(
                    f"`{ctx.prefix}backup create` – Create/update backup\n"
                    f"`{ctx.prefix}backup delete` – Delete backup\n"
                    f"`{ctx.prefix}backup load` – Load backup"
                ),
            )

            if backups.check_backup(ctx.guild):
                data = await backups.get(guild_id=ctx.guild.id)
                data = data["backup_data"]
                embed.add_field(
                    name="Last Backup:",
                    value=f"<t:{data['info']['created']}:f> (<t:{data['info']['created']}:R>)",
                )

            await ctx.send(embed=embed)

    @backup.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @is_owner()
    async def create(self, ctx: commands.Context) -> None:
        guild_backup = (await BackupDB.create(guild=ctx.guild)).to_json()
        print(guild_backup)

        guild_id = guild_backup.get("guild_id", ctx.guild.id)
        guild_backup.pop("guild_id")
        await self.backups.update_backups_info(
            guild_id=guild_id, backup_data=guild_backup
        )

        backup_data = await self.backups.get(
            guild_id=ctx.guild.id, to_return="backup_data"
        )
        print(backup_data)

        print("OK")
        # embed = disnake.Embed(color=0x2F3136)
        # if ctx.author == ctx.guild.owner:
        #     try:
        #         embed.title = "<a:loading:1168599537682755584> Please wait..."
        #         embed.description = "Creating a server backup..."
        #         msg = await ctx.send(embed=embed)
        #
        #         backup_data = {
        #             "info": {
        #                 "nextsave": 2147483647,
        #                 "interval": 0,
        #                 "created": int(time.time()),
        #             },
        #             "guild": {"name": ctx.guild.name},
        #             "text": {},
        #             "voice": {},
        #             "category": {},
        #             "roles": {},
        #         }
        #
        #         for index, category in enumerate(ctx.guild.categories):
        #             category_data = {
        #                 "name": category.name,
        #                 "position": category.position,
        #                 "perms": {
        #                     role.name: {"a": ovw.pair()[0].value, "d": ovw.pair()[1].value}
        #                     for role, ovw in category.overwrites.items()
        #                 },
        #             }
        #             backup_data["category"][str(index)] = category_data
        #
        #         for index, text_channel in enumerate(ctx.guild.text_channels):
        #             text_channel_data = {
        #                 "name": text_channel.name,
        #                 "position": text_channel.position,
        #                 "category": None if text_channel.category is None else str(text_channel.category.id),
        #                 "topic": (
        #                     text_channel.topic
        #                     if text_channel.topic
        #                     else None
        #                 ),
        #                 "slowmode": text_channel.slowmode_delay,
        #                 "nsfw": text_channel.nsfw,
        #                 "perms": {
        #                     role.name: {"a": ovw.pair()[0].value, "d": ovw.pair()[1].value}
        #                     for role, ovw in text_channel.overwrites.items()
        #                 },
        #             }
        #
        #             backup_data["text"][str(index)] = text_channel_data
        #
        #         for index, voice_channel in enumerate(ctx.guild.voice_channels):
        #             voice_channel_data = {
        #                 "name": voice_channel.name.replace(".", " "),
        #                 "limit": voice_channel.user_limit,
        #                 "category": None if voice_channel.category is None else str(voice_channel.category.id),
        #                 "bitrate": voice_channel.bitrate,
        #                 "position": voice_channel.position,
        #                 "perms": {
        #                     role.name: {"a": ovw.pair()[0].value, "d": ovw.pair()[1].value}
        #                     for role, ovw in voice_channel.overwrites.items()
        #                 },
        #             }
        #
        #             backup_data["voice"][str(index)] = voice_channel_data
        #
        #         for index, role in enumerate(ctx.guild.roles):
        #             if not role.managed and role != ctx.guild.default_role:
        #                 role_data = {
        #                     "name": role.name.replace(".", ""),
        #                     "perms": role.permissions.value,
        #                     "color": role.colour.value,
        #                     "hoist": role.hoist,
        #                     "mentionable": role.mentionable,
        #                 }
        #                 backup_data["roles"][str(index)] = role_data
        #
        #         await self.backups.update_backups_info(ctx.guild.id, backup_data)
        #
        #         embed.colour = 0x2F3136
        #         embed.title = "Finished"
        #         embed.description = "Server backup has been successfully created"
        #         await msg.edit(embed=embed)
        #
        #     except (Exception, ExceptionGroup) as e:
        #         raise e
        #         exc_type = e.__class__.__name__
        #         exc_line = sys.exc_info()[2].tb_lineno
        #         logging.error(
        #             f"[log]! {exc_type}: {str(e)}, line {exc_line}"
        #         )
        #         embed.colour = 0x2F3136
        #         embed.title = "An error occurred"
        #         embed.description = (
        #             "An error occurred when trying to save the server. Roles/channels names can't "
        #             "contain the `$` symbol."
        #         )
        #         await ctx.send(embed=embed)
        #
        # else:
        #     embed.colour = 0x2F3136
        #     embed.title = "An error occurred"
        #     embed.description = "This command can only be used by the server owner"
        #     await ctx.send(embed=embed)

    @backup.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @is_owner()
    @has_bot_permissions()
    async def load(self, ctx: commands.Context) -> None:
        guild_backup = await self.backups.get(
            guild_id=ctx.guild.id, to_return="backup_data"
        )
        guild_info = guild_backup.get("guild_info", {})
        categories = guild_backup.get("categories", [])
        channels = guild_backup.get("channels", {})
        print(guild_backup)

        for channel in ctx.guild.channels:
            try:
                if ctx.channel.id != channel.id:
                    await channel.delete()
            except (disnake.HTTPException, disnake.Forbidden, disnake.NotFound):
                continue

        for category in ctx.guild.categories:
            try:
                await category.delete()
            except (disnake.HTTPException, disnake.Forbidden, disnake.NotFound):
                continue

        for role in ctx.guild.roles:
            try:
                await role.delete()
            except (disnake.HTTPException, disnake.Forbidden):
                continue

        print("stage 2: edit guild information")

        """
        guild_info = {
            "name": guild.name, "rules_channel": guild.rules_channel,
            "public_updates_channel": guild.public_updates_channel,
            "afk_channel": guild.afk_channel, "afk_timeout": guild.afk_timeout,
            "description": guild.description, 
        }
        """
        await ctx.guild.edit(
            name=guild_info.get("name", ctx.guild.name),
            description=guild_info.get("description", None),
            rules_channel=guild_info.get("rules_channel", None),
            public_updates_channel=guild_info.get("public_updates_channel", None),
            afk_channel=guild_info.get("afk_channel", None),
            afk_timeout=guild_info.get("afk_timeout", None),
        )

        print("stage 3: creating categories")
        for index, (name, value) in enumerate(categories.items()):
            if channels[index].get("overwrites", {}):
                category = await ctx.guild.create_category(
                    name=value.get("name"),
                    position=value.get("position"),
                    overwrites=channels[index].get("overwrites", {}),
                )
            else:
                category = await ctx.guild.create_category(
                    name=value.get("name"),
                    position=value.get("position"),
                )
            channels[index]["new_category_id"] = category.id


        print("stage 4: creating channels")

        for channel in channels:
            if channel.get("overwrites", {}):
                await ctx.guild._create_channel(
                    name=channel.get("name"),
                    channel_type=self.CHANNEL_TYPES.get(str(channel.get("type"))),
                    position=channel.get("position"),
                    category=channel.get("category", None),
                    default_auto_archive_duration=channel.get("default_auto_archive_duration", None),
                    default_thread_slowmode_delay=channel.get("default_thread_slowmode_delay", None),
                    nsfw=channel.get("nsfw", False),
                    slowmode_delay=channel.get("slowmode_delay", None),
                    overwrites=channel.get("overwrites"),
                    bitrate=channel.get("bitrate", None),
                    user_limit=channel.get("user_limit", None),
                    rtc_region=channel.get("rtc_region", None),
                    video_quality_mode=channel.get("video_quality_mode", None),
                    reason="backup",
                )
            else:
                print(channel.get("type"))
                await ctx.guild._create_channel(
                    name=channel.get("name"),
                    channel_type=self.CHANNEL_TYPES.get(str(channel.get("type"))),
                    position=channel.get("position"),
                    category=channel.get("category", None),
                    default_auto_archive_duration=channel.get("default_auto_archive_duration", None),
                    default_thread_slowmode_delay=channel.get("default_thread_slowmode_delay", None),
                    nsfw=channel.get("nsfw", False),
                    slowmode_delay=channel.get("slowmode_delay", None),
                    bitrate=channel.get("bitrate", None),
                    user_limit=channel.get("user_limit", None),
                    rtc_region=channel.get("rtc_region", None),
                    video_quality_mode=channel.get("video_quality_mode", None),
                    reason="backup",
                )
            print(channel)
        #
        # # FIXME: Refactor
        # embed = disnake.Embed(color=0x2F3136)
        # embed.title = "Loading Backup"
        # embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
        #
        # msg = await ctx.send(embed=embed)
        #
        # if ctx.author == ctx.guild.owner:
        #     data = await self.backups.get(ctx.guild.id, to_return="backup_data")
        #
        #     embed.description = "Stage 1 of 6\n> **Restoring the server name**"
        #     await msg.edit(embed=embed)
        #
        #     # TODO: need refactor because see line 174
        #     await ctx.guild.edit(name=data["guild"]["name"])
        #
        #     embed.description = "Stage 2 of 6\n> **Deleting roles**"
        #     await msg.edit(embed=embed)
        #
        #     for role in ctx.guild.roles:
        #         try:
        #             await role.delete()
        #         except (disnake.Forbidden, disnake.HTTPException):
        #             pass
        #
        #     embed.description = "Stage 3 of 6\n> **Deleting channels**"
        #     await msg.edit(embed=embed)
        #
        #     for channel in ctx.guild.channels:
        #         try:
        #             if channel != ctx.channel:
        #                 await channel.delete()
        #         except (disnake.Forbidden, disnake.NotFound, disnake.HTTPException):
        #             pass
        #
        #     embed.description = "Stage 4 of 6\n> **Creating roles**"
        #     await msg.edit(embed=embed)
        #
        #     roles = len(data["roles"])
        #     for k in range(roles + 1):
        #         try:
        #             await ctx.guild.create_role(
        #                 name=data["roles"][str(k)]["name"],
        #                 colour=disnake.Colour(value=data["roles"][str(k)]["color"]),
        #                 permissions=disnake.Permissions(
        #                     permissions=data["roles"][str(k)]["perms"]
        #                 ),
        #                 hoist=data["roles"][str(k)]["hoist"],
        #                 mentionable=data["roles"][str(k)]["mentionable"],
        #             )
        #         except (
        #             disnake.NotFound,
        #             disnake.Forbidden,
        #             disnake.HTTPException,
        #             TypeError,
        #             KeyError,
        #         ):
        #             pass
        #
        #     embed.description = "Stage 5 of 6\n> **Creating categories**"
        #     await msg.edit(embed=embed)
        #
        #     categories = len(data["category"])
        #     for i in range(categories + 1):
        #         try:
        #             overwrites = {}
        #             # TODO: need refactor because see line 174
        #             raw_overwrites = data["category"][str(i)]["perms"]
        #
        #             for role_to_recovery in ctx.guild.roles:
        #                 try:
        #                     ovw = disnake.PermissionOverwrite.from_pair(
        #                         disnake.Permissions(
        #                             permissions=raw_overwrites[role_to_recovery.name][
        #                                 "a"
        #                             ]
        #                         ),
        #                         disnake.Permissions(
        #                             permissions=raw_overwrites[role_to_recovery.name][
        #                                 "d"
        #                             ]
        #                         ),
        #                     )
        #                     overwrites[role_to_recovery] = ovw
        #                 except (Exception, ExceptionGroup):
        #                     pass
        #
        #             await ctx.guild.create_category(
        #                 name=data["category"][str(i)]["name"],
        #                 position=data["category"][str(i)]["position"],
        #                 overwrites=overwrites,
        #             )
        #         except (disnake.Forbidden, disnake.HTTPException, TypeError, KeyError):
        #             pass
        #
        #     embed.description = "Stage 6 of 6\n> **Creating channels**"
        #     await msg.edit(embed=embed)
        #
        #     text_channels = len(data["text"])
        #     for i in range(text_channels + 1):
        #         try:
        #             overwrites = {}
        #             # TODO: need refactor because see line 174
        #             raw_overwrites = data["text"][str(i)]["perms"]
        #
        #             for old_role_permissions in ctx.guild.roles:
        #                 try:
        #                     ovw = disnake.PermissionOverwrite.from_pair(
        #                         disnake.Permissions(
        #                             permissions=raw_overwrites[
        #                                 old_role_permissions.name
        #                             ]["a"]
        #                         ),
        #                         disnake.Permissions(
        #                             permissions=raw_overwrites[
        #                                 old_role_permissions.name
        #                             ]["d"]
        #                         ),
        #                     )
        #                     overwrites[old_role_permissions] = ovw
        #                 except (Exception, ExceptionGroup):
        #                     pass
        #
        #             if data["text"][str(i)]["category"] is None:
        #                 await ctx.guild.create_text_channel(
        #                     name=data["text"][str(i)]["name"],
        #                     topic=data["text"][str(i)]["topic"],
        #                     nsfw=data["text"][str(i)]["nsfw"],
        #                     slowmode_delay=data["text"][str(i)]["slowmode"],
        #                     position=data["text"][str(i)]["position"],
        #                     overwrites=overwrites,
        #                 )
        #             else:
        #                 category = (
        #                     await self.backups.get(  # TODO: FIX
        #                         ctx.guild.id, to_return="backup_data"
        #                     ),
        #                 )
        #
        #                 await ctx.guild.create_text_channel(
        #                     name=data["text"][str(i)]["name"],
        #                     topic=data["text"][str(i)]["topic"],
        #                     nsfw=data["text"][str(i)]["nsfw"],
        #                     slowmode_delay=data["text"][str(i)]["slowmode"],
        #                     position=data["text"][str(i)]["position"],
        #                     category=category["text"][str(i)]["category"],
        #                     overwrites=overwrites,
        #                 )
        #         except (disnake.Forbidden, disnake.HTTPException, TypeError, KeyError):
        #             pass
        #
        #     voice_channels = len(data["voice"])
        #     for i in range(voice_channels + 1):
        #         try:
        #             overwrites = {}
        #             raw_overwrites = data["voice"][str(i)]["perms"]
        #
        #             for old_role_permissions in ctx.guild.roles:
        #                 try:
        #                     ovw = disnake.PermissionOverwrite.from_pair(
        #                         disnake.Permissions(
        #                             permissions=raw_overwrites[
        #                                 old_role_permissions.name
        #                             ]["a"]
        #                         ),
        #                         disnake.Permissions(
        #                             permissions=raw_overwrites[
        #                                 old_role_permissions.name
        #                             ]["d"]
        #                         ),
        #                     )
        #                     overwrites[old_role_permissions] = ovw
        #                 except (Exception, ExceptionGroup, KeyError):
        #                     pass
        #
        #             if data["voice"][str(i)]["category"] is None:
        #                 await ctx.guild.create_voice_channel(
        #                     name=data["voice"][str(i)]["name"],
        #                     user_limit=data["voice"][str(i)]["limit"],
        #                     bitrate=data["voice"][str(i)]["bitrate"],
        #                     position=data["voice"][str(i)]["position"],
        #                     overwrites=overwrites,
        #                 )
        #             else:
        #                 category = (
        #                     await self.backups.get(  # TODO: FIX
        #                         ctx.guild.id, to_return="backup_data"
        #                     ),
        #                 )
        #
        #                 await ctx.guild.create_voice_channel(
        #                     name=data["voice"][str(i)]["name"],
        #                     user_limit=data["voice"][str(i)]["limit"],
        #                     bitrate=data["voice"][str(i)]["bitrate"],
        #                     position=data["voice"][str(i)]["position"],
        #                     category=category["voice"][str(i)]["category"],
        #                     overwrites=overwrites,
        #                 )
        #         except (disnake.Forbidden, disnake.HTTPException, TypeError, KeyError):
        #             pass
        #
        #     embed.title = "Finished"
        #     embed.colour = 0x2F3136
        #     embed.description = "Server backup has been successfully loaded"
        #
        #     await msg.edit(embed=embed)
        # else:
        #     embed.colour = 0x2F3136
        #     embed.title = "An error occurred"
        #     embed.description = "This command can only be used by the server owner"
        #
        #     await msg.edit(embed=embed)

    @backup.command(aliases=["file"])
    @commands.cooldown(1, 50, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def _file(self, ctx: commands.Context) -> None:
        if backups.check_backup(ctx.guild):
            backup = {
                "guild": {},
                "text_channels": {},
                "voice_channels": {},
                "categories": {},
                "roles": {},
            }
            data = await self.backups.get(ctx.guild.id, to_return="backup_data")
            backup["guild"]["name"] = data["guild"]["name"]
            backup["text_channels"] = data["text"]
            backup["voice_channels"] = data["voice"]
            backup["categories"] = data["category"]
            backup["roles"] = data["roles"]

            with open(
                    str(ctx.guild.id) + ".json", "w"
            ) as f:  # TODO: use ujson + f-string
                json.dump(backup, f, indent=4)

            await ctx.send(
                file=disnake.File(str(ctx.guild.id) + ".json")
            )  # TODO: use f-string
            os.remove(str(ctx.guild.id) + ".json")
        else:
            embed = disnake.Embed(
                colour=0x2F3136,
                title="An error occurred",
                description="There isn't any backup created for this server",
            )

            await ctx.send(embed=embed)

    @backup.command()
    @is_owner()
    async def delete(self, ctx: commands.Context) -> None:
        embed = disnake.Embed(color=0x2F3136)

        if backups.check_backup(ctx.guild):
            await self.backups.remove_from_db({"_id": ctx.guild.id})
            embed.title = "Finished"
            embed.description = "Server backup has been successfully deleted"
            await ctx.send(embed=embed)
        else:
            embed.title = "An error occurred"
            embed.description = "Server backup hasn't been deleted."
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar)
            await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Backup(bot))
