import discord
import random
from discord.ext import commands
from EGKeys import TOKEN

client = commands.Bot(command_prefix='&')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event # captcha
async def on_message(message):
    if message.channel == 533125618309529620:
        await message.channel.send('You at least got the channel right.')
        if message == 'a wizard lizard with a gizzard in a blizzard':
            await message.channel.send('captcha successful')
            await message.author.add_roles(discord.utils.get(message.guild.roles,  name = "Adventurer"))
            await message.delete()
    if 'rougelike' in message:
        message.channel.send('It\s spelled *rogue*like.')
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
async def ban(member):
    await member.ban()
    
@client.event
async def on_error(error, ctx):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You sense the mods are displeased...')


client.run(TOKEN)