import discord
from discord.ext import commands
import asyncio


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
        helpembed.add_field(name='Custom VCs', value='`$createvc`, `$deletevc`, `$vcinvite`, `$vcmute`, `$vcunmute`, `$vcban`, `$vcunban`', inline=False)
        helpembed.add_field(name='Games', value='`$hangman`', inline=False)
        helpembed.add_field(name='Chess', value='`$chessplay`, `$move`, `$status`, `$offer`, `$accept`, `$concede`, `$games`, `$elo`, `$chessleaderboard`', inline=False)
        helpembed.add_field(name='Music', value='`$play`, `$skip`, `$queue`, `$join`, `$summon`, `$leave`, `$volume`, `$np`, `$pause`, `$resume`, `$stop`, `$shuffle`, `$loop`', inline=False)
        await ctx.message.channel.send(embed=helpembed)

            


def setup(client):
    client.add_cog(GeneralCommands(client))
