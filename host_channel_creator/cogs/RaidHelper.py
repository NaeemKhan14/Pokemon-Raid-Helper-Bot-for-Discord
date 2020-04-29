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

            # Set permissions for the user in this new channel
            await self.new_chan.set_permissions(self.channel_creator, manage_messages=True)
        else:
            await ctx.message.channel.send('Please input a name for the channel after the command.')

    # Mute player
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def mute(self, ctx):
        if self.channel_creator == ctx.message.author:
            await self.new_chan.set_permissions(ctx.message.mentions[0], send_messages=False)
            await ctx.message.delete()
            await self.new_chan.send(
                'Darkrai used Disable. ' + ctx.message.mentions[0].mention + " no longer has permission to speak.")
            # This embed needs proper permission checking
            #alreadymutedembeed.set_author(name=ctx.message.mentions[0] + ' is already muted.',
            #                              icon_url='https://cdn.discordapp.com/attachments/704174855813070901/704762398896160818/CoolyDrinksPiss.png')
        # Need to add check for if member is already muted.
        else:
            await ctx.message.channel.send(embed=nopermembed)  # Error message

    # Unmute player
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def unmute(self, ctx):
        if self.channel_creator == ctx.message.author:
            await self.new_chan.set_permissions(ctx.message.mentions[0], send_messages=True)
            await ctx.message.delete()
            await self.new_chan.send(
                'Disable has worn off for ' + ctx.message.mentions[0].mention + " and they are now able to speak.")
        else:
            await ctx.message.channel.send(embed=nopermembed)  # Error message

    # Ban player from channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def ban(self, ctx):
        if self.channel_creator == ctx.message.author:
            await ctx.message.delete()
            await self.new_chan.send(
                'Darkrai used Dark Void. ' + ctx.message.mentions[0].mention + " has been banished to the void.")
            await self.new_chan.set_permissions(ctx.message.mentions[0], read_messages=False)
        else:
            await ctx.message.channel.send(embed=nopermembed)  # Error message

    # Unban player from channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def unban(self, ctx):
        if self.channel_creator == ctx.message.author:
            await ctx.message.delete()
            await self.new_chan.set_permissions(ctx.message.mentions[0], read_messages=True)
            await self.new_chan.send(
                ctx.message.mentions[0].mention + " has been pardoned and released from the void.")
        else:
            await ctx.message.channel.send(embed=nopermembed)  # Error message


def setup(client):
    client.add_cog(RaidHelper(client))
