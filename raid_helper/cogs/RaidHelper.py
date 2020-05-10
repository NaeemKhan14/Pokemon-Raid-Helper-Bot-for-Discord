import discord
from discord.ext import commands
import sqlite3
import asyncio
import re

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
        new_chan = None
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
                await new_chan.set_permissions(discord.utils.get(ctx.message.guild.roles, name='@everyone'),
                                               read_messages=False)
                await new_chan.set_permissions(ctx.message.author, manage_messages=True, read_messages=True)
                # Setup command list
                help_embed = discord.Embed(title=f"Welcome to {chan_name}",
                                           description="Following are the available bot commands that you can use. Please note that all commands must be executed from this channel.")
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
                # Sends help embed and pins it
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
        await ctx.guild.get_channel(new_chan.id).last_message.pin()

    # Steps for posting host embed
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('$create'):
            await asyncio.sleep(3)
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT * FROM HostInfo WHERE user_id = {message.author.id}').fetchone()
            onstep1 = True
            if row:
                message1 = await message.guild.get_channel(row[2]).send(embed=discord.Embed(
                    description="Please tell me what Pokemon or den you are hosting (include Gmax if Gmax) along with the nature in parathenses. Feel free to put 'rerolling' and the den # if you are rerolling dens (do not include shininess, gender, etc. only the den/mon and nature). Ex: Eevee (Modest)").set_footer(
                    text=
                    'Step 1/6'))
                while onstep1:

                    def check(msg):
                        return msg.channel == message.guild.get_channel(row[2]) and msg.author.id == row[0]

                    step1 = await self.client.wait_for('message', check=check)
                    step1content = step1.content
                    if 'rerolling' in step1.content:
                        await message.guild.get_channel(row[2]).last_message.delete()
                        await message1.edit(
                            embed=discord.Embed(
                                description="You are **" + step1content + ".** Is this correct? Y/N"))
                    else:
                        await message.guild.get_channel(row[2]).last_message.delete()
                        await message1.edit(
                            embed=discord.Embed(
                                description="You are hosting **" + step1content + ".** Is this correct? Y/N"))

                    def confirmcheck(msg):
                        return msg.channel == message.guild.get_channel(row[2]) and msg.author.id == row[0] and (msg.content == 'y' or msg.content == 'Y' or msg.content == 'n' or msg.content == 'N')
                    confirm = await self.client.wait_for('message', check=confirmcheck)
                    if confirm.content == 'Y' or confirm.content == 'y':
                        await message.guild.get_channel(row[2]).last_message.delete()
                        onstep1 = False
                        onstep2 = True
                        await message1.edit(embed=discord.Embed(
                            description="Please tell me the IVs in XX/XX/XX/XX/XX/XX format. If you are unsure of the IVs simply put 'idk'.").set_footer(
                            text=
                            'Step 2/6'))
                    if confirm.content == 'N' or confirm.content == 'n':
                        await message.guild.get_channel(row[2]).last_message.delete()
                        await message1.edit(embed=discord.Embed(
                            description="Please tell me what Pokemon or den you are hosting (include Gmax if Gmax). Feel free to put 'rerolling' and the den # if you are rerolling dens (do not include shininess, gender, etc. only the den/mon).").set_footer(
                                text=
                                'Step 1/6'))
                while onstep2:
                    step2 = await self.client.wait_for('message', check=check)
                    step2content = step2.content
                    if 'idk' in step2.content or 'Idk' in step2.content:
                        await message.guild.get_channel(row[2]).last_message.delete()
                        step2content = 'Unknown'
                        onstep2 = False
                        onstep3 = True

                    elif re.search("[0-3][0-9][/][0-3][0-9][/][0-3][0-9][/][0-3][0-9][/][0-3][0-9][/][0-3][0-9]", step2content):
                        await message.guild.get_channel(row[2]).last_message.delete()
                        onstep2 = False
                        onstep3 = True
                    else:
                        await message.guild.get_channel(row[2]).last_message.delete()
                        await message1.edit(embed=discord.Embed(
                            description="Incorrect format. Please tell me the IVs in XX/XX/XX/XX/XX/XX format. If you are unsure of the IVs simply put 'idk'.").set_footer(
                            text=
                            'Step 2/6'))
                if onstep3:
                    await message1.edit(embed=discord.Embed(
                        description="React with ⭐ if it is star shiny, 🟧 if it's square shiny, and 🇺 if you are unsure.").set_footer(
                        text=
                        'Step 3/6'))
                    await message1.add_reaction('⭐')
                    await message1.add_reaction('🟧')
                    await message1.add_reaction('🇺')

                    def check2(reaction, user):
                        return user.id == row[0] and reaction.message.id == message1.id and (reaction.emoji == '⭐' or reaction.emoji == '🟧' or reaction.emoji == '🇺')
                    reaction, user = await self.client.wait_for('reaction_add', check=check2)
                    await message1.remove_reaction('⭐', message1.author)
                    await message1.remove_reaction('🟧', message1.author)
                    await message1.remove_reaction('🇺', message1.author)
                    if reaction.emoji == '⭐':
                        step3content = 'Star'
                        await message1.remove_reaction('⭐', user)
                        onstep4 = True
                    elif reaction.emoji == '🟧':
                        step3content = 'Square'
                        await message1.remove_reaction('🟧', user)
                        onstep4 = True
                    elif reaction.emoji == '🇺':
                        step3content = 'Unknown'
                        await message1.remove_reaction('🇺', user)
                        onstep4 = True
                if onstep4:
                    await message1.edit(embed=discord.Embed(
                        description="React with 1\N{combining enclosing keycap} if it is ability 1, 2\N{combining enclosing keycap} if it's ability 2, H if it's hidden ability, and 🇺 if you are unsure.").set_footer(
                        text=
                        'Step 4/6'))
                    await message1.add_reaction('1\N{combining enclosing keycap}')
                    await message1.add_reaction('2\N{combining enclosing keycap}')
                    await message1.add_reaction('🇭')
                    await message1.add_reaction('🇺')

                    def check3(reaction, user):
                        return user.id == row[0] and reaction.message.id == message1.id and (reaction.emoji == '1\N{combining enclosing keycap}' or reaction.emoji == '2\N{combining enclosing keycap}' or reaction.emoji == '🇭' or reaction.emoji == '🇺')
                    reaction, user = await self.client.wait_for('reaction_add', check=check3)
                    await message1.remove_reaction('1\N{combining enclosing keycap}', message1.author)
                    await message1.remove_reaction('2\N{combining enclosing keycap}', message1.author)
                    await message1.remove_reaction('🇭', message1.author)
                    await message1.remove_reaction('🇺', message1.author)

                    if reaction.emoji == '1\N{combining enclosing keycap}':
                        step4content = '1'
                        await message1.remove_reaction('1\N{combining enclosing keycap}', user)
                        onstep5 = True
                    elif reaction.emoji == '2\N{combining enclosing keycap}':
                        step4content = '2'
                        await message1.remove_reaction('2\N{combining enclosing keycap}', user)
                        onstep5 = True
                    elif reaction.emoji == '🇭':
                        step4content = 'Hidden'
                        await message1.remove_reaction('🇭', user)
                        onstep5 = True
                    elif reaction.emoji == '🇺':
                        step4content = 'Unknown'
                        await message1.remove_reaction('🇺', user)
                        onstep5 = True
                if onstep5:
                    await message1.edit(embed=discord.Embed(
                        description="React with ♀ if it is female, ♂ if it's male, and 🇺 if you are unsure.").set_footer(
                        text=
                        'Step 5/6'))
                    await message1.add_reaction('♀')
                    await message1.add_reaction('♂')
                    await message1.add_reaction('🇺')

                    def check4(reaction, user):
                        return user.id == row[0] and reaction.message.id == message1.id and (
                                    reaction.emoji == '♂' or reaction.emoji == '♀' or reaction.emoji == '🇺')

                    reaction, user = await self.client.wait_for('reaction_add', check=check4)
                    await message1.remove_reaction('♀', message1.author)
                    await message1.remove_reaction('♂', message1.author)
                    await message1.remove_reaction('🇺', message1.author)
                    if reaction.emoji == '♀':
                        step5content = 'Female'
                        await message1.remove_reaction('♀', user)
                        onstep6 = True
                        await message1.edit(embed=discord.Embed(
                            description="Please type any custom rules you may have such as no DD or removing off friend's list after hosting.").set_footer(
                            text=
                            'Step 6/6'))
                    elif reaction.emoji == '♂':
                        step5content = 'Male'
                        await message1.remove_reaction('♂', user)
                        onstep6 = True
                        await message1.edit(embed=discord.Embed(
                            description="Please type any custom rules you may have such as no DD or removing off friend's list after hosting.").set_footer(
                            text=
                            'Step 6/6'))
                    elif reaction.emoji == '🇺':
                        step5content = 'Unknown'
                        await message1.remove_reaction('🇺', user)
                        onstep6 = True
                        await message1.edit(embed=discord.Embed(
                            description="Please type any custom rules you may have such as no DD or removing off friend's list after hosting.").set_footer(
                            text=
                            'Step 6/6'))
                while onstep6:
                    step6 = await self.client.wait_for('message', check=check)
                    step6content = step6.content
                    await message.guild.get_channel(row[2]).last_message.delete()
                    await message1.edit(
                        embed=discord.Embed(
                            description="Your rules are: **" + step6content + ".** Is this correct? Y/N"))
                    confirm = await self.client.wait_for('message', check=confirmcheck)
                    if confirm.content == 'Y' or confirm.content == 'y':
                        await message.guild.get_channel(row[2]).last_message.delete()
                        onstep6 = False
                        await message1.delete()
                    if confirm.content == 'N' or confirm.content == 'n':
                        await message.guild.get_channel(row[2]).last_message.delete()
                        await message1.edit(embed=discord.Embed(
                            description="Please type any custom rules you may have such as no DD or removing off friend's list after hosting.").set_footer(
                            text=
                            'Step 6/6'))
                # Create and send the hosting embed
                hostingembed = discord.Embed(description='**' + step1content + "** is being hosted in " + message.guild.get_channel(row[2]).mention)
                hostingembed.set_thumbnail(url=message.author.avatar_url)
                hostingembed.add_field(name='Host:', value=message.author.mention, inline=False)
                hostingembed.add_field(name='Shiny:', value=step3content, inline=True)
                hostingembed.add_field(name='Gender:', value=step5content, inline=False)
                hostingembed.add_field(name='Ability:', value=step4content, inline=True)
                hostingembed.add_field(name='IVs:', value=step2content, inline=False)
                hostingembed.add_field(name='Custom Rules:', value=step6content, inline=True)
                hostingembed.set_footer(text='React with ✨ to gain access to the channel.')
                shinyraidschannel = discord.utils.get(message.guild.text_channels, name='shiny-raids')
                message2 = await shinyraidschannel.send(embed=hostingembed)
                await message2.add_reaction('✨')

            cursor.close()
            db.close()


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
                    description='<:SeekPng:705124992349896795> **Darkrai used Disable.** ' + member.mention +
                                " ***no longer has permission to speak.***"))
                cursor.execute(
                    """INSERT INTO MutedUsers (user_id, user_name, channel_id, channel_name) VALUES (?, ?, ?, ?)""",
                    (member.id, member.display_name, ctx.message.channel.id, ctx.message.channel.name))
                db.commit()
            else:  # If user is already muted
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> **Darkrai used Disable.** ' + member.mention
                                + " ***already has no permission to speak.***"))
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
                    description='<:SeekPng:705124992349896795> **Disable has worn off for** ' + member.mention +
                                " ***and they are now able to speak.***"))
                cursor.execute(f'DELETE FROM MutedUsers WHERE user_id = {member.id}')
                db.commit()
            else:  # If user is already muted
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> **Disable is not active for** ' + member.mention +
                                " ***and they are already allowed to speak.***"))
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
                    description='<:blackhole:705225042052644915> **Darkrai used Dark Void.** ' +
                                member.mention + " ***has been banished to the void.***"))
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
                    description='<:SeekPng:705124992349896795> ' + member.mention +
                                " ***has been pardoned from the void.***"))
                cursor.execute(f'DELETE FROM BannedUsers WHERE user_id = {member.id}')
                db.commit()
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> ' + member.mention +
                                " ***was never previously banned here.***"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751> **User not available or you do not have permissions in this channel.**'))
        cursor.close()
        db.close()
        await ctx.message.delete()


def setup(client):
    client.add_cog(RaidHelper(client))
