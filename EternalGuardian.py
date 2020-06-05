# EternalGuardian originally designed by PyroL for the roguelikes Discord server https://discord.gg/9pmFGKx 

import discord # requires installing discord.py, see https://discordpy.readthedocs.io/en/latest/intro.html#installing
from discord.ext import commands

import random
import asyncio
import datetime

# the following files not included on github, must be manually created after cloning
from EGKeys import TOKEN
from banned_words import banned_list

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
    global EGguild, EGwelcome_channel, EGmod_channel, EGverified_role, EGcaptcha
    EGguild = discord.utils.get(client.guilds, id = 205277826788622337)
    EGwelcome_channel = discord.utils.get(EGguild.text_channels, id = 533125618309529620)
    EGmod_channel = discord.utils.get(EGguild.text_channels, id = 207537092467621889)
    EGverified_role = discord.utils.get(EGguild.roles, name = 'Adventurer')
    EGcaptcha = 'a wizard lizard with a gizzard in a blizzard'

@client.event
async def on_message(message):
    if message.author != client.user: # ignores its own messages
        if message.channel == EGwelcome_channel: # captcha verification
            if message.content == EGcaptcha:
                await message.channel.send('captcha successful', delete_after=3.0)
                await message.author.add_roles(EGverified_role)
            else:
                await message.channel.send('captcha failed',delete_after=3.0)
            await message.delete()

        for word in banned_list: # censored words
            if word in message.content.lower():
                print(str(message.channel))
                if not message.channel == EGmod_channel:
                    print('Slur detected {} '.format(str(message.channel)))
                    # notifies mod channel if a slur is detected
                    await EGmod_channel.send('Slur detected in #{0} by user {1}.'.format(message.channel, message.author.mention))
                    await EGmod_channel.send('`{}`'.format(message.content))
                    
        if 'rougelike' in message.content.lower(): 
            await message.channel.send('It\'s spelled *rogue*like.')
    await client.process_commands(message)

@client.command() # echo command
async def echo(ctx, *, text : str):
    print(text)
    await ctx.send(text)

@client.command(name = "kick") # kick command
@commands.has_permissions(manage_roles=True, ban_members=True)
async def _kick(ctx, member : discord.Member):
    await member.kick()
    await ctx.send('Kicked')

@client.command(name = "ban") # ban command 
@commands.has_permissions(manage_roles=True, ban_members=True)
async def _ban(ctx, member : discord.Member):
    await ctx.send('{0} just got SokoBanned!'.format(ctx.author.mention))
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
