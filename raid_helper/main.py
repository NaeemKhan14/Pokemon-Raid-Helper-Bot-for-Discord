import os
import discord
from discord.ext import commands
import sys
sys.path.insert(0, "C:/Users/Eric/Desktop/Pokemon-Raid-Helper-Bot-for-Discord/raid_helper")

TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix='$', case_insensitive=True)

client.remove_command('help')

@client.command()
@commands.has_role('Owner')
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print(f'{extension} has been reloaded')
    await ctx.message.delete()

# Initially load all the cogs on startup
for file in os.listdir('./cogs'):
    if file.endswith('.py'):
        client.load_extension(f'cogs.{file[:-3]}')

client.run(TOKEN)
