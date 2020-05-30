import discord
from discord.ext import commands
import sqlite3
import re

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
    async def createvc(self, ctx, *, name=''):
        if name:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT user_id FROM CustomVCs WHERE user_id = {ctx.message.author.id}').fetchone()
            if row is None:
                step1 = True
                message1 = await ctx.message.channel.send(embed=discord.Embed(
                    description="How many slots do you want your channel to have? (0-99) 0 being infinite slots."))
                while step1:

                    def check(msg):
                        return ctx.message.channel == msg.channel and msg.author.id == ctx.message.author.id
                    slots = await self.client.wait_for('message', check=check)
                    if re.search("[0-99]", slots.content):
                        slots1 = slots.content
                        step1 = False
                        await slots.delete()
                    else:
                        await message1.edit(embed=discord.Embed(
                            description="Incorrect response. Please tell me how many slots you want your channel to have from 0-99 and 0 being infinite slots."))

                await message1.edit(embed=discord.Embed(
                    description="Do you want this VC to be public or private?"))

                def check2(msg):
                    return ctx.message.channel == msg.channel and msg.author.id == ctx.message.author.id and (str.lower(msg.content) == 'public' or str.lower(msg.content) == 'private')

                type = await self.client.wait_for('message', check=check2)
                type2 = type.content
                await type.delete()

                category = discord.utils.get(ctx.guild.categories, name='🔊 Voice Chats 🔊')
                if slots1 == 0:
                    new_chan = await ctx.guild.create_voice_channel(name, category=category)
                    if type2 == 'private':
                        await new_chan.set_permissions(discord.utils.get(ctx.message.guild.roles, name='Member'),
                                                       view_channel=False)
                        await new_chan.set_permissions(ctx.message.author, view_channel=True)
                    else:
                        await new_chan.set_permissions(discord.utils.get(ctx.message.guild.roles, name='Member'),
                                                       view_channel=True)
                else:
                    new_chan = await ctx.guild.create_voice_channel(name, category=category, user_limit=slots1)
                    if type2 == 'private':
                        await new_chan.set_permissions(discord.utils.get(ctx.message.guild.roles, name='Member'),
                                                       view_channel=False)
                        await new_chan.set_permissions(ctx.message.author, view_channel=True)
                    else:
                        await new_chan.set_permissions(discord.utils.get(ctx.message.guild.roles, name='Member'),
                                                       view_channel=True)


                help_embed = discord.Embed(title="<:SeekPng:705124992349896795> "  + ctx.message.author.display_name + " Voice channel named '" + name + "' has been created.",
                                           description="Use **$help** for a list of commands that you can use while your VC is active.")
                help_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/704174855813070901/715387986191056956/kissclipart-speakers-emoji-png-clipart-loudspeaker-clip-art-07d31b3095b35b4b.png")
                help_embed.set_footer(text="Don't forget to delete this voice channel once you're done using it!")
                await message1.edit(embed=help_embed)

                # Write user and channel info into DB for later use
                cursor.execute(
                    """INSERT INTO CustomVCs (user_id, channel_id, invite) VALUES (?, ?, ?)""",
                    (ctx.message.author.id, new_chan.id, type2))
                db.commit()

            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description=
                    '<:x_:705214517961031751>  **You already have a channel created.**'))
            cursor.close()
            db.close()
        else:
            await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751>  **Invalid syntax. Please provide a name after the command. Example:** ***$createvc channelname***'))
        await ctx.message.delete()

    # Delete a custom vc
    @commands.command()
    async def deletevc(self, ctx):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute(f'SELECT * FROM CustomVCs WHERE user_id = {ctx.message.author.id}').fetchone()
        if row:
            mutedrow = cursor.execute(f'SELECT * FROM MutedVC WHERE channel_id = {row[1]}').fetchone()
            bannedrow = cursor.execute(f'SELECT * FROM BannedVC WHERE channel_id = {row[1]}').fetchone()
            invitedrow = cursor.execute(f'SELECT * FROM InvitedVC WHERE channel_id = {row[1]}').fetchone()

            await ctx.guild.get_channel(row[1]).delete()

            if mutedrow:
                cursor.execute(f'DELETE FROM MutedVC WHERE channel_id = {row[1]}')
                db.commit()
            if bannedrow:
                cursor.execute(f'DELETE FROM BannedVC WHERE channel_id = {row[1]}')
                db.commit()
            if invitedrow:
                cursor.execute(f'DELETE FROM InvitedVC WHERE channel_id = {row[1]}')
                db.commit()
            cursor.execute(f'DELETE FROM CustomVCs WHERE user_id = {ctx.message.author.id}')
            db.commit()
            await ctx.message.channel.send(
                embed=discord.Embed(description='<:SeekPng:705124992349896795> ' + ctx.message.author.mention + ' **Your custom VC was successfully deleted.**'))
        else:
            await ctx.message.channel.send(
                embed=discord.Embed(description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **You do not have any custom VCs created.**'))
        await ctx.message.delete()
        cursor.close()
        db.close()

    # Invite someone to your private VC
    @commands.command()
    async def vcinvite(self, ctx, member: discord.Member = ''):
        if member:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT * FROM CustomVCs WHERE user_id = {ctx.message.author.id}').fetchone()
            if row:
                invitedrow = cursor.execute(
                    f'SELECT * FROM InvitedVC WHERE user_id = {member.id} AND channel_id = {row[1]}').fetchone()
                if row[2] == 'private':
                    if invitedrow is None:
                        cursor.execute(
                            """INSERT INTO InvitedVC (user_id, channel_id) VALUES (?, ?)""",
                            (member.id, row[1]))
                        db.commit()
                        vc = discord.utils.get(ctx.message.guild.voice_channels, id=row[1])
                        await vc.set_permissions(member, view_channel=True)
                        await ctx.message.channel.send(embed=discord.Embed(
                            description='<:SeekPng:705124992349896795> ' + member.mention + ' **can now access your custom VC.**'))
                    else:
                        await ctx.message.channel.send(embed=discord.Embed(
                            description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **This person has already been invited to your custom VC.**'))
                else:
                    await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **You cannot invite someone to a public VC.**'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **You do not have any custom VCs created.**'))
            cursor.close()
            db.close()
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **Please specify a user to invite.**'))
        await ctx.message.delete()

    @commands.command()
    async def vcmute(self, ctx, member: discord.Member = ''):
        if member:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT * FROM CustomVCs WHERE user_id = {ctx.message.author.id}').fetchone()
            if row:
                mutedrow = cursor.execute(
                    f'SELECT * FROM MutedVC WHERE user_id = {member.id} AND channel_id = {row[1]}').fetchone()
                if mutedrow is None:
                    cursor.execute(
                        """INSERT INTO MutedVC (user_id, channel_id) VALUES (?, ?)""",
                        (member.id, row[1]))
                    db.commit()
                    vc = discord.utils.get(ctx.message.guild.voice_channels, id=row[1])
                    await vc.set_permissions(member, speak=False)
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:SeekPng:705124992349896795> ' + member.mention + ' **has been muted in your custom VC.**'))
                else:
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **This person has already been muted in your custom VC.**'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **You do not have any custom VCs created.**'))
            cursor.close()
            db.close()
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **Please specify a user to mute.**'))
        await ctx.message.delete()

    @commands.command()
    async def vcunmute(self, ctx, member: discord.Member = ''):
        if member:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT * FROM CustomVCs WHERE user_id = {ctx.message.author.id}').fetchone()
            if row:
                mutedrow = cursor.execute(
                    f'SELECT * FROM MutedVC WHERE user_id = {member.id} AND channel_id = {row[1]}').fetchone()
                if mutedrow:
                    cursor.execute(f'DELETE FROM MutedVC WHERE user_id = {member.id} AND channel_id = {row[1]}')
                    db.commit()
                    vc = discord.utils.get(ctx.message.guild.voice_channels, id=row[1])
                    await vc.set_permissions(member, speak=True)
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:SeekPng:705124992349896795> ' + member.mention + ' **has been unmuted in your custom VC.**'))
                else:
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **This person is not muted in your custom VC.**'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **You do not have any custom VCs created.**'))
            cursor.close()
            db.close()
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **Please specify a user to unmute.**'))
        await ctx.message.delete()

    @commands.command()
    async def vcban(self, ctx, member: discord.Member = ''):
        if member:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT * FROM CustomVCs WHERE user_id = {ctx.message.author.id}').fetchone()
            if row:
                bannedrow = cursor.execute(
                    f'SELECT * FROM BannedVC WHERE user_id = {member.id} AND channel_id = {row[1]}').fetchone()
                if bannedrow is None:
                    cursor.execute(
                        """INSERT INTO BannedVC (user_id, channel_id) VALUES (?, ?)""",
                        (member.id, row[1]))
                    db.commit()
                    vc = discord.utils.get(ctx.message.guild.voice_channels, id=row[1])
                    await vc.set_permissions(member, view_channel=False)
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:SeekPng:705124992349896795> ' + member.mention + ' **has been banned from your custom VC.**'))
                else:
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **This person is already banned from your custom VC.**'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **You do not have any custom VCs created.**'))
            cursor.close()
            db.close()
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **Please specify a user to ban.**'))
        await ctx.message.delete()

    @commands.command()
    async def vcunban(self, ctx, member: discord.Member = ''):
        if member:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(f'SELECT * FROM CustomVCs WHERE user_id = {ctx.message.author.id}').fetchone()
            if row:
                bannedrow = cursor.execute(
                    f'SELECT * FROM BannedVC WHERE user_id = {member.id} AND channel_id = {row[1]}').fetchone()
                if bannedrow:
                    cursor.execute(f'DELETE FROM BannedVC WHERE user_id = {member.id} AND channel_id = {row[1]}')
                    db.commit()
                    vc = discord.utils.get(ctx.message.guild.voice_channels, id=row[1])
                    await vc.set_permissions(member, view_channel=True)
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:SeekPng:705124992349896795> ' + member.mention + ' **has been unbanned from your custom VC.**'))
                else:
                    await ctx.message.channel.send(embed=discord.Embed(
                        description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **This person is not banned from your custom VC.**'))
            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **You do not have any custom VCs created.**'))
            cursor.close()
            db.close()
        else:
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:x_:705214517961031751> ' + ctx.message.author.mention + ' **Please specify a user to unban.**'))
        await ctx.message.delete()


def setup(client):
    client.add_cog(CustomVCs(client))