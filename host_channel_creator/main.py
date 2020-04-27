import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class CustomClient(discord.Client):

    # Print in console that the bot has connected to server
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    # DM the new user a welcome message on join
    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, welcome to this amazingly empty discord server'
        )


# Initialize class object
client = CustomClient()
client.run(TOKEN)
