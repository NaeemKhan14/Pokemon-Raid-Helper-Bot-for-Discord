import discord
import os
from discord.ext import commands
import sqlite3


class RaidHelper(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        # Create the DB table if it does not exist on startup
        db = sqlite3.connect('RaidHelper.sqlite').cursor()
        db.execute(
            '''
            CREATE TABLE IF NOT EXISTS HostInfo 
            (
                user_id	INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_name INTEGER NOT NULL,
                PRIMARY KEY(user_id)
            )
            ''')
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS MutedUsers (
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                user_discriminator TEXT NOT NULL,
                PRIMARY KEY(user_id)
            )
            """
        )
        db.close()
        print('RaidHelper cog is loaded.')

    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def delete(self, ctx):

        # Get user data from DB
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute(f'SELECT * FROM HostInfo WHERE user_id = {ctx.message.author.id}').fetchone()

        # If there is any data, it means the user has a channel which can be deleted
        if row:
            await ctx.guild.get_channel(row[2]).delete()
            await ctx.send("Channel " + row[3] + " has been deleted")
            # Remove user data from DB
            cursor.execute(f'DELETE FROM HostInfo WHERE user_id = {row[0]}')
            db.commit()
        else:
            await ctx.message.channel.send('You do not have any channel created.')
        cursor.close()
        db.close()

    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def create(self, ctx, chan_name=''):

        # If channel name is given
        if chan_name:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT user_id FROM HostInfo WHERE user_id = {ctx.message.author.id}').fetchone()
            # Empty row data means user does not already have a channel created
            if row is None:
                # Delete the user message and send an embed to the channel
                await ctx.message.delete()
                await ctx.message.channel.send(
                    embed=discord.Embed().set_author(name="Channel named '" + chan_name + "' has been created.",
                                                     icon_url='https://cdn.discordapp.com/attachments/662128235982618635/704757893798428732/SeekPng.com_green-tick-icon-png_3672259.png'))
                # Create a new channel based on category
                category = discord.utils.get(ctx.guild.categories, name='Text Channels')
                new_chan = await ctx.guild.create_text_channel(chan_name, category=category)
                # Set permissions for the user in this new channel
                await new_chan.set_permissions(ctx.message.author, manage_messages=True)
                # Setup and command list
                command_embed = discord.Embed().set_author(name='List of Commands',
                                                           icon_url='https://cdn.discordapp.com/attachments/704174855813070901/705216533923889263/491Darkrai.png')
                command_embed.add_field(name='$mute', value='Used to mute a player', inline=False)
                command_embed.add_field(name='$unmute', value='Used to unmute a player', inline=False)
                command_embed.add_field(name='$ban', value='Used to ban a player from the channel', inline=False)
                command_embed.add_field(name='$unban', value='Used to unban a player from the channel', inline=False)
                command_embed.add_field(name='$delete', value='Used to delete your channel', inline=False)
                await new_chan.send(embed=command_embed)
                # Write user and channel info into DB for later use
                cursor.execute(
                    """
                    INSERT INTO HostInfo (user_id, user_name, channel_id, channel_name) VALUES (?, ?, ?, ?)
                    """,
                    (ctx.message.author.id, ctx.message.author.display_name, new_chan.id, new_chan.name))
                db.commit()
            else:
                await ctx.message.channel.send('You already have created channel created.')
            cursor.close()
            db.close()
        else:
            input_name_embed = discord.Embed(
                description='<:x_:705214517961031751> Please input a name for the channel after the command.')
            await ctx.message.channel.send(embed=input_name_embed)

    # Mute player
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def mute(self, ctx, member: discord.Member):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        host_row = cursor.execute(
            f'SELECT * FROM HostInfo WHERE user_id = {ctx.message.author.id} AND channel_id={ctx.message.channel.id}').fetchone()

        # Check if the host has permissions to mute users in this channel
        if host_row:
            channel = ctx.guild.get_channel(host_row[2])
            muted_users_row = cursor.execute(f'SELECT * FROM MutedUsers WHERE user_id = {member.id}').fetchone()
            # Check if user is already muted or not
            if not muted_users_row:
                await ctx.message.delete()
                await channel.set_permissions(member, send_messages=False)
                await channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795> **Darkrai used Disable.** ***' + member.display_name +
                                " no longer has permission to speak.***"))
                cursor.execute(
                    """
                    INSERT INTO MutedUsers (user_id, user_name, user_discriminator) VALUES (?, ?, ?)
                    """,
                    (member.id, member.display_name, member.discriminator))
                db.commit()
            else:  # If user is already muted
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> **Darkrai used Disable.** ***' + member.display_name
                                + " already has no permission to speak.***"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751> User not available or you do not have permissions in this channel'))
        cursor.close()
        db.close()

    # Unmute player
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def unmute(self, ctx):
        if ctx.message.mentions[0].permissions_in(
                self.new_chan).send_messages and self.channel_creator == ctx.message.author and ctx.channel == self.new_chan:
            await ctx.message.delete()
            unmuted_embed = discord.Embed(
                description='<:x_:705214517961031751> **Disable has already worn off for** ***' + ctx.message.mentions[
                    0].name + "***")
            await self.new_chan.send(embed=unmuted_embed)
        elif self.channel_creator == ctx.message.author and ctx.channel == self.new_chan:
            await self.new_chan.set_permissions(ctx.message.mentions[0], send_messages=True)
            await ctx.message.delete()
            disable_off_embed = discord.Embed(
                description='<:SeekPng:705124992349896795> **Disable has worn off for** ***' + ctx.message.mentions[
                    0].name + " and they are now able to speak.***")
            await self.new_chan.send(embed=disable_off_embed)

    # Ban player from channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def ban(self, ctx):
        if self.channel_creator == ctx.message.author:
            await ctx.message.delete()
            ban_embed = discord.Embed(
                description='<:blackhole:705225042052644915> **Darkrai used Dark Void.** ***' + ctx.message.mentions[
                    0].mention + " has been banished to the void.***")
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
