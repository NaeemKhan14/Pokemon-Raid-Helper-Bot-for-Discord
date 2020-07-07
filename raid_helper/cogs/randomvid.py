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
        API_KEY = 'AIzaSyAzHV9cVQXBzE6ydQ4kpYRZ6f55ZrMCfrA'
        randoms = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))

        urlData = "https://www.googleapis.com/youtube/v3/search?key={}&maxResults={}&part=snippet&type=video&q={}".format(
            API_KEY, count, randoms)

        webURL = urllib.request.urlopen(urlData)

        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        results = json.loads(data.decode(encoding))

        for data in results['items']:
            videoId = (data['id']['videoId'])

        await ctx.message.channel.send(embed=discord.Embed(description='https://www.youtube.com/watch?v=' + videoId))



def setup(client):
    client.add_cog(RandomVid(client))