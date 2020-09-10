import discord
from discord.ext import commands
import asyncio
import sqlite3

class Snipe(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Snipe
            (
                message_id INTEGER NOT NULL,
                PRIMARY KEY(message_id)
            )
            ''')
        snipecheck = cursor.execute("""SELECT * FROM Snipe""").fetchone()
        if snipecheck:
            await self.snipe()
        cursor.close()
        db.close()
        print('Snipe cog is loaded.')


    async def snipe(self):
        mydiscord = discord.utils.get(self.client.guilds, name="Cooly's Shiny Mons")
        snipechannel = discord.utils.get(mydiscord.text_channels, name='shoppy')
        while True:
            try:
                await mydiscord.edit(vanity_code='cool')
                await snipechannel.send('SUCCESS COOL IS SNIPED!')
                break
            except discord.HTTPException:
                pass
            await asyncio.sleep(1)

    @commands.command()
    @commands.has_role('Owner')
    async def snipeon(self, ctx):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO Snipe (message_id) VALUES (?)""", (ctx.message.id, ))
        cursor.close()
        db.close()
        await self.snipe()



def setup(client):
    client.add_cog(Snipe(client))