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

    async def on_message(self, message):
        server = discord.utils.get(self.guilds, name='Bot Testing')
        # Ignore self messages
        if message.author == client.user:
            return
        # Respond to only those messages that start with given prefix
        if message.content.startswith('$t'):
            await message.channel.send("Channel named " + message.content.split(' ')[-1] + " has been created") # TODO: add error-handling
            await server.create_text_channel(message.content.split(' ')[-1])


# Initialize class object
client = CustomClient()
client.run(TOKEN)
