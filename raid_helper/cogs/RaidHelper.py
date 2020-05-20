import discord
from discord.ext import commands
import sqlite3
import asyncio
import re
import datetime

class RaidHelper(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        # Create the DB table if it does not exist on startup
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS HostInfo
            (
                user_id	INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_name INTEGER NOT NULL,
                message_id INTEGER,
                PRIMARY KEY(user_id)
            )
            ''')
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS NotHosting
            (
                message_id INTEGER NOT NULL,
                PRIMARY KEY(message_id)
            )
            ''')
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Leaderboards
            (
                user_id INTEGER NOT NULL,
                time_hosted REAL,
                PRIMARY KEY(user_id)
            )
            ''')
        cursor.execute("""CREATE TABLE IF NOT EXISTS MutedUsers AS SELECT * FROM HostInfo""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS BannedUsers AS SELECT * FROM HostInfo""")
        checkhosting = cursor.execute("""SELECT * FROM HostInfo""").fetchone()
        checknothosting = cursor.execute("""SELECT * FROM NotHosting""").fetchone()
        if checkhosting is None and checknothosting is None:
            shinyraidschannel = discord.utils.get(self.client.get_all_channels(), name='shiny-raids')
            message = await shinyraidschannel.send(embed=discord.Embed(description="<:x_:705214517961031751>  **No raids are currently being hosted.**"))
            cursor.execute(
                """INSERT INTO NotHosting (message_id) VALUES (?)""",
                (message.id, ))
            db.commit()
        cursor.close()
        db.close()
        print('RaidHelper cog is loaded.')

    # Create a channel
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def create(self, ctx, *, chan_name=''):
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
                    embed=discord.Embed(description="<:SeekPng:705124992349896795>  **Channel named '" + chan_name + "' has been created.**"))
                # Create a new channel based on category
                category = discord.utils.get(ctx.guild.categories, name='✨ Pokemon ✨')
                new_chan = await ctx.guild.create_text_channel(chan_name, category=category)
                # Set permissions for the user in this new channel
                await new_chan.set_permissions(discord.utils.get(ctx.message.guild.roles, name='Member'),
                                               read_messages=False)
                await new_chan.set_permissions(ctx.message.guild.get_member(262691055030370306),
                                               read_messages=True)
                await new_chan.set_permissions(ctx.message.guild.get_member(663505910580248587),
                                               read_messages=True)
                await new_chan.set_permissions(ctx.message.guild.get_member(437808476106784770),
                                               read_messages=True)
                await new_chan.set_permissions(ctx.message.author, manage_messages=True, read_messages=True, mention_everyone=True)
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
                    '<:x_:705214517961031751>  **You already have a channel created.**'))
            cursor.close()
            db.close()
        else:
            input_name_embed = discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax. Please provide a name after the command. Example:** ***$create channelname***')
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
                    description="Please tell me what Pokemon or den you are hosting (include Gmax if Gmax) along with the nature in parantheses. Feel free to put 'rerolling' and the den # if you are rerolling dens (do not include shininess, gender, etc. only the den/mon and nature). Ex: Eevee (Modest)").set_footer(
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

                        # Grant permission for user to tag shiny raids
                        shinyrole = discord.utils.get(message.guild.roles, name='Shiny Raids')
                        shinyraidschannel = discord.utils.get(message.guild.text_channels, name='shiny-raids')
                        user = discord.utils.get(message.guild.members, id=row[0])
                        await message1.edit(embed=discord.Embed(
                            description="Please tag " + shinyrole.mention + " in " + shinyraidschannel.mention + " to start hosting"))
                        await shinyraidschannel.set_permissions(user, send_messages=True)
                        await shinyrole.edit(mentionable=True)

                    if confirm.content == 'N' or confirm.content == 'n':
                        await message.guild.get_channel(row[2]).last_message.delete()
                        await message1.edit(embed=discord.Embed(
                            description="Please type any custom rules you may have such as no DD or removing off friend's list after hosting.").set_footer(
                            text=
                            'Step 6/6'))

                # Create the hosting embed
                hostingembed = discord.Embed(description='**' + step1content + "** is being hosted in " + message.guild.get_channel(row[2]).mention)
                hostingembed.set_thumbnail(url=message.author.avatar_url)
                hostingembed.add_field(name='Host:', value=message.author.mention, inline=False)
                hostingembed.add_field(name='Shiny:', value=step3content, inline=True)
                hostingembed.add_field(name='Gender:', value=step5content, inline=True)
                hostingembed.add_field(name='Ability:', value=step4content, inline=True)
                hostingembed.add_field(name='IVs:', value=step2content, inline=True)
                hostingembed.add_field(name='Custom Rules:', value=step6content, inline=False)
                hostingembed.set_footer(text='React with ✨ to gain access to the channel.')

                # Get role and channel
                shinyraidschannel = discord.utils.get(message.guild.text_channels, name='shiny-raids')
                shinyrole = discord.utils.get(message.guild.roles, name='Shiny Raids')
                user = discord.utils.get(message.guild.members, id=row[0])

                # Check for ping
                waitingforping = True
                while waitingforping:
                    def pingcheck(msg):
                        return msg.channel == shinyraidschannel and msg.author.id == row[0]
                    pingconfirm = await self.client.wait_for('message', check=pingcheck)
                    if shinyrole.mention in pingconfirm.content:
                        waitingforping = False
                        await shinyraidschannel.set_permissions(user, send_messages=False)
                        await shinyrole.edit(mentionable=False)
                        await pingconfirm.delete()
                        await message1.delete()
                    else:
                        await pingconfirm.delete()

                nothosting = db.execute("""SELECT * FROM NotHosting""").fetchone()
                if nothosting:
                    nothostingmessage = await shinyraidschannel.fetch_message(nothosting[0])
                    await nothostingmessage.delete()
                    cursor.execute(f'DELETE FROM NotHosting WHERE message_id = {nothosting[0]}')
                    db.commit()
                message2 = await shinyraidschannel.send(embed=hostingembed)
                await message2.add_reaction('✨')
                cursor.execute(f'UPDATE HostInfo SET message_id = {message2.id} WHERE user_id = {row[0]}')
                db.commit()

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
            bannedrow = cursor.execute(f'SELECT * FROM BannedUsers WHERE channel_id = {row[2]}').fetchone()
            mutedrow = cursor.execute(f'SELECT * FROM MutedUsers WHERE channel_id = {row[2]}').fetchone()
            leaderboardsrow = cursor.execute(f'SELECT * FROM Leaderboards WHERE user_id = {row[0]}').fetchone()

            await ctx.guild.get_channel(row[2]).delete()
            shinyraidschannel = discord.utils.get(ctx.message.guild.text_channels, name='shiny-raids')

            if row[4]:
                hostmessage = await shinyraidschannel.fetch_message(row[4])
                hosted_time = datetime.datetime.utcnow() - hostmessage.created_at
                hostedtimeseconds = hosted_time.total_seconds()
                hostedtimehours = hostedtimeseconds/3600

                if leaderboardsrow:
                    hostedtimehours += leaderboardsrow[1]
                    cursor.execute(f'UPDATE Leaderboards SET time_hosted = {hostedtimehours} WHERE user_id = {row[0]}')
                    db.commit()

                else:
                    cursor.execute(
                        """INSERT INTO Leaderboards (user_id, time_hosted) VALUES (?, ?)""",
                        (ctx.message.author.id, hostedtimehours))
                    db.commit()

                await hostmessage.delete()

            if bannedrow:
                cursor.execute(f'DELETE FROM BannedUsers WHERE channel_id = {row[2]}')
                db.commit()
            if mutedrow:
                cursor.execute(f'DELETE FROM MutedUsers WHERE channel_id = {row[2]}')
                db.commit()
            cursor.execute(f'DELETE FROM HostInfo WHERE user_id = {row[0]}')
            db.commit()

            # See if anyone else is still hosting
            checkhosting = db.execute("""SELECT * FROM HostInfo""").fetchone()
            checkmessage = db.execute("""SELECT * FROM NotHosting""").fetchone()
            if checkhosting is None and checkmessage is None:
                noraids = await shinyraidschannel.send(
                    embed=discord.Embed(description="<:x_:705214517961031751>  **No raids are currently being hosted.**"))
                db.execute(
                    """INSERT INTO NotHosting (message_id) VALUES (?)""",
                    (noraids.id,))
                db.commit()
        else:
            await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751>  **You do not have any channels created.**'))
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

            if ctx.author == member:
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **You cannot mute yourself**'))

            # Check if user is already muted or not
            if not muted_users_row:
                await channel.set_permissions(member, send_messages=False)
                await channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795>  **Darkrai used Disable.** ' + member.mention +
                                " ***no longer has permission to speak.***"))
                cursor.execute(
                    """INSERT INTO MutedUsers (user_id, user_name, channel_id, channel_name) VALUES (?, ?, ?, ?)""",
                    (member.id, member.display_name, ctx.message.channel.id, ctx.message.channel.name))
                db.commit()
            else:  # If user is already muted
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Darkrai used Disable.** ' + member.mention
                                + " ***already has no permission to speak.***"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751>  **User not available or you do not have permissions in this channel.**'))
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
                    description='<:SeekPng:705124992349896795>  **Disable has worn off for** ' + member.mention +
                                " ***and they are now able to speak.***"))
                cursor.execute(f'DELETE FROM MutedUsers WHERE user_id = {member.id}')
                db.commit()
            else:  # If user is already muted
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Disable is not active for** ' + member.mention +
                                " ***and they are already allowed to speak.***"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751>  **User not available or you do not have permissions in this channel.**'))
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
                f'SELECT * FROM BannedUsers WHERE user_id = {member.id} AND channel_id = {ctx.message.channel.id}').fetchone()

            if ctx.author == member:
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **You cannot ban yourself**'))

            # Check if user is already banned or not
            if not banned_users_row:
                await channel.set_permissions(member, read_messages=False)
                await channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795>  **Darkrai used Dark Void. <:blackhole:705225042052644915>** ' +
                                member.mention + " ***has been banished to the void.***"))
                cursor.execute(
                    """INSERT INTO BannedUsers (user_id, user_name, channel_id, channel_name) VALUES (?, ?, ?, ?)""",
                    (member.id, member.display_name, ctx.message.channel.id, ctx.message.channel.name))
                db.commit()
            if banned_users_row:
                await channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Player is already banished.**'))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751>  **User not available or you do not have permissions in this channel.**'))
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
                    description='<:SeekPng:705124992349896795>  ' + member.mention +
                                " ***has been pardoned from the void. <:blackhole:705225042052644915>***"))
                cursor.execute(f'DELETE FROM BannedUsers WHERE user_id = {member.id}')
                db.commit()
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  ' + member.mention +
                                " ***was never previously banned here.***"))
        else:  # If user is not available or current channel != host's channel
            await ctx.message.channel.send(embed=discord.Embed(
                description=
                '<:x_:705214517961031751>  **User not available or you do not have permissions in this channel.**'))
        cursor.close()
        db.close()
        await ctx.message.delete()

    # Force delete a channel
    @commands.command()
    @commands.has_role('Owner')
    async def forcedelete(self, ctx, chan_id=''):
        if chan_id:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(
                f'SELECT * FROM HostInfo WHERE channel_id = {chan_id}').fetchone()
            bannedrow = cursor.execute(f'SELECT * FROM BannedUsers WHERE channel_id = {chan_id}').fetchone()
            mutedrow = cursor.execute(f'SELECT * FROM MutedUsers WHERE channel_id = {chan_id}').fetchone()
            leaderboardsrow = cursor.execute(f'SELECT * FROM Leaderboards WHERE user_id = {row[0]}').fetchone()

            # If there is any data, it means the user has a channel which can be deleted
            if row:
                await ctx.guild.get_channel(row[2]).delete()
                shinyraidschannel = discord.utils.get(ctx.message.guild.text_channels, name='shiny-raids')

                if row[4]:
                    hostmessage = await shinyraidschannel.fetch_message(row[4])
                    hosted_time = datetime.datetime.utcnow() - hostmessage.created_at
                    hostedtimeseconds = hosted_time.total_seconds()
                    hostedtimehours = hostedtimeseconds / 3600

                    if leaderboardsrow:
                        hostedtimehours += leaderboardsrow[1]
                        cursor.execute(
                            f'UPDATE Leaderboards SET time_hosted = {hostedtimehours} WHERE user_id = {row[0]}')
                        db.commit()

                    else:
                        cursor.execute(
                            """INSERT INTO Leaderboards (user_id, time_hosted) VALUES (?, ?)""",
                            (row[0], hostedtimehours))
                        db.commit()

                    await hostmessage.delete()

                if bannedrow:
                    cursor.execute(f'DELETE FROM BannedUsers WHERE channel_id = {row[2]}')
                    db.commit()

                if mutedrow:
                    cursor.execute(f'DELETE FROM MutedUsers WHERE channel_id = {row[2]}')
                    db.commit()

                cursor.execute(f'DELETE FROM HostInfo WHERE user_id = {row[0]}')
                db.commit()

                checkhosting = db.execute("""SELECT * FROM HostInfo""").fetchone()
                checkmessage = db.execute("""SELECT * FROM NotHosting""").fetchone()
                if checkhosting is None and checkmessage is None:
                    noraids = await shinyraidschannel.send(
                        embed=discord.Embed(
                            description="<:x_:705214517961031751>  **No raids are currently being hosted.**"))
                    db.execute(
                        """INSERT INTO NotHosting (message_id) VALUES (?)""",
                        (noraids.id,))
                    db.commit()
            else:
                noid = discord.Embed(
                    description='<:x_:705214517961031751>  **Channel with specified ID does not exist.**')
                await ctx.message.channel.send(embed=noid)
            cursor.close()
            db.close()
        else:
            input_invalid = discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax. Please provide an id after the command. Example:** ***$forcedelete channelid***')
            await ctx.message.channel.send(embed=input_invalid)
        await ctx.message.delete()

    # Give channel perms to those who react to the embed
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) == '✨':
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(
                f'SELECT * FROM HostInfo WHERE message_id = {payload.message_id}').fetchone()
            if row:
                bannedrow = cursor.execute(
                    f'SELECT * FROM BannedUsers WHERE user_id = {payload.user_id} AND channel_id = {row[2]}').fetchone()
                mutedrow = cursor.execute(
                    f'SELECT * FROM MutedUsers WHERE user_id = {payload.user_id} AND channel_id = {row[2]}').fetchone()

                hostchannel = self.client.get_channel(id=row[2])

                if bannedrow is None and mutedrow is None and payload.user_id != row[0]:
                    await hostchannel.set_permissions(payload.member, read_messages=True)

                elif bannedrow is None and mutedrow and payload.user_id != row[0]:
                    await hostchannel.set_permissions(payload.member, read_messages=True, send_messages=False)
            cursor.close()
            db.close()

    # Remove channel perms to those who unreact to the embed
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if str(payload.emoji) == '✨':
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(
                f'SELECT * FROM HostInfo WHERE message_id = {payload.message_id}').fetchone()
            if row and payload.user_id != row[0]:
                hostchannel = self.client.get_channel(id=row[2])
                await hostchannel.set_permissions(self.client.get_user(payload.user_id), read_messages=False)
            cursor.close()
            db.close()

    # Clear database in case of glitches
    @commands.command()
    @commands.has_role('Owner')
    async def cleardb(self, ctx, user_id=''):
        if user_id:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(
                f'SELECT * FROM HostInfo WHERE user_id = {user_id}').fetchone()
            if row:
                bannedrow = cursor.execute(
                    f'SELECT * FROM BannedUsers WHERE channel_id = {row[2]}').fetchone()
                mutedrow = cursor.execute(
                    f'SELECT * FROM MutedUsers WHERE channel_id = {row[2]}').fetchone()
                if bannedrow:
                    cursor.execute(f'DELETE FROM BannedUsers WHERE channel_id = {row[2]}')
                    db.commit()
                if mutedrow:
                    cursor.execute(f'DELETE FROM MutedUsers WHERE channel_id = {row[2]}')
                    db.commit()
                cursor.execute(f'DELETE FROM HostInfo WHERE user_id = {user_id}')
                db.commit()

            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **User with specified ID does not exist in the database.**'))

            cursor.close()
            db.close()

        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax. Please provide an id after the command. Example:** ***$cleardb userid***'))
        await ctx.message.delete()

    # Check hours hosted
    @commands.command()
    @commands.has_role('Shiny Raid Host')
    async def hours(self, ctx, member: discord.Member):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        if member:
            row = cursor.execute(
                f'SELECT * FROM Leaderboards WHERE user_id = {member.id}').fetchone()
            if row:
                await ctx.message.channel.send(embed=discord.Embed(
                    description=member.display_name + ' currently has **' + str(round(row[1], 2)) + '** hours hosted.'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description=member.display_name + ' currently has **0** hours hosted.'))
        else:
            row = cursor.execute(
                f'SELECT * FROM Leaderboards WHERE user_id = {ctx.message.author.id}').fetchone()
            if row:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='You currently have **' + str(round(row[1], 2)) + '** hours hosted.'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='You currently have **0** hours hosted.'))
        cursor.close()
        db.close()

    # Leaderboard
    @commands.command()
    async def leaderboard(self, ctx):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        beforerow = cursor.execute(f'SELECT * FROM Leaderboards ORDER BY time_hosted DESC LIMIT 10')
        row = beforerow.fetchall()

        leaderboardembed = discord.Embed(title='Leaderboard', description='**1. ' + self.client.get_user(row[0][0]).name + '** - **' + str(round(row[0][1], 2)) + '** hours hosted \n **2. ' + self.client.get_user(row[1][0]).name + '** - **' + str(round(row[1][1], 2)) + '** hours hosted \n **3. ' + self.client.get_user(row[2][0]).name + '** - **' + str(round(row[2][1], 2)) + '** hours hosted \n **4. ' + self.client.get_user(row[3][0]).name + '** - **' + str(round(row[3][1], 2)) + '** hours hosted \n **5. ' + self.client.get_user(row[4][0]).name + '** - **' + str(round(row[4][1], 2)) + '** hours hosted \n **6. ' + self.client.get_user(row[5][0]).name + '** - **' + str(round(row[5][1], 2)) + '** hours hosted \n **7. ' + self.client.get_user(row[6][0]).name + '** - **' + str(round(row[6][1], 2)) + '** hours hosted \n **8. ' + self.client.get_user(row[7][0]).name + '** - **' + str(round(row[7][1], 2)) + '** hours hosted \n **9. ' + self.client.get_user(row[8][0]).name + '** - **' + str(round(row[8][1], 2)) + '** hours hosted \n **10. ' + self.client.get_user(row[9][0]).name + '** - **' + str(round(row[9][1], 2)) + '** hours hosted \n')
        await ctx.message.channel.send(embed=leaderboardembed)

        cursor.close()
        db.close()

    # Subtract hours from people
    @commands.command()
    @commands.has_role('Owner')
    async def subtracthours(self, ctx, member: discord.Member, time=''):
        if member and time:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(
                f'SELECT * FROM Leaderboards WHERE user_id = {member.id}').fetchone()
            timehosted = row[1] - float(time)
            cursor.execute(
                f'UPDATE Leaderboards SET time_hosted = {timehosted} WHERE user_id = {row[0]}')
            db.commit()
            await ctx.message.channel.send(embed=discord.Embed(description='You have subtracted **' + str(time) + '** hours from **' + member.display_name + '** and they have now hosted for **' + str(round(timehosted, 2)) + '** hours.'))
            await ctx.message.delete()

            cursor.close()
            db.close()

    # Add hours for people
    @commands.command()
    @commands.has_role('Owner')
    async def addhours(self, ctx, member: discord.Member, time=''):
        if member and time:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(
                f'SELECT * FROM Leaderboards WHERE user_id = {member.id}').fetchone()
            timehosted = row[1] + float(time)
            cursor.execute(
                f'UPDATE Leaderboards SET time_hosted = {timehosted} WHERE user_id = {row[0]}')
            db.commit()
            await ctx.message.channel.send(embed=discord.Embed(description='You have added **' + str(time) + '** hours for **' + member.display_name + '** and they have now hosted for **' + str(round(timehosted, 2)) + '** hours.'))
            await ctx.message.delete()

            cursor.close()
            db.close()


def setup(client):
    client.add_cog(RaidHelper(client))
