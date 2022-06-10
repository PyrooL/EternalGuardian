from http import server
import discord
import json
import traceback
import re

class ServerRoles:
    def __init__(self, member: discord.Role, mod: discord.Role, mute: discord.Role):
        self.member: discord.Role = member
        self.mod: discord.Role    = mod
        self.mute: discord.Role   = mute

class ServerChannels:
    def __init__(self, modchat: discord.TextChannel,
                       entryway: discord.TextChannel,
                       unifiedchat: discord.TextChannel,
                       banskicks: discord.TextChannel,
                       filtercatches: discord.TextChannel,
                       botmessages: discord.TextChannel):
        self.modchat: discord.TextChannel       = modchat
        self.entryway: discord.TextChannel      = entryway
        self.unifiedchat: discord.TextChannel   = unifiedchat
        self.banskicks: discord.TextChannel     = banskicks
        self.filtercatches: discord.TextChannel = filtercatches
        self.botmessages: discord.TextChannel   = botmessages

class ServerInfo:
    def __init__(self, roles: ServerRoles, channels: ServerChannels):
        self.roles: ServerRoles = roles
        self.channels: ServerChannels = channels

class EternalGuardian(discord.Client):
    def __init__(self, config, *args, **kwargs):
        super(EternalGuardian, self).__init__(*args, **kwargs)
        self.ready = False
        self.loaded = False

        self.config = config
        self.error_channel = None
        self.servers = {}
        self.filter_hard = []
        self.filter_soft = []
    
    async def on_ready(self):
        print(f"logged on as {self.user}")
        self.ready = True
        await self.load()

    async def on_message(self, message: discord.Message):
        if not self.ready or not self.loaded:
            return
        if message.guild and message.guild.id in self.servers:
            server_info: ServerInfo = self.servers[message.guild.id]

        try:
            # was this message sent in bot dms?
            if message.channel.type == discord.ChannelType.private and message.author != self.user:
                for _, server_info in self.servers.items():
                    embed = discord.Embed()
                    embed.set_author(name = f"{message.author} ({message.author.id})",
                                     icon_url = message.author.avatar_url)

                    if message.clean_content:
                        embed.description = message.clean_content
                    else:
                        embed.description = "*(message has no content. could be a sticker?)*"

                    if message.attachments or message.stickers:
                        embed.description += "\n\n**Attachments:**"
                    for attachment in message.attachments:
                        embed.description += f"\n<{attachment.url}>"
                    for sticker in message.stickers:
                        embed.description += f"\n<{sticker.image_url}>"

                    await server_info.channels.botmessages.send(embed = embed)
                return

            # from this point on, ignore messages in invalid servers or ones from bots.
            if not message.guild.id in self.servers or message.author.bot:
                return

            # let's check the message to see if it violates the filter.
            for pattern in self.filter_soft:
                if pattern.search(message.clean_content.lower()) is not None:
                    content = message.clean_content
                    if len(content) > 1800: # too long to send without hitting message length limit
                        content = "(message was too long to send)"
                    await server_info.channels.filtercatches.send(f"{server_info.roles.mod.mention} soft filter triggered by {message.author.mention}: ```{message.clean_content}```filter triggered: `{pattern.pattern}`")
                    await message.delete()
                    return

            for pattern in self.filter_hard:
                if pattern.search(message.clean_content.lower()) is not None:
                    content = message.clean_content
                    if len(content) > 1800: # too long to send without hitting message length limit
                        content = "(message was too long to send)"
                    await server_info.channels.filtercatches.send(f"{server_info.roles.mod.mention} hard filter triggered by {message.author.mention}: ```{message.clean_content}```filter triggered: `{pattern.pattern}`\n*mute has been auto-applied*")
                    await message.author.add_roles(server_info.roles.mute)
                    await message.delete()
                    return

            # handle entryway!
            if message.channel == server_info.channels.entryway:
                if message.content.lower() == self.config["captcha"]:
                    await message.author.add_roles(server_info.roles.member)
                await message.delete()
                await server_info.channels.unifiedchat.send(f":white_check_mark: {message.author.mention} just verified with captcha")
                return
            
            # it's spelled *roguelike.*
            if "rougelike" in message.content.lower():
                await message.reply("It's spelled *roguelike*.")
            if "rougelite" in message.content.lower():
                await message.reply("It's spelled *roguelite*.")
                
            # and now it's time to just put it in unified!
            # todo..
        except BaseException:
            await self.error_channel.send(
                embed = discord.Embed(title = "error!",
                    description = traceback.format_exc().replace("_", "\_"),
                    color = discord.Color.red()))
    
    async def load(self):
        """Loads the bot information from the provided config!"""
        self.loaded = False
        print("loading from config..")

        await self.change_presence(activity = discord.Game(name = self.config["status"]))

        self.error_channel = self.get_channel(self.config["errorchannel"])

        for guild in self.guilds:
            role_member = None
            role_mod    = None
            role_mute   = None
            channel_modchat       = None
            channel_entryway      = None
            channel_unifiedchat   = None
            channel_banskicks     = None
            channel_filtercatches = None
            channel_botmessages   = None

            for role in guild.roles:
                if role.name == self.config["roles"]["member"]:
                    role_member = role
                    continue
                
                if role.name == self.config["roles"]["mod"]:
                    role_mod = role
                    continue

                if role.name == self.config["roles"]["mute"]:
                    role_mute = role
                    continue
            
            for channel in guild.channels:
                if channel.name == self.config["channels"]["modchat"]:
                    channel_modchat = channel
                    continue

                if channel.name == self.config["channels"]["entryway"]:
                    channel_entryway = channel
                    continue

                if channel.name == self.config["channels"]["unifiedchat"]:
                    channel_unifiedchat = channel
                    continue

                if channel.name == self.config["channels"]["banskicks"]:
                    channel_banskicks = channel
                    continue

                if channel.name == self.config["channels"]["filtercatches"]:
                    channel_filtercatches = channel
                    continue

                if channel.name == self.config["channels"]["botmessages"]:
                    channel_botmessages = channel
                    continue

            has_roles = role_member is not None and role_mod is not None and role_mute is not None
            has_channels = channel_modchat is not None   \
                       and channel_entryway is not None   \
                       and channel_unifiedchat is not None \
                       and channel_banskicks is not None    \
                       and channel_filtercatches is not None \
                       and channel_botmessages is not None
            if has_roles and has_channels:
                server_roles = ServerRoles(role_member, role_mod, role_mute)
                server_channels = ServerChannels(channel_modchat,
                                                 channel_entryway,
                                                 channel_unifiedchat,
                                                 channel_banskicks,
                                                 channel_filtercatches,
                                                 channel_botmessages)
                self.servers[guild.id] = ServerInfo(server_roles, server_channels)
                print(f"{guild.name} loaded!")
            else:
                print(f"{guild.name} not loaded as it is missing necessary roles / channels")

        for term in self.config["filter"]["soft"]:
            self.filter_soft.append(re.compile(term))

        for term in self.config["filter"]["hard"]:
            self.filter_hard.append(re.compile(term))

        self.loaded = True
        print("loaded!")

    async def log_unified(self, channel: discord.TextChannel, text: str):
        pass

if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
        bot = EternalGuardian(config, intents = discord.Intents.all())
        bot.run(config["token"])