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
            except NoSuchElementException:
                sm = False
            if sm and ss:
                await ctx.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **Pokemon not found.**'))
            elif sm:
                pass
            elif ss:
                pass
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