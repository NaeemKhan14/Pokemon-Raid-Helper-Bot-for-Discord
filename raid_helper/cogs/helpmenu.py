import discord
from discord.ext import commands
import asyncio

class HelpMenu(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('HelpMenu cog is loaded.')

    # Help command
    @commands.command()
    async def help(self, ctx):
        helpembed = discord.Embed(description='This is a list of commands that can be used. Some may only be used by certain roles.')
        helpembed.set_author(name='Darkrai Commands', icon_url='https://cdn.discordapp.com/attachments/704174855813070901/712733586632998963/491Darkrai.png')
        helpembed.set_footer(text='Darkrai • Created by Cooly4477 & Charming Potato', icon_url='https://cdn.discordapp.com/attachments/704174855813070901/712733586632998963/491Darkrai.png')
        helpembed.add_field(name='General', value='`$help`, `$ping`, `$suggest`, `$poll`', inline=False)
        helpembed.add_field(name='Shiny Raids', value='`$create`, `$delete`, `$hours`, `$leaderboard`, `$mute`, `$unmute`, `$ban`, `$unban`, `$lock`', inline=False)
        helpembed.add_field(name='Custom VCs', value='`$createvc`, `$deletevc`, `$vcinvite`, `$vcmute`, `$vcunmute`, `$vcban`, `$vcunban`', inline=False)
        helpembed.add_field(name='Games', value='`$hangman`, `$rps`', inline=False)

        helpembed2 = discord.Embed(
            description='This is a list of commands that can be used. Some may only be used by certain roles.')
        helpembed2.set_author(name='Darkrai Commands',
                             icon_url='https://cdn.discordapp.com/attachments/704174855813070901/712733586632998963/491Darkrai.png')
        helpembed2.set_footer(text='Darkrai • Created by Cooly4477 & Charming Potato',
                             icon_url='https://cdn.discordapp.com/attachments/704174855813070901/712733586632998963/491Darkrai.png')

        helpembed2.add_field(name='Chess', value='`$chessplay`, `$move`, `$status`, `$offer`, `$accept`, `$concede`, `$games`, `$elo`, `$chessleaderboard`', inline=False)
        helpembed2.add_field(name='Music', value='`$play`, `$skip`, `$queue`, `$join`, `$summon`, `$leave`, `$volume`, `$np`, `$pause`, `$resume`, `$stop`, `$shuffle`, `$loop`', inline=False)
        helpembed2.add_field(name='Staff', value='`$giverole`', inline=False)
        helpembed2.add_field(name='Owner Only', value='`$clown`, `$torture`, `$addhours`, `$subtracthours`, `$clearhours`, `$cleardb`, `$forcedelete`, `$forcedeletevc`, `$say`', inline=False)
        helpmsg = await ctx.message.channel.send(embed=helpembed)

        def check(reaction, user):
            return reaction.message.id == helpmsg.id and reaction.emoji == '▶' and user.id != helpmsg.author.id

        def check2(reaction, user):
            return reaction.message.id == helpmsg.id and reaction.emoji == '◀' and user.id != helpmsg.author.id

        active = True

        while active:
            await helpmsg.add_reaction('▶')

            try:
                await self.client.wait_for('reaction_add', timeout=60.0, check=check)
                await helpmsg.clear_reactions()
                await helpmsg.edit(embed=helpembed2)
                await helpmsg.add_reaction('◀')
                try:
                    await self.client.wait_for('reaction_add', timeout=60.0, check=check2)
                    await helpmsg.clear_reactions()
                    await helpmsg.edit(embed=helpembed)
                except asyncio.TimeoutError:
                    active = False
                    await helpmsg.clear_reactions()

            except asyncio.TimeoutError:
                active = False
                await helpmsg.clear_reactions()



def setup(client):
    client.add_cog(HelpMenu(client))