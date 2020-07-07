import discord
from discord.ext import commands
import praw
import random

reddit = praw.Reddit(client_id='Jup8dCL4JJwQoQ',
                     client_secret='1txH9y-X_EXmyKm1VxcY7IWey-0',
                     user_agent='Meme Searcher v1.0')

class RandomMeme(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('RandomMeme cog is loaded.')

    @commands.command()
    async def meme(self, ctx):
        memes_submissions = reddit.subreddit('memes').hot()
        post_to_pick = random.randint(1, 100)
        for i in range(0, post_to_pick):
            submission = next(x for x in memes_submissions if not x.stickied)

        await ctx.message.channel.send(submission.url)



def setup(client):
    client.add_cog(RandomMeme(client))