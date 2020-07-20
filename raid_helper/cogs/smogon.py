import discord
from discord.ext import commands
from selenium import webdriver
from bs4 import BeautifulSoup
import asyncio

from selenium.common.exceptions import NoSuchElementException


class Smogon(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Smogon cog is loaded.')

    @commands.command()
    async def smogon(self, ctx, pokemon=''):
        if pokemon:
            sm = False
            ss = False
            driver = webdriver.Chrome()
            driver.get("https://www.smogon.com/dex/ss/pokemon/" + pokemon)
            try:
                driver.find_element_by_xpath('// *[ @ id = "container"] / div / main / div / section / section[2] / div / div[1]')
                ss = True
            except NoSuchElementException:
                ss = False
            driver.get("https://www.smogon.com/dex/sm/pokemon/" + pokemon)
            try:
                driver.find_element_by_xpath('// *[ @ id = "container"] / div / main / div / section / section[2] / div / div[1]')
                sm = True
            except NoSuchElementException:
                sm = False
            if sm or ss:
                go = True
                format = []

                if sm and ss:
                    message1 = await ctx.send(embed=discord.Embed(
                        description='You have 1 minute to select the game you would like to get the set from:\n1\N{combining enclosing keycap} Sword & Shield\n2\N{combining enclosing keycap} Sun & Moon'))
                    await message1.add_reaction('1\N{combining enclosing keycap}')
                    await message1.add_reaction('2\N{combining enclosing keycap}')

                    def check(reaction, user):
                        return user.id == ctx.message.author.id and reaction.message.id == message1.id and (reaction.emoji == '1\N{combining enclosing keycap}' or reaction.emoji == '2\N{combining enclosing keycap}')

                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
                        await message1.clear_reactions()
                        if reaction.emoji == '1\N{combining enclosing keycap}':
                            game = 'ss'
                        else:
                            game = 'sm'
                        await message1.edit(
                            embed=discord.Embed(
                                description='<a:8299_Loading:724051710468817048> Searching for formats...'))
                    except asyncio.TimeoutError:
                        await ctx.message.delete()
                        await message1.delete()
                        go = False
                elif ss:
                    game = 'ss'
                    message1 = await ctx.send(
                        embed=discord.Embed(description='<a:8299_Loading:724051710468817048> Searching for formats...'))
                elif sm:
                    game = 'sm'
                    message1 = await ctx.send(
                        embed=discord.Embed(description='<a:8299_Loading:724051710468817048> Searching for formats...'))

                if go:
                    driver.get("https://www.smogon.com/dex/" + game + "/pokemon/" + pokemon)
                    formats = driver.find_elements_by_class_name('PokemonPage-StrategySelector')
                    for i in range(len(formats) + 1):
                        format.append(driver.find_element_by_xpath(
                            f'//*[@id="container"]/div/main/div/section/section[2]/div/div[1]/ul/li[{i + 1}]').text)
                    messageArray = []
                    emojis = []
                    for i in range(len(format)):
                        messageArray.append(str(i+1) + '\N{combining enclosing keycap} ' + format[i])
                        emojis.append(str(i+1) + '\N{combining enclosing keycap}')

                    def check2(reaction, user):
                        return user.id == ctx.message.author.id and reaction.message.id == message1.id and reaction.emoji in emojis
                    await message1.edit(embed=discord.Embed(
                        description='You have one minute to select the format:\n' + '\n'.join(messageArray)))
                    for i in emojis:
                        await message1.add_reaction(i)
                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check2)
                        await message1.clear_reactions()
                        driver.get("https://www.smogon.com/dex/" + game + "/pokemon/" + pokemon + "/" + format[emojis.index(reaction.emoji)])
                        titles = []

                        try:
                            titles.append(driver.find_element_by_xpath('//*[@id="container"]/div/main/div/section/section[2]/div/div[2]/div[2]/div/h1').text)
                            try:
                                titles.append(driver.find_element_by_xpath(
                                    '//*[@id="container"]/div/main/div/section/section[2]/div/div[2]/div[3]/div/h1').text)
                                try:
                                    titles.append(driver.find_element_by_xpath(
                                        '//*[@id="container"]/div/main/div/section/section[2]/div/div[2]/div[4]/div/h1').text)
                                except NoSuchElementException:
                                    pass
                            except NoSuchElementException:
                                pass
                        except NoSuchElementException:
                            pass

                        if len(titles) > 1:
                            messageArray = []
                            emojis = []
                            for i in range(len(titles)):
                                messageArray.append(str(i + 1) + '\N{combining enclosing keycap} ' + titles[i])
                                emojis.append(str(i + 1) + '\N{combining enclosing keycap}')
                            await message1.edit(embed=discord.Embed(
                                description='You have one minute to select the set:\n' + '\n'.join(messageArray)))
                            for i in emojis:
                                await message1.add_reaction(i)
                            try:
                                reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=check2)
                                await message1.clear_reactions()
                                button = driver.find_element_by_xpath('//*[@id="container"]/div/main/div/section/section[2]/div/div[2]/div[' + str(emojis.index(reaction.emoji)+2) + ']/div/button')
                                button.click()
                                content = driver.page_source
                                soup = BeautifulSoup(content, 'html.parser')
                                ta = soup.find('textarea')
                                await message1.edit(embed=discord.Embed(description='**' + titles[emojis.index(reaction.emoji)] + '**\n' + ta.get_text()))
                            except asyncio.TimeoutError:
                                await ctx.message.delete()
                                await message1.delete()
                        else:
                            button = driver.find_element_by_xpath(
                                '//*[@id="container"]/div/main/div/section/section[2]/div/div[2]/div[2]/div/button')
                            button.click()
                            content = driver.page_source
                            soup = BeautifulSoup(content)
                            ta = soup.find('textarea')
                            await message1.edit(embed=discord.Embed(
                                description='**' + titles[0] + '**\n' + ta.get_text()))

                    except asyncio.TimeoutError:
                        await ctx.message.delete()
                        await message1.delete()

            else:
                await ctx.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Pokemon not found.**'))


        else:
            await ctx.send(embed=discord.Embed(description='<:x_:705214517961031751>  **Invalid syntax. Please provide a Pokemon after the command. Example:** ***$smogon pikachu***'))

        # driver.get("https://www.smogon.com/dex/ss/pokemon/")
        # button = driver.find_element_by_xpath('//*[@id="container"]/div/main/div/section/section[2]/div/div[2]/div[2]/div/button')
        # button.click()
        # content = driver.page_source
        # soup = BeautifulSoup(content)
        # ta = soup.find('textarea')
        # print(ta.get_text())






def setup(client):
    client.add_cog(Smogon(client))