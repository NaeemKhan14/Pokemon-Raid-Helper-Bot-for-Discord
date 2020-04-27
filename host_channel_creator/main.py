import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN2')


class Raid_Helper(discord.Client):
    channel_creator = None
    new_chan = None

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
        server = discord.utils.get(self.guilds)
        # Ignore self messages
        if message.author == client.user:
            return
        # Respond to only those messages that start with given prefix
        if message.content.startswith('$t'): # TODO: Check user permission and allow HOSTS only to use this command
            self.channel_creator = message.author

            await message.channel.send(
                "Channel named " + message.content.split(' ')[-1] + " has been created")  # TODO: add error-handling
            self.new_chan = await server.create_text_channel(message.content.split(' ')[-1])
            # Set permissions for the user in this new channel
            await self.new_chan.set_permissions(message.author, manage_messages=True)

        # Mute user in channel
        if message.content.startswith('$mute'):
            if self.channel_creator == message.author:
                await self.new_chan.set_permissions(message.mentions[0], send_messages=False)
            else:
                pass  # TODO: Error message

        # Unmute user in channel
        if message.content.startswith('$unmute'):
            if self.channel_creator == message.author:
                await self.new_chan.set_permissions(message.mentions[0], send_messages=True)
            else:
                pass  # TODO: Error message

        # Kick user from server
        if message.content.startswith('$kick'):
            if self.channel_creator == message.author:
                await self.new_chan.send(
                    '' + message.mentions[0].name + " has been kicked from server by " + message.author.name)
                await message.mentions[0].kick(reason="You have been kicked by a host")
            else:
                pass  # TODO: Error message


# Initialize class object
client = Raid_Helper()
client.run(TOKEN)
