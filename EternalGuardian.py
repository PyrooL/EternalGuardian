import discord
import random
import asyncio
import datetime
from discord.ext import commands
from EGKeys import TOKEN

welcome_channel = discord.utils.get(discord.guild.channels, name='the-door')
client = commands.Bot(command_prefix='&')
captcha = 'a wizard lizard with a gizzard in a blizzard'

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def captcha_instructions():
    await client.wait_until_ready()
    if datetime.datetime.now().hour == 0:
        welcome_channel.send('Welcome, Adventurer! To verify you\'re not a bot, please type the captcha: \"{}\"'.format(captcha))


@client.event # captcha
async def on_message(message):
    if message.channel == welcome_channel:
        await message.channel.send('You at least got the channel right.', delete_after=3.0)
        if message.content == captcha:
            await message.channel.send('captcha successful', delete_after=3.0)
            verified_role = discord.utils.get(message.guild.roles,  name = "Adventurer")
            print(verified_role)
            await message.author.add_roles(verified_role)
            await message.delete()
    if 'rougelike' in message.content:
        await message.channel.send('It\'s spelled *rogue*like.')
    if 'nigg' in message.content:
        await message.author.ban()
        await 
    await client.process_commands(message)

@client.command()
async def echo(ctx, *, text : str):
    await ctx.send(text)

@client.command(name = "kick")
@commands.has_permissions(manage_roles=True, ban_members=True)
async def _kick(ctx, member : discord.Member):
    await member.kick()
    await ctx.send('Kicked')

@client.command()
@commands.has_permissions(manage_roles=True, ban_members=True)
async def ban(ctx, member : discord.Member):
    await ctx.send('{0} just got SokoBanned!'.format(ctx.author.mention))
    await member.ban()

@client.event
async def on_error(error, ctx):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You\'re not high enough level to do that...')


client.run(TOKEN)