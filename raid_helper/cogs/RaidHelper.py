import discord
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
        db.execute("""CREATE TABLE IF NOT EXISTS MutedUsers AS SELECT * FROM HostInfo""")
        db.execute("""CREATE TABLE IF NOT EXISTS BannedUsers AS SELECT * FROM HostInfo""")
        db.close()
        print('RaidHelper cog is loaded.')

    # Create a channel
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
                await ctx.message.channel.send(
                    embed=discord.Embed().set_author(name="Channel named " + chan_name + " has been created.",
                                                     icon_url='https://cdn.discordapp.com/attachments/662128235982618635/704757893798428732/SeekPng.com_green-tick-icon-png_3672259.png'))
                # Create a new channel based on category
                category = discord.utils.get(ctx.guild.categories, name='Text Channels')
                new_chan = await ctx.guild.create_text_channel(chan_name, category=category)
                # Set permissions for the user in this new channel
                await new_chan.set_permissions(ctx.message.author, manage_messages=True)
                # Setup and command list
                help_embed = discord.Embed(title=f"Welcome to {chan_name}",
                                           description="Following are the available bot commands that you can use. Please note that all commands must be executed from this channel.",
                                           color=0x74729e)
                help_embed.set_thumbnail(url="https://i.imgur.com/p146gWE.png")
                help_embed.add_field(name="$mute @username", value="Revokes the user's right to speak in this channel.",
                                     inline=False)
                help_embed.add_field(name="$unmute @username", value="Allows the user to speak in this channel again.",
                                     inline=False)
                help_embed.add_field(name="$ban @username", value="Removes the user from this channel.", inline=False)
                help_embed.add_field(name="$unban @username",
                                     value="Allows the user to join this channel again. Please note that you must provide the username along with the user discriminator. For example: $unban @User Name#9001.",
                                     inline=False)
                help_embed.add_field(name="$delete",
                                     value="Removes this room permanently along with all the messages/users.",
                                     inline=False)
                help_embed.set_footer(text="Don't forget to delete this channel once you are finished hosting!")
                await new_chan.send(embed=help_embed)
                # Write user and channel info into DB for later use
                cursor.execute(
                    """INSERT INTO HostInfo (user_id, user_name, channel_id, channel_name) VALUES (?, ?, ?, ?)""",
                    (ctx.message.author.id, ctx.message.author.display_name, new_chan.id, new_chan.name))
                db.commit()
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description=
                    '<:x_:705214517961031751> **You already have a channel created.**'))
            cursor.close()
            db.close()
        else:
            input_name_embed = discord.Embed(
                description='<:x_:705214517961031751> **Invalid syntax. Please provide a name after the command. Example:** ***$create channelname***')
            await ctx.message.channel.send(embed=input_name_embed)
        await ctx.message.delete()

    # Delete a channel
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
            # Remove user data from DB
            cursor.execute(f'DELETE FROM HostInfo WHERE user_id = {row[0]}')
            db.commit()
        else:
            await ctx.message.channel.send('**You do not have any channels created.**')
        cursor.close()
        db.close()

        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass

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
            muted_users_row = cursor.execute(
                f'SELECT * FROM MutedUsers WHERE user_id = {member.id} AND channel_id = {ctx.message.channel.id}').fetchone()
            # Check if user is already muted or not
            if not muted_users_row:
                await channel.set_permissions(member, send_messages=False)
                await channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795> **Darkrai used Disable.** ***' + member.display_name +
                                "*** **no longer has permission to speak.**"))
                cursor.execute(
                    """INSERT INTO MutedUsers (user_id, user_name, channel_id, channel_name) VALUES (?, ?, ?, ?)""",
                    (member.id, member.display_name, ctx.message.channel.id, ctx.message.channel.name))
                db.commit()
            else:  # If user is already muted
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> **Darkrai used Disable.** ***' + member.display_name
                                + "*** **already has no permission to speak.**"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751> **User not available or you do not have permissions in this channel.**'))
        cursor.close()
        db.close()
        await ctx.message.delete()

    # Unmute player
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def unmute(self, ctx, member: discord.Member):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        host_row = cursor.execute(
            f'SELECT * FROM HostInfo WHERE user_id = {ctx.message.author.id} AND channel_id={ctx.message.channel.id}').fetchone()

        # Check if the host has permissions to mute users in this channel
        if host_row:
            channel = ctx.guild.get_channel(host_row[2])
            muted_users_row = cursor.execute(
                f'SELECT * FROM MutedUsers WHERE user_id = {member.id} AND channel_id = {ctx.message.channel.id}').fetchone()
            # Check if user is already muted or not
            if muted_users_row:
                await channel.set_permissions(member, send_messages=True)
                await channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795> **Disable has worn off for** ***' + member.display_name +
                                "*** **and they are now able to speak.**"))
                cursor.execute(f'DELETE FROM MutedUsers WHERE user_id = {member.id}')
                db.commit()
            else:  # If user is already muted
                await channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795> **Disable is not active for** ***' + member.display_name +
                                "*** **and they are already allowed to speak.**"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751> **User not available or you do not have permissions in this channel.**'))
        cursor.close()
        db.close()
        await ctx.message.delete()

    # Ban player from channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def ban(self, ctx, member: discord.Member):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        host_row = cursor.execute(
            f'SELECT * FROM HostInfo WHERE user_id = {ctx.message.author.id} AND channel_id={ctx.message.channel.id}').fetchone()

        # Check if the host has permissions to ban users in this channel
        if host_row:
            channel = ctx.guild.get_channel(host_row[2])
            banned_users_row = cursor.execute(
                f'SELECT * FROM MutedUsers WHERE user_id = {member.id} AND channel_id = {ctx.message.channel.id}').fetchone()
            # Check if user is already banned or not
            if not banned_users_row:
                await channel.set_permissions(member, read_messages=False)
                await channel.send(embed=discord.Embed(
                    description='<:blackhole:705225042052644915> **Darkrai used Dark Void.** ***' +
                                member.display_name + "*** **has been banished to the void.**"))
                cursor.execute(
                    """INSERT INTO BannedUsers (user_id, user_name, channel_id, channel_name) VALUES (?, ?, ?, ?)""",
                    (member.id, member.display_name, ctx.message.channel.id, ctx.message.channel.name))
                db.commit()
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751> **User not available or you do not have permissions in this channel.**'))
        cursor.close()
        db.close()
        await ctx.message.delete()

    # Unban player from channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def unban(self, ctx, user):
        member = discord.utils.get(ctx.message.guild.members, id=int(user[3:-1]))
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        host_row = cursor.execute(
            f'SELECT * FROM HostInfo WHERE user_id = {ctx.message.author.id} AND channel_id={ctx.message.channel.id}').fetchone()

        # Check if the host has permissions to unban users in this channel
        if host_row:
            channel = ctx.guild.get_channel(host_row[2])
            banned_users_row = cursor.execute(
                f'SELECT * FROM BannedUsers WHERE user_id = {member.id} AND channel_id = {ctx.message.channel.id}').fetchone()
            # Check if user is already banned or not
            if banned_users_row:
                await channel.set_permissions(member, read_messages=True)
                await channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795> ***' + member.display_name +
                                "*** **has been pardoned from the void.**"))
                cursor.execute(f'DELETE FROM BannedUsers WHERE user_id = {member.id}')
                db.commit()
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> ***' + member.display_name +
                                "*** **was never previously banned here.**"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751> **User not available or you do not have permissions in this channel.**'))
        cursor.close()
        db.close()
        await ctx.message.delete()


def setup(client):
    client.add_cog(RaidHelper(client))
