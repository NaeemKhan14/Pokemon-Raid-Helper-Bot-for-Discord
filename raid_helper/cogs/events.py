import discord
from discord.ext import commands

class Events(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Game('discord.gg/cool | $help'))
        print('Events cog is loaded.')


    # Verify new players
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == discord.utils.get(self.client.get_all_channels(), name='verify'):
            if message.content == 'I agree':
                await message.author.add_roles(discord.utils.get(message.guild.roles, name='Member'))
            await message.delete()

    # Welcome DM
    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcomeembed = discord.Embed(title="Welcome to Cooly's Shiny Mons!", description='Read the rules and verify in **' +
            discord.utils.get(self.client.get_all_channels(), name='verify').mention +
            '**\n\n After you have verified, make sure to read **' + discord.utils.get(self.client.get_all_channels(), name='server-info').mention +
            '** for a description of what channels are for.\n\n If you have any questions, read **' + discord.utils.get(self.client.get_all_channels(), name='faq').mention
            + '**\n\n Give yourself a role in **' + discord.utils.get(self.client.get_all_channels(), name='roles').mention +
            '** to get notified for certain things happening in the server.\n\n If you have additional questions about the server that were not answered in **' + discord.utils.get(self.client.get_all_channels(), name='faq').mention + '** feel free to ask in **' + discord.utils.get(self.client.get_all_channels(), name='questions').mention + '** or DM a staff member.\n\n If you are ever banned and you believe it was unjustified you may appeal here: https://forms.gle/w1yhARVadckZMXPR6', color=0xf2e8bb)
        welcomeembed.set_thumbnail(url='https://cdn.discordapp.com/attachments/704174855813070901/721158854842384414/discordicon.gif')
        welcomeembed.set_footer(text='Darkrai • Created by Cooly4477 & Charming Potato',
                             icon_url='https://cdn.discordapp.com/attachments/704174855813070901/712733586632998963/491Darkrai.png')
        await member.send(embed=welcomeembed)




def setup(client):
    client.add_cog(Events(client))
