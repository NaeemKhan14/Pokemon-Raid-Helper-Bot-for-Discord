import discord
from discord.ext import commands
import asyncio
import sqlite3

class GeneralCommands(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Game('discord.gg/cool | $help'))
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Clown
            (
                user_id	INTEGER NOT NULL,
                number INTEGER,
                PRIMARY KEY(user_id)
            )
            ''')
        cursor.close()
        db.close()
        print('GeneralCommands cog is loaded.')


    # Ping certain roles command
    @commands.command()
    @commands.has_any_role('Streamer', 'Giveaway', 'Event Host', 'Smash Ultimate')
    async def ping(self, ctx, role=''):
        streamchannel = discord.utils.get(self.client.get_all_channels(), name='stream-announcements')
        giveawaychannel = discord.utils.get(self.client.get_all_channels(), name='giveaways')
        giveawaychannel2 = discord.utils.get(self.client.get_all_channels(), name='private-giveaways')
        eventschannel = discord.utils.get(self.client.get_all_channels(), name='event-announcements')
        smashchannel = discord.utils.get(self.client.get_all_channels(), name='smash-ultimate')

        streamrole = discord.utils.get(ctx.message.guild.roles, name='Stream Notifications')
        giveawayrole = discord.utils.get(ctx.message.guild.roles, name='Giveaway')
        eventsrole = discord.utils.get(ctx.message.guild.roles, name='Events')
        smashrole = discord.utils.get(ctx.message.guild.roles, name='Smash Ultimate')

        await ctx.message.delete()

        if role == 'stream' and ctx.message.channel == streamchannel:
            await streamrole.edit(mentionable=True)
            message1 = await ctx.message.channel.send(embed=discord.Embed(description=streamrole.mention + ' **is now able to be pinged.**'))

            def pingcheck(msg):
                return msg.channel == streamchannel and msg.author == ctx.message.author

            pingconfirm = await self.client.wait_for('message', check=pingcheck)
            if streamrole.mention in pingconfirm.content:
                await streamrole.edit(mentionable=False)
            await message1.delete()
        elif role == 'giveaway' and (ctx.message.channel == giveawaychannel or ctx.message.channel == giveawaychannel2):
            await giveawayrole.edit(mentionable=True)
            message1 = await ctx.message.channel.send(
                embed=discord.Embed(description=giveawayrole.mention + ' **is now able to be pinged.**'))

            def pingcheck(msg):
                return (msg.channel == giveawaychannel or msg.channel == giveawaychannel2) and msg.author == ctx.message.author

            pingconfirm = await self.client.wait_for('message', check=pingcheck)
            if giveawayrole.mention in pingconfirm.content:
                await giveawayrole.edit(mentionable=False)
            await message1.delete()
        elif role == 'events' and ctx.message.channel == eventschannel:
            await eventsrole.edit(mentionable=True)
            message1 = await ctx.message.channel.send(
                embed=discord.Embed(description=eventsrole.mention + ' **is now able to be pinged.**'))

            def pingcheck(msg):
                return msg.channel == eventschannel and msg.author == ctx.message.author

            pingconfirm = await self.client.wait_for('message', check=pingcheck)
            if eventsrole.mention in pingconfirm.content:
                await eventsrole.edit(mentionable=False)
            await message1.delete()
        elif role == 'smash' and ctx.message.channel == smashchannel:
            await smashrole.edit(mentionable=True)
            message1 = await ctx.message.channel.send(
                embed=discord.Embed(description=smashrole.mention + ' **is now able to be pinged.**'))

            def pingcheck(msg):
                return msg.channel == smashchannel and msg.author == ctx.message.author

            pingconfirm = await self.client.wait_for('message', check=pingcheck)
            if smashrole.mention in pingconfirm.content:
                await smashrole.edit(mentionable=False)
            await message1.delete()
        else:
            message = await ctx.message.channel.send(embed=discord.Embed(description='Use the syntax **$ping {role}** with the role being **lowercase in the respective channels**. *Here is a list of roles that can be pinged:* **stream**, **giveaway**, **events**, and **smash.**'))
            await asyncio.sleep(60)
            await message.delete()

    # Help command
    @commands.command()
    async def help(self, ctx):
        helpembed = discord.Embed(description='This is a list of commands that can be used. Some may only be used by certain roles.')
        helpembed.set_author(name='Darkrai Commands', icon_url='https://cdn.discordapp.com/attachments/704174855813070901/712733586632998963/491Darkrai.png')
        helpembed.set_footer(text='Darkrai • Created by Cooly4477 & Charming Potato', icon_url='https://cdn.discordapp.com/attachments/704174855813070901/712733586632998963/491Darkrai.png')
        helpembed.add_field(name='General', value='`$help`, `$ping`', inline=False)
        helpembed.add_field(name='Shiny Raids', value='`$create`, `$delete`, `$hours`, `$leaderboard`, `$mute`, `$unmute`, `$ban`, `$unban`, `$addhours`, `$subtracthours`, `$cleardb`, `$forcedelete`', inline=False)
        helpembed.add_field(name='Custom VCs', value='`$createvc`, `$deletevc`, `$vcinvite`, `$vcmute`, `$vcunmute`, `$vcban`, `$vcunban`, `$forcedeletevc`', inline=False)
        helpembed.add_field(name='Games', value='`$hangman`, `$rps`', inline=False)
        helpembed.add_field(name='Chess', value='`$chessplay`, `$move`, `$status`, `$offer`, `$accept`, `$concede`, `$games`, `$elo`, `$chessleaderboard`', inline=False)
        helpembed.add_field(name='Music', value='`$play`, `$skip`, `$queue`, `$join`, `$summon`, `$leave`, `$volume`, `$np`, `$pause`, `$resume`, `$stop`, `$shuffle`, `$loop`', inline=False)
        helpembed.add_field(name='Staff', value='`$giverole`', inline=False)
        helpembed.add_field(name='Owner Only', value='`$clown`, `$torture`', inline=False)
        await ctx.message.channel.send(embed=helpembed)


    # Play RPS
    @commands.command()
    async def rps(self, ctx, member: discord.Member = ''):
        if member:
            if member != ctx.message.author:
                message1 = await ctx.message.channel.send(embed=discord.Embed(
                    description=member.mention + ', you have been challenged to a best of 3 game of RPS by ' + ctx.message.author.mention + '. To accept this challenge, type `accept` in the next minute, or type `reject` to reject this challenge.').set_image(url='https://cdn.discordapp.com/attachments/704174855813070901/717464068688052254/cartoon-rock-paper-scissors-vector-characters.png'))

                def check(msg):
                    return ctx.message.channel == msg.channel and member == msg.author and (str.lower(msg.content) == 'accept' or str.lower(msg.content) == 'reject')

                try:
                    reply = await self.client.wait_for('message', timeout=60.0, check=check)
                    if reply.content == 'accept':
                        await message1.edit(embed=discord.Embed(
                            description='The challenge has been **accepted**. Check your DMs for instructions.'))
                        await reply.delete()
                        p1score = 0
                        p2score = 0
                        p1 = self.client.get_user(member.id)
                        p2 = self.client.get_user(ctx.message.author.id)

                        while (p1score != 2 and p2score != 2):
                            p1msg = await p1.send(embed=discord.Embed(description='You have **one minute** to reply with your choice of `rock`, `paper`, or `scissors`.'))

                            def check2(msg):
                                return p1msg.channel == msg.channel and p1 == msg.author and (str.lower(msg.content) == 'rock' or str.lower(msg.content) == 'paper' or str.lower(msg.content) == 'scissors')

                            try:
                                p1reply = await self.client.wait_for('message', timeout=60.0, check=check2)
                                p1replycontent = str.lower(p1reply.content)
                                await p1msg.edit(
                                    embed=discord.Embed(description='You have selected `' + p1replycontent + '`.'))

                                p2msg = await p2.send(embed=discord.Embed(
                                    description='You have **one minute** to reply with your choice of `rock`, `paper`, or `scissors`.'))
                                def check3(msg):
                                    return p2msg.channel == msg.channel and p2 == msg.author and (
                                                str.lower(msg.content) == 'rock' or str.lower(
                                            msg.content) == 'paper' or str.lower(msg.content) == 'scissors')
                                try:
                                    p2reply = await self.client.wait_for('message', timeout=60.0, check=check3)
                                    p2replycontent = str.lower(p2reply.content)
                                    await p2msg.edit(
                                        embed=discord.Embed(description='You have selected `' + p2replycontent + '`.'))

                                    if p1replycontent == p2replycontent:
                                        await message1.edit(embed=discord.Embed(
                                            description='Both players sent out `' + p2replycontent + '` resulting in a tie. \n **Scores:** \n' + p1.mention + ' - **' + str(p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                    elif p1replycontent == 'rock' and p2replycontent == 'paper':
                                        p2score += 1
                                        await message1.edit(embed=discord.Embed(
                                            description=p1.mention + ' sent out rock and ' + p2.mention + ' sent out paper. **Paper wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                                p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                    elif p1replycontent == 'rock' and p2replycontent == 'scissors':
                                        p1score += 1
                                        await message1.edit(embed=discord.Embed(
                                            description=p1.mention + ' sent out rock and ' + p2.mention + ' sent out scissors. **Rock wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                                p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                    elif p1replycontent == 'paper' and p2replycontent == 'scissors':
                                        p2score += 1
                                        await message1.edit(embed=discord.Embed(
                                            description=p1.mention + ' sent out paper and ' + p2.mention + ' sent out scissors. **Scissors wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                                p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                    elif p1replycontent == 'paper' and p2replycontent == 'rock':
                                        p1score += 1
                                        await message1.edit(embed=discord.Embed(
                                            description=p1.mention + ' sent out paper and ' + p2.mention + ' sent out rock. **Paper wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                                p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                    elif p1replycontent == 'scissors' and p2replycontent == 'paper':
                                        p1score += 1
                                        await message1.edit(embed=discord.Embed(
                                            description=p1.mention + ' sent out scissors and ' + p2.mention + ' sent out paper. **Scissors wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                                p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                    elif p1replycontent == 'scissors' and p2replycontent == 'rock':
                                        p2score += 1
                                        await message1.edit(embed=discord.Embed(
                                            description=p1.mention + ' sent out scissors and ' + p2.mention + ' sent out rock. **Rock wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                                p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))

                                except asyncio.TimeoutError:
                                    await message1.edit(embed=discord.Embed(description=p2.mention + ' has not responded within one minute. ' + p1.mention + ' **has won the RPS game.**'))
                                    await p2msg.edit(embed=discord.Embed(description='You have lost because you did not respond in time.'))
                                    p1score = 2

                            except asyncio.TimeoutError:
                                await message1.edit(embed=discord.Embed(description=p1.mention + ' has not responded within one minute. ' + p2.mention + ' **has won the RPS game.**'))
                                await p1msg.edit(embed=discord.Embed(description='You have lost because you did not respond in time.'))
                                p2score = 2
                        if p1score == 2:
                            await message1.edit(embed=discord.Embed(
                                description=p1.mention + ' has **won** the RPS game with a score of ' + str(p1score) + '-' + str(p2score)))
                        if p2score == 2:
                            await message1.edit(embed=discord.Embed(
                                description=p2.mention + ' has **won** the RPS game with a score of **' + str(
                                    p2score) + '-' + str(p1score) + '**'))

                    else:
                        await message1.edit(embed=discord.Embed(
                            description='The challenge has been **rejected**.'))
                        await reply.delete()

                except asyncio.TimeoutError:
                    await message1.edit(embed=discord.Embed(description=member.mention + ' has not responded within one minute. **The challenge has expired.**'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **You cannot challenge yourself**'))
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax. Please provide a user to challenge after the command. Example:** ***$rps @user***'))

    # Clown msg if author is a clown
    @commands.Cog.listener()
    async def on_message(self, message):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        if cursor.execute(f'SELECT * FROM Clown WHERE user_id = {message.author.id}').fetchone():
            row = cursor.execute(f'SELECT * FROM Clown WHERE user_id = {message.author.id}').fetchone()
            if row[1] > 0:
                await message.add_reaction('🤡')
                await message.add_reaction('<:clownoftheyear:689910124806013090>')
                await message.add_reaction('<:cuteclown:720000248574902383>')

                time = row[1] - 1
                cursor.execute(
                    f'UPDATE Clown SET number = {time} WHERE user_id = {row[0]}')
                db.commit()
            else:
                cursor.execute(f'DELETE FROM Clown WHERE user_id = {row[0]}')
                db.commit()
            cursor.close()
            db.close()

    # Clown command
    @commands.command()
    @commands.has_role('Owner')
    async def clown(self, ctx, member: discord.Member = '', time: int = 0):
        if member:
            if time > 0:
                db = sqlite3.connect('RaidHelper.sqlite')
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO Clown (user_id, number) VALUES (?, ?)""",
                    (member.id, time))
                db.commit()
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795> ' + member.mention + ' will be clowned on their next **' + str(time) + '** messages.'))
                cursor.close()
                db.close()
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Invalid syntax. Please provide the # of msgs to clown after the user. Example:** ***$clown @user #***'))
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax. Please provide a user to clown after the command. Example:** ***$clown @user***'))
        await ctx.message.delete()

    # Ping torture
    @commands.command()
    @commands.has_role('Owner')
    async def torture(self, ctx, member: discord.Member = '', time: int = 0):
        await ctx.message.delete()
        if member:
            if time > 0:
                await ctx.message.channel.send(embed=discord.Embed(
                    description=member.mention + ' will be pinged ' + str(time) + ' times.'))
                category = await ctx.message.guild.create_category(name='Pings')
                pingrole = await ctx.message.guild.create_role(name='Ping Torture')
                await member.add_roles(pingrole)
                while time > 0:
                    pingchannel = await ctx.message.guild.create_text_channel(name='Pings', category=category)
                    await pingchannel.set_permissions(discord.utils.get(ctx.message.guild.roles, name='Member'), read_messages=False)
                    await pingchannel.set_permissions(pingrole, read_messages=True, send_messages=False)
                    await pingchannel.send(content=member.mention)
                    time -= 1
                await asyncio.sleep(300)
                for channels in category.channels:
                    await channels.delete()
                await category.delete()
                await pingrole.delete()
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Invalid syntax. Please provide the # of pings to torture the user with. Example:** ***$torture @user #***'))
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax. Please provide a user to torture after the command. Example:** ***$torture @user***'))

    # Allow staff to give roles
    @commands.command()
    @commands.has_any_role('Owner', 'Admin', 'Mod')
    async def giverole(self, ctx, member: discord.Member = '', role=''):
        if member and role:
            if str.lower(role) == 'host':
                await member.add_roles(discord.utils.get(ctx.message.guild.roles, name='Shiny Raid Host'))
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795>  You have successfully given ' + member.mention + ' the **Shiny Raid Host** role.'))
            elif str.lower(role) == 'giveaways':
                await member.add_roles(discord.utils.get(ctx.message.guild.roles, name='Giveaways'))
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795>  You have successfully given ' + member.mention + ' the **Giveaways** role.'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Role not found.** \n *List of available roles:* **Host** and **Giveaways**'))
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax.** Please provide a **user** and **role** to give after the command. \n *Example:* **$giverole @user role** \n *List of available roles:* **Host** and **Giveaways**'))
        await ctx.message.delete()

    # Verify new players
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == discord.utils.get(self.client.get_all_channels(), name='verify'):
            if message.content == 'I agree':
                await message.author.add_roles(discord.utils.get(message.guild.roles, name='Member'))
            await message.delete()




def setup(client):
    client.add_cog(GeneralCommands(client))
