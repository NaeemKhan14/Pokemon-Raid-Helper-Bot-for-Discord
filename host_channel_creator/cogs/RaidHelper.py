import discord
import os
from discord.ext import commands


class RaidHelper(commands.Cog, discord.Client):
    # Class variables
    channel_creator = None
    new_chan = None
    bot_user = None



    def __init__(self, client):
        self.client = client
        self.bot_user = client.user

    @commands.Cog.listener()
    async def on_ready(self):
        print('RaidHelper cog is loaded.')

    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def create(self, ctx, chan_name=''):
        if ctx.message.author == self.bot_user:
            return
        # If channel name is given
        if chan_name:
            self.channel_creator = ctx.message.author
            # Delete the user message and send an embed to the channel
            await ctx.message.delete()
            await ctx.message.channel.send(
                embed=discord.Embed().set_author(name="Channel named '" + chan_name + "' has been created.",
                                                 icon_url='https://cdn.discordapp.com/attachments/662128235982618635/704757893798428732/SeekPng.com_green-tick-icon-png_3672259.png'))
            # Create a new channel based on category
            category = discord.utils.get(ctx.guild.categories, name='Text Channels')
            self.new_chan = await ctx.guild.create_text_channel(chan_name, category=category)
            await self.new_chan.edit(overwrites=None)

            # Setup and command list
            commandembed = discord.Embed().set_author(name='List of Commands', icon_url='https://cdn.discordapp.com/attachments/704174855813070901/705216533923889263/491Darkrai.png')
            commandembed.add_field(name='$mute', value='Used to mute a player', inline=False)
            commandembed.add_field(name='$unmute', value='Used to unmute a player', inline=False)
            commandembed.add_field(name='$ban', value='Used to ban a player from the channel', inline=False)
            commandembed.add_field(name='$unban', value='Used to unban a player from the channel', inline=False)
            await self.new_chan.send(embed=commandembed)

            # Set permissions for the user in this new channel
            await self.new_chan.set_permissions(self.channel_creator, manage_messages=True)
        else:
            inputnameembed = discord.Embed(description='<:x_:705214517961031751> Please input a name for the channel after the command.')
            await ctx.message.channel.send(embed=inputnameembed)

    # Mute player
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def mute(self, ctx):
        if ctx.message.mentions[0].permissions_in(self.new_chan).send_messages and self.channel_creator == ctx.message.author and ctx.channel == self.new_chan:
            await self.new_chan.set_permissions(ctx.message.mentions[0], send_messages=False)
            await ctx.message.delete()
            disableembed = discord.Embed(description='<:SeekPng:705124992349896795> **Darkrai used Disable.** ***' + ctx.message.mentions[0].name + " no longer has permission to speak.***")
            await self.new_chan.send(embed=disableembed)
        elif self.channel_creator == ctx.message.author and ctx.channel == self.new_chan:
            await ctx.message.delete()
            mutedembed = discord.Embed(description='<:x_:705214517961031751> **Darkrai used Disable.** ***' + ctx.message.mentions[0].name + " already has no permission to speak.***")
            await ctx.message.channel.send(embed=mutedembed)
        # Need to add check for if member is already muted.


    # Unmute player
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def unmute(self, ctx):
        if ctx.message.mentions[0].permissions_in(self.new_chan).send_messages and self.channel_creator == ctx.message.author and ctx.channel == self.new_chan:
            await ctx.message.delete()
            unmutedembed = discord.Embed(description='<:x_:705214517961031751> **Disable has already worn off for** ***' + ctx.message.mentions[0].name + "***")
            await self.new_chan.send(embed=unmutedembed)
        elif self.channel_creator == ctx.message.author and ctx.channel == self.new_chan:
            await self.new_chan.set_permissions(ctx.message.mentions[0], send_messages=True)
            await ctx.message.delete()
            disableoffembed = discord.Embed(description='<:SeekPng:705124992349896795> **Disable has worn off for** ***' + ctx.message.mentions[0].name + " and they are now able to speak.***")
            await self.new_chan.send(embed=disableoffembed)


    # Ban player from channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def ban(self, ctx):
        if self.channel_creator == ctx.message.author:
            await ctx.message.delete()
            banembed = discord.Embed(description='<:blackhole:705225042052644915> **Darkrai used Dark Void.** ***' + ctx.message.mentions[0].mention + " has been banished to the void.***")
            await self.new_chan.send(
                'Darkrai used Dark Void. ' + ctx.message.mentions[0].mention + " has been banished to the void.")
            await self.new_chan.set_permissions(ctx.message.mentions[0], read_messages=False)


    # Unban player from channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def unban(self, ctx):
        if self.channel_creator == ctx.message.author:
            await ctx.message.delete()
            await self.new_chan.set_permissions(ctx.message.mentions[0], read_messages=True)
            await self.new_chan.send(
                ctx.message.mentions[0].mention + " has been pardoned and released from the void.")


def setup(client):
    client.add_cog(RaidHelper(client))
