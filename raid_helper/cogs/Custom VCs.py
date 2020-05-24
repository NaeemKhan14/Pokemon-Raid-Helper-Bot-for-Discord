import discord
from discord.ext import commands
import sqlite3

class CustomVCs(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS CustomVCs
            (
                user_id	INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                invite TEXT,
                PRIMARY KEY(user_id)
            )
            ''')
        cursor.execute("""CREATE TABLE IF NOT EXISTS InvitedVC AS SELECT * FROM CustomVCs""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS BannedVC AS SELECT * FROM CustomVCs""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS MutedVC AS SELECT * FROM CustomVCs""")
        cursor.close()
        db.close()
        print('Custom VCs cog is loaded.')


    # Create a custom vc
    @commands.command()
    async def createvc(self, ctx, name=''):
        if name:
            pass
        else:
            await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751>  **Invalid syntax. Please provide a name after the command. Example:** ***$createvc channelname***'))


def setup(client):
    client.add_cog(CustomVCs(client))