import discord
from discord.ext import commands
import json
import urllib.request
import string
import random



class RandomVid(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('RandomVid cog is loaded.')

    @commands.command()
    async def video(self, ctx):
        count = 1
        API_KEY = 'AIzaSyA_hXrUpjM3cQ0Kc-oKPWMJf90iit_R0jc'
        randoms = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))

        urlData = "https://www.googleapis.com/youtube/v3/search?key={}&maxResults={}&part=snippet&type=video&q={}".format(
            API_KEY, count, randoms)

        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request=urllib.request.Request(urlData, None, headers)

        webURL = urllib.request.urlopen(request)

        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        results = json.loads(data.decode(encoding))

        for data in results['items']:
            videoId = (data['id']['videoId'])

        await ctx.message.channel.send(embed=discord.Embed(description='https://www.youtube.com/watch?v=' + videoId))






def setup(client):
    client.add_cog(RandomVid(client))