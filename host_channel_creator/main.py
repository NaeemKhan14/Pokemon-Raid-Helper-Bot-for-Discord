import os
import discord
from discord.ext import commands


TOKEN = 'NzA0MTc0OTg3NTYwNjE2MDU3.XqZWlA.6tdYxAYNBEU_-95AK8-LalJmxyo'  # Discord Token
catename = 'Text Channels'  # Name of category you want channels made in


client = commands.Bot(command_prefix='$')


createembed = discord.Embed()


alreadymutedembeed = discord.Embed()


discord.CustomActivity('Banishing players to the void.', emoji=None)


@client.event
async def on_ready():
    print('Bot is ready.')


# Create a channel
@client.command()
@commands.has_role('Shiny Raid Host')
async def create(ctx, *, name=None):
    if ctx.message.author == client.user:
        return
    if name is not None:
        global channel_creator
        channel_creator = ctx.message.author
        await ctx.message.delete()
        createembed.set_author(name="Channel named '" + name + "' has been created.", icon_url='https://cdn.discordapp.com/attachments/662128235982618635/704757893798428732/SeekPng.com_green-tick-icon-png_3672259.png')
        await ctx.message.channel.send(embed=createembed)
        category = discord.utils.get(ctx.guild.categories, name=catename)
        global newchan
        newchan = await ctx.guild.create_text_channel(name, category=category)
        # Set permissions for the user in this new channel
        await newchan.set_permissions(channel_creator, manage_messages=True)
    elif name is None:
        await ctx.message.channel.send('Please input a name for the channel after the command.')


# Mute player
@client.command()
@commands.has_role('Shiny Raid Host')
async def mute(ctx):
    if channel_creator == ctx.message.author:
        await newchan.set_permissions(ctx.message.mentions[0], send_messages=False)
        await ctx.message.delete()
        await ctx.message.channel.send(
            'Darkrai used Disable. ' + ctx.message.mentions[0].mention + " no longer has permission to speak.")
    elif:
        alreadymutedembeed.set_author(name=ctx.message.mentions[0] + ' is already muted.', icon_url='https://cdn.discordapp.com/attachments/704174855813070901/704762398896160818/CoolyDrinksPiss.png')
    # Need to add check for if member is already muted.


# Unmute player
@client.command()
@commands.has_role('Shiny Raid Host')
async def unmute(ctx):
    if channel_creator == ctx.message.author:
        await newchan.set_permissions(ctx.message.mentions[0], send_messages=True)
        await ctx.message.delete()
        await message.channel.send(
            'Disable has worn off for ' + message.mentions[0].mention + " and they are now able to speak.")
    else:
        await ctx.message.channel.send(embed=nopermembed)  # Error message


# Ban player from channel
@client.command()
@commands.has_role('Shiny Raid Host')
async def ban(ctx):
    if channel_creator == ctx.message.author:
        await ctx.message.delete()
        await newchan.send(
            'Darkrai used Dark Void. ' + message.mentions[0].mention + " has been banished to the void.")
        await newchan.set_permissions(message.mentions[0], read_messages=False)
    else:
        await ctx.message.channel.send(embed=nopermembed)  # Error message


# Unban player from channel
@client.command()
@commands.has_role('Shiny Raid Host')
async def unban(ctx):
    if channel_creator == ctx.message.author:
        await ctx.message.delete()
        await newchan.set_permissions(message.mentions[0], read_messages=True)
        await newchan.send(
            message.mentions[0].mention + " has been pardoned and released from the void.")
    else:
        await ctx.message.channel.send(embed=nopermembed)  # Error message







client.run(TOKEN)
