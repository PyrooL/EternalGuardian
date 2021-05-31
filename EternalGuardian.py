# EternalGuardian originally designed by PyroL for the roguelikes Discord server https://discord.gg/9pmFGKx 

import discord # requires installing discord.py, see https://discordpy.readthedocs.io/en/latest/intro.html#installing
from discord.ext import commands

import random
import asyncio
import datetime

# the following files not included on github, must be manually created after cloning
from EGKeys import TOKEN
from banned_words import *

client = commands.Bot(command_prefix='&')

@client.event
async def on_ready():
    # initializing messages in console
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(datetime.datetime.now())
    print('------') 

    # replace with new IDs if using in a different server
    global EGguild, EGwelcome_channel, EGmod_channel, EGverified_role, EGcaptcha, EGmute_role, EGlog_channel
    EGguild = discord.utils.get(client.guilds, id = 205277826788622337)
    EGwelcome_channel = discord.utils.get(EGguild.text_channels, id = 533125618309529620)
    EGmod_channel = discord.utils.get(EGguild.text_channels, id = 207537092467621889)
    EGlog_channel = discord.utils.get(EGguild.text_channels, id = 261352132496588800)
    EGverified_role = discord.utils.get(EGguild.roles, name = 'Adventurer')
    EGmute_role = discord.utils.get(EGguild.roles, name = 'Mute')

    EGcaptcha = 'a wizard lizard with a gizzard in a blizzard'

@client.event
async def on_member_join(member):
    for word in insta:
        if word in member.name.lower():
            await EGmod_channel.send('Autobanned user ||'+member.mention+'|| on join.')
            await member.ban()
            break

@client.event
async def on_member_update(before,after):
    if after.nick != before.nick:
        await EGlog_channel.send('{0} updated their nickname to {1}.'.format(before.display_name,after.display_name))
        for word in insta:
            if after.nick != None:
                if word in after.nick.lower():
                    await EGmod_channel.send('Autobanned user ||'+after.mention+'|| on nickname update.')
                    await after.ban()
                    break

@client.event
async def on_user_update(before,after):
    if after.name != before.name:
        await EGlog_channel.send('#{0} updated their global username to {1}.'.format(before.mention,after.name))
        for word in insta:
            if word in after.name.lower():
                await EGmod_channel.send('Autobanned user ||'+after.mention+'|| on global name update.')
                member = discord.utils.get(EGguild.members, id = after.id) # i think this is how you have to handle the distinction between member and user, see discord.py docs
                await member.ban()
                break

@client.event
async def on_message(message):
    if message.author != client.user: # ignores its own messages
        if message.channel == EGwelcome_channel: # captcha verification
            if message.content == EGcaptcha:
                await message.channel.send('captcha successful', delete_after=3.0)
                print("Captcha sucessful, " + datetime.datetime.now()) 
                await message.author.add_roles(EGverified_role)
                print("User verified: {0}#{1}".format(message.author.name, message.author.id))
                print(message.author.id)
            else:
                await message.channel.send('captcha failed',delete_after=3.0)
                print("Captcha failed " + datetime.datetime.now())
            await message.delete()

        for word in insta: # instant ban/mute words
            if word in message.content.lower():
                if not message.channel == EGmod_channel:
                    print('Auto mute in {} '.format(str(message.channel)))
                    await message.author.add_roles(EGmute_role)
                    await message.channel.send('Automatically muted :oncoming_police_car:')
                    await EGmod_channel.send('@Mod Auto-mute in #{0} by user ||{1}||. Message content: ||{2}||'.format(message.channel, message.author.mention, message.content))
                    await EGmod_channel.send(message.jump_url)

        for word in banned_list: # censored words
            if word in message.content.lower():
                if message.channel != EGmod_channel:
                    print('Slur detected {} '.format(str(message.channel)))
                    # notifies mod channel if a slur is detected
                    await EGmod_channel.send('@here Slur detected in #{0} by user {1}. Message content: ||{2}||'.format(message.channel, message.author.mention, message.content))
                    await EGmod_channel.send(message.jump_url)

      
        if 'rougelike' in message.content.lower(): 
            await message.channel.send('It\'s spelled *rogue*like.')
    await client.process_commands(message)

#-------COMMANDS-------

@client.command() # echo command
async def echo(ctx, *, text : str):
    print('ECHO '+text)
    await ctx.send(text)

@client.command(name = "kick") # kick command
@commands.has_permissions(manage_roles=True, ban_members=True)
async def _kick(ctx, member : discord.Member):
    await member.kick()
    await ctx.send('Kicked')

@client.command(name = "ban") # ban command 
@commands.has_permissions(manage_roles=True, ban_members=True)
async def _ban(ctx, member : discord.Member):
    await ctx.send('{0} just got SokoBanned! :banhammer:'.format(ctx.author.mention))
    await member.ban()

@client.command() # admin-only command to add the Adventurer role to everyone, outputs progress to log, takes time because of rate limiting
@commands.has_permissions(administrator=True)
async def verifyall(ctx):
    for vmember in ctx.guild.members:
        if EGverified_role not in vmember.roles:
            await vmember.add_roles(EGverified_role)
            if EGverified_role in vmember.roles:
                print('{0} is verified'.format(vmember.name))
    await ctx.send('all members verfied')

@client.command() # command that locks the channel
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    print(ctx.channel+' locked')
    await ctx.channel.set_permissions(EGverified_role, send_messages=False)

@client.command() # command that unlocks the channel
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(EGverified_role, send_messages=True)

@client.command() # links source
async def source(ctx):
    await ctx.send('https://github.com/PyrooL/EternalGuardian')

@client.command() # member count
async def members(ctx):
    await ctx.send(str(ctx.guild.member_count))

@client.event # error handling
async def on_error(ctx,error):
    if isinstance(error, commands.CommandNotFound):  # fails silently
        pass
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You\'re not high enough level to do that...')

client.run(TOKEN)
