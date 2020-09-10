import discord
from discord.ext import commands
import sqlite3

class RoleMenu(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS RoleMenu
            (
                notification_id	INTEGER NOT NULL,
                specific_id INTEGER NOT NULL,
                PRIMARY KEY(notification_id)
            )
            ''')
        cursor.close()
        db.close()
        print('RoleMenu cog is loaded.')

    # Force delete a custom vc
    @commands.command()
    @commands.has_role('Owner')
    async def rolemenu(self, ctx):
        rolechannel = discord.utils.get(self.client.get_all_channels(), name='roles')
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()

        specificmsg = await rolechannel.send(embed=discord.Embed(description="**Roles For Specific Channels:**\n*React to receive the role and unreact if you want to lose it.*"
                                                                                 "\n\n<a:acnh:753059949784858624> <a:right:753046208838238228> **Animal Crossing: New Horizons**\n\n"
                                                                             "<:pokemongo:753059982727184477> <a:right:753046208838238228> **Pokemon GO**"))

        notificationmsg = await rolechannel.send(embed=discord.Embed(description="**Notification Roles:**\n*React to receive the role and unreact if you want to lose it.*"
                                                                                 "\n\n<a:shiny:753045078137634848> <a:right:753046208838238228> **Shiny Raids**\n\n"
                                                                                 "<a:pokeball:753051810280767558> <a:right:753046208838238228> **Pokemon GO Raids (requires Pokemon Go role)**\n\n"
                                                                                 "<a:giveaway:753052588269633608> <a:right:753046208838238228> **Giveaways**\n\n"
                                                                                 "<a:event:753053074196660364> <a:right:753046208838238228> **Events**\n\n"
                                                                                 "<a:sword:753387555600203776> <a:right:753046208838238228> **Pokemon Battles**\n\n"
                                                                                 "<:jackbox:753054258487623753> <a:right:753046208838238228> **Jackbox**\n\n"
                                                                                 "<:smash:753056976463986739> <a:right:753046208838238228> **Smash Ultimate**\n\n"
                                                                                 "<:amongus:753058198692560953> <a:right:753046208838238228> **Among Us**"))
        cursor.execute(
            """INSERT INTO RoleMenu (notification_id, specific_id) VALUES (?, ?)""",
            (notificationmsg.id, specificmsg.id,))
        db.commit()

        await specificmsg.add_reaction("<a:acnh:753059949784858624>")
        await specificmsg.add_reaction("<:pokemongo:753059982727184477>")

        await notificationmsg.add_reaction("<a:shiny:753045078137634848>")
        await notificationmsg.add_reaction("<a:pokeball:753051810280767558>")
        await notificationmsg.add_reaction("<a:giveaway:753052588269633608>")
        await notificationmsg.add_reaction("<a:event:753053074196660364>")
        await notificationmsg.add_reaction("<a:sword:753387555600203776>")
        await notificationmsg.add_reaction("<:jackbox:753054258487623753>")
        await notificationmsg.add_reaction("<:smash:753056976463986739>")
        await notificationmsg.add_reaction("<:amongus:753058198692560953>")

        cursor.close()
        db.close()
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute("""SELECT * FROM RoleMenu WHERE notification_id IS NOT NULL""").fetchone()
        if payload.message_id == row[0]:
            if str(payload.emoji) == "<a:shiny:753045078137634848>":
                await payload.member.add_roles(
                    discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Shiny Raids'))
            elif str(payload.emoji) == "<a:pokeball:753051810280767558>" and discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon GO') in self.client.get_guild(payload.guild_id).get_member(payload.user_id).roles:
                await payload.member.add_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon GO Raids'))
            elif str(payload.emoji) == "<a:giveaway:753052588269633608>":
                await payload.member.add_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Giveaway'))
            elif str(payload.emoji) == "<a:event:753053074196660364>":
                await payload.member.add_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Events'))
            elif str(payload.emoji) == "<a:sword:753387555600203776>":
                await payload.member.add_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon Battles'))
            elif str(payload.emoji) == "<:jackbox:753054258487623753>":
                await payload.member.add_roles(
                    discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Jackbox'))
            elif str(payload.emoji) == "<:smash:753056976463986739>":
                await payload.member.add_roles(
                    discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Smash Ultimate'))
            elif str(payload.emoji) == "<:amongus:753058198692560953>":
                await payload.member.add_roles(
                    discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Among Us'))
        if payload.message_id == row[1]:
            if str(payload.emoji) == "<a:acnh:753059949784858624>":
                await payload.member.add_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Animal Crossing'))
            elif str(payload.emoji) == "<:pokemongo:753059982727184477>":
                await payload.member.add_roles(
                    discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon GO'))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute("""SELECT * FROM RoleMenu WHERE notification_id IS NOT NULL""").fetchone()
        if payload.message_id == row[0]:
            if str(payload.emoji) == "<:shiny:753045078137634848>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Shiny Raids'))
            elif str(payload.emoji) == "<:pokeball:753051810280767558>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(
                    discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon GO Raids'))
            elif str(payload.emoji) == "<:giveaway:753052588269633608>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Giveaway'))
            elif str(payload.emoji) == "<:event:753053074196660364>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Events'))
            elif str(payload.emoji) == "<:sword:753387555600203776>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon Battles'))
            elif str(payload.emoji) == "<:jackbox:753054258487623753>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Jackbox'))
            elif str(payload.emoji) == "<:smash:753056976463986739>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Smash Ultimate'))
            elif str(payload.emoji) == "<:amongus:753058198692560953>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Among Us'))
        if payload.message_id == row[1]:
            if str(payload.emoji) == "<:acnh:753059949784858624>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Animal Crossing'))
            elif str(payload.emoji) == "<:pokemongo:753059982727184477>":
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon GO'))
                await self.client.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(
                    discord.utils.get(self.client.get_guild(payload.guild_id).roles, name='Pokemon GO Raids'))



def setup(client):
    client.add_cog(RoleMenu(client))