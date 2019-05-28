import discord
from discord.ext import commands

import random
import asyncio
import datetime
from EGKeys import TOKEN

client = commands.Bot(command_prefix='&')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(datetime.datetime.now())
    print('------') 

    global EGguild, EGwelcome_channel, EGmod_channel, EGverified_role, EGcaptcha
    EGguild = discord.utils.get(client.guilds, id = 205277826788622337)
    EGwelcome_channel = discord.utils.get(EGguild.text_channels, id = 533125618309529620)
    EGmod_channel = discord.utils.get(EGguild.text_channels, id = 207537092467621889)
    EGverified_role = discord.utils.get(EGguild.roles, name = 'Adventurer')
    EGcaptcha = 'a wizard lizard with a gizzard in a blizzard'

@client.event
async def on_message(message):
    banned_list = ['nigg', 'chink', 'noxico']
    for word in banned_list:
        if word in message.content.lower():
            print(str(message.channel))
            if not message.channel == EGmod_channel
                print('Slur detected {} '.format(message.channel)+str(datetime.datetime.now)
                await EGmod_channel.send('Slur detected in #{0} by user {1}.'.format(message.channel,message.author.mention))
                await EGmod_channel.send('`{}`'.format(message.content))
    if not message.author == client.user:
        if message.channel == EGwelcome_channel:
            if message.content == EGcaptcha:
                await message.channel.send('captcha successful', delete_after=3.0)
                await message.author.add_roles(EGverified_role)
            else:
                await message.channel.send('captcha failed',delete_after=3.0)
            await message.delete()

        if 'rougelike' in message.content.lower():
            await message.channel.send('It\'s spelled *rogue*like.')
    await client.process_commands(message)

@client.command()
async def echo(ctx, *, text : str):
    print(text)
    await ctx.send(text)

@client.command(name = "kick")
@commands.has_permissions(manage_roles=True, ban_members=True)
async def _kick(ctx, member : discord.Member):
    await member.kick()
    await ctx.send('Kicked')

@client.command(name = "ban")
@commands.has_permissions(manage_roles=True, ban_members=True)
async def _ban(ctx, member : discord.Member):
    await ctx.send('{0} just got SokoBanned!'.format(ctx.author.mention))
    await member.ban()

@client.command()
@commands.has_permissions(administrator=True)
async def verifyall(ctx):
    for vmember in ctx.guild.members:
        if EGverified_role not in vmember.roles:
            await vmember.add_roles(EGverified_role)
            if EGverified_role in vmember.roles:
                print('{0} is verified'.format(vmember.name))
    await ctx.send('all members verfied')

@client.command()
async def source(ctx):
    await ctx.send('https://github.com/PyrooL/EternalGuardian')

@client.command()
async def members(ctx):
    await ctx.send(str(ctx.guild.member_count))

@client.event
async def on_error(ctx,error):
    if isinstance(error, commands.CommandNotFound):  # fails silently
        pass
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You\'re not high enough level to do that...')

client.run(TOKEN)
