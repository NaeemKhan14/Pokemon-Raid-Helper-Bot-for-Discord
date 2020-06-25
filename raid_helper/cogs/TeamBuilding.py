import discord
from discord.ext import commands
import asyncio
from teampokemon import weaknessCheck
from selenium import webdriver
from bs4 import BeautifulSoup
import pokebase as pb

class TeamBuilding(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('TeamBuilding cog is loaded.')

    @commands.command()
    async def teambuild(self, ctx):
        message1 = await ctx.message.channel.send(embed=discord.Embed(description=ctx.message.author.mention + ' Which format would you like to team build for? National Dex or VGC? You have one minute to reply before you are timed out.'))

        def formatcheck(msg):
            return msg.channel.id == ctx.message.channel.id and msg.author.id == ctx.message.author.id and (str.lower(msg.content) == 'national dex' or str.lower(msg.content) == 'vgc')

        def pokepastecheck(msg):
            return msg.channel.id == ctx.message.channel.id and msg.author.id == ctx.message.author.id and "https://pokepast.es/" in str.lower(msg.content)

        try:
            format = await self.client.wait_for('message', timeout=60.0, check=formatcheck)

            if str.lower(format.content) == 'national dex':  # Nat Dex Team Build
                await format.delete()
                await message1.edit(embed=discord.Embed(description=ctx.message.author.mention + ' You have chosen **National Dex**. Please provide me with a **legal pokepaste link** to a **legal** team. You have one minute. \n **Warning:** Do not nickname any of your Pokemon.'))

            else:  # VGC Team Build
                await format.delete()
                await message1.edit(embed=discord.Embed(description=ctx.message.author.mention + ' You have chosen **VGC**. Please provide me with a **pokepaste link** to a **legal** team. You have one minute. \n **Warning:** Do not nickname any of your Pokemon.'))
                try:
                    pokepaste = await self.client.wait_for('message', timeout=60.0, check=pokepastecheck)
                    await message1.edit(embed=discord.Embed(
                        description='<a:8299_Loading:724051710468817048> Give me a moment while I analyze your team.'))
                    pokepastecontent = pokepaste.content
                    await pokepaste.delete()
                    driver = webdriver.Chrome()
                    driver.get(str(pokepastecontent))
                    count = 0
                    set = []
                    items = []
                    abilities = []
                    moves = []
                    evs = []
                    nature = []
                    suggestions = []
                    mons = driver.find_elements_by_tag_name("article")
                    while count < len(mons):
                        mon = mons[count].text
                        mon = mon.split()
                        set.append(mon[0])
                        if len(mon[mon.index('@')+1:mon.index('Ability:')]) == 2:
                            items.append(' '.join(mon[mon.index('@')+1:mon.index('Ability:')]))
                        else:
                            items.append(str(mon[mon.index('@')+1:mon.index('Ability:')]).strip("['']"))

                        if len(mon[mon.index('Ability:')+1:mon.index('EVs:')]) == 2:
                            abilities.append(' '.join(mon[mon.index('Ability:')+1:mon.index('EVs:')]))
                        else:
                            abilities.append(str(mon[mon.index('Ability:') + 1:mon.index('EVs:')]).strip("['']"))
                        evs.append(' '.join(mon[mon.index('EVs:')+1:mon.index('Nature')-1]))
                        nature.append(mon[mon.index('Nature')-1])

                        moves.append((' '.join(mon[mon.index('-')+1:len(mon)+1])).replace(' -', ', '))

                        count += 1

                    # Type checking
                    types = []
                    for i in set:
                        for a in pb.pokemon(str.lower(i)).types:
                            types.append(a.type.name)

                    weakness = {
                        'normal': 0,
                        'fighting': 0,
                        'flying': 0,
                        'poison': 0,
                        'ground': 0,
                        'rock': 0,
                        'bug': 0,
                        'ghost': 0,
                        'steel': 0,
                        'fire': 0,
                        'water': 0,
                        'grass': 0,
                        'electric': 0,
                        'psychic': 0,
                        'ice': 0,
                        'dragon': 0,
                        'dark': 0,
                        'fairy': 0
                    }

                    print(types)
                    for i in types:
                        weaknessCheck(weakness, i)



                    if 'Trick Room' in moves:
                        if moves.count('Trick Room') > 1:
                            suggestions.append('Only one TR setter is required.')
                        if 'Dusclops' not in set:
                            suggestions.append('Dusclops is a way better alternative as a TR setter.')


                    print(items)
                    print(abilities)
                    print(evs)
                    print(nature)
                    print(moves)


                except asyncio.TimeoutError:
                    await message1.edit(embed=discord.Embed(description=ctx.message.author.mention + ' You have been timed out.'))


        except asyncio.TimeoutError:
            await message1.edit(embed=discord.Embed(description=ctx.message.author.mention + ' You have been timed out.'))

    @commands.command()
    async def test(self, ctx):
        driver = webdriver.Chrome()
        driver.get("https://www.smogon.com/dex/sm/pokemon/shuckle/")
        button = driver.find_element_by_xpath('//*[@id="container"]/div/main/div/section/section[2]/div/div[2]/div[2]/div/button')
        button.click()
        content = driver.page_source
        soup = BeautifulSoup(content)
        ta = soup.find('textarea')
        print(ta.get_text())

    @commands.command()
    async def test2(self, ctx):
        driver = webdriver.Chrome()
        driver.get("https://pokepast.es/09006e32c5d387f5")
        count = 0
        set = []
        mons = driver.find_elements_by_tag_name("article")
        while count < len(mons):
            mon = mons[count].text
            mon = mon.split()
            set.append(mon[0])
            count += 1
        print(set)


def setup(client):
    client.add_cog(TeamBuilding(client))