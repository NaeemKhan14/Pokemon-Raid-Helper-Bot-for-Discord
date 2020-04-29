import os
import discord
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')  # Discord Token

client = commands.Bot(command_prefix='$')


@client.command()
@commands.has_role('admin')
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
@commands.has_role('admin')
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
@commands.has_role('admin')
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')

# Initially load all the cogs on startup
for file in os.listdir('./cogs'):
    if file.endswith('.py'):
        client.load_extension(f'cogs.{file[:-3]}')

client.run(TOKEN)
