import discord
from discord.ext import commands
import asyncio
import sqlite3

class GeneralCommands(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
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
        await ctx.message.channel.send(embed=helpembed)


    # Play RPS
    @commands.command()
    async def rps(self, ctx, member: discord.Member = ''):
        if member:
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
                            p1replycontent = p1reply.content
                            await p1reply.delete()
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
                                p2replycontent = p2reply.content
                                await p2reply.delete()
                                await p2msg.edit(
                                    embed=discord.Embed(description='You have selected `' + p2replycontent + '`.'))

                                if p1replycontent == p2replycontent:
                                    await ctx.message.channel.send(embed=discord.Embed(
                                        description='Both players sent out `'+ p2replycontent + '` resulting in a tie. \n **Scores:** \n' + p1.mention + ' - **' + str(p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                elif p1replycontent == 'rock' and p2replycontent == 'paper':
                                    p2score += 1
                                    await ctx.message.channel.send(embed=discord.Embed(
                                        description=p1.mention + ' sent out rock and ' + p2.mention + ' sent out paper. **Paper wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                            p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                elif p1replycontent == 'rock' and p2replycontent == 'scissors':
                                    p1score += 1
                                    await ctx.message.channel.send(embed=discord.Embed(
                                        description=p1.mention + ' sent out rock and ' + p2.mention + ' sent out scissors. **Rock wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                            p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                elif p1replycontent == 'paper' and p2replycontent == 'scissors':
                                    p2score += 1
                                    await ctx.message.channel.send(embed=discord.Embed(
                                        description=p1.mention + ' sent out paper and ' + p2.mention + ' sent out scissors. **Scissors wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                            p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                elif p1replycontent == 'paper' and p2replycontent == 'rock':
                                    p1score += 1
                                    await ctx.message.channel.send(embed=discord.Embed(
                                        description=p1.mention + ' sent out paper and ' + p2.mention + ' sent out rock. **Paper wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                            p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                elif p1replycontent == 'scissors' and p2replycontent == 'paper':
                                    p1score += 1
                                    await ctx.message.channel.send(embed=discord.Embed(
                                        description=p1.mention + ' sent out scissors and ' + p2.mention + ' sent out paper. **Scissors wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                            p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))
                                elif p1replycontent == 'scissors' and p2replycontent == 'rock':
                                    p2score += 1
                                    await ctx.message.channel.send(embed=discord.Embed(
                                        description=p1.mention + ' sent out scissors and ' + p2.mention + ' sent out rock. **Rock wins!** \n **Scores:** \n' + p1.mention + ' - **' + str(
                                            p1score) + '** \n' + p2.mention + ' - **' + str(p2score) + '**'))

                            except asyncio.TimeoutError:
                                await ctx.message.channel.send(embed=discord.Embed(description=p2.mention + ' has not responded within one minute. ' + p1.mention + ' **has won the RPS game.**'))
                                await p2msg.edit(embed=discord.Embed(description='You have lost because you did not respond in time.'))
                                p1score = 2

                        except asyncio.TimeoutError:
                            await ctx.message.channel.send(embed=discord.Embed(description=p1.mention + ' has not responded within one minute. ' + p2.mention + ' **has won the RPS game.**'))
                            await p1msg.edit(embed=discord.Embed(description='You have lost because you did not respond in time.'))
                            p2score = 2
                    if p1score == 2:
                        await ctx.message.channel.send(embed=discord.Embed(
                            description=p1.mention + ' has **won** the RPS game with a score of ' + str(p1score) + '-' + str(p2score)))
                    if p2score == 2:
                        await ctx.message.channel.send(embed=discord.Embed(
                            description=p2.mention + ' has **won** the RPS game with a score of ' + str(
                                p2score) + '-' + str(p1score)))

                else:
                    await message1.edit(embed=discord.Embed(
                        description='The challenge has been **rejected**.'))
                    await reply.delete()

            except asyncio.TimeoutError:
                await message1.edit(embed=discord.Embed(description=member.mention + ' has not responded within one minute. **The challenge has expired.**'))

        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751>  **Invalid syntax. Please provide a user to challenge after the command. Example:** ***$rps @user***'))


def setup(client):
    client.add_cog(GeneralCommands(client))
