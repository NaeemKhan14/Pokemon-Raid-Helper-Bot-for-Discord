import discord
from discord.ext import commands
import random
import sqlite3
import asyncio



man = [
    (
        '    **___**    \n'
        '   **|\u200b \u200b \u200b \u200b |**   \n'
        '   **|**\u200b \u200b \u200b \u200bX   \n'
        '   **|**\u200b \u200b\u200b\u200b\\ | / \n'
        '   **|**\u200b \u200b \u200b \u200b  |   \n'
        '   **|**\u200b \u200b \u200b\u200b/ \\ \n'
        '   **|**       \n'
    ), (
        '    **___**    \n'
        '   **|\u200b \u200b \u200b \u200b  |**   \n'
        '   **|**\u200b \u200b \u200b \u200bO   \n'
        '   **|**\u200b \u200b\u200b\u200b\\ | / \n'
        '   **|**\u200b \u200b \u200b \u200b  |   \n'
        '   **|**\u200b \u200b \u200b\u200b/    \n'
        '   **|**       \n'
    ), (
        '    **___**    \n'
        '   **|\u200b \u200b \u200b \u200b  |**   \n'
        '   **|**\u200b \u200b \u200b \u200bO   \n'
        '   **|**\u200b \u200b\u200b\u200b\\ | / \n'
        '   **|**\u200b \u200b \u200b \u200b  |   \n'
        '   **|**       \n'
        '   **|**       \n'
    ), (
        '    **___**    \n'
        '   **|\u200b \u200b \u200b \u200b   |**   \n'
        '   **|**\u200b \u200b \u200b \u200bO   \n'
        "   **|**\u200b \u200b\u200b\u200b\\ |  \n"
        '   **|**\u200b \u200b \u200b \u200b |   \n'
        '   **|**       \n'
        '   **|**       \n'
    ), (
        '    **___**    \n'
        '   **|\u200b \u200b \u200b \u200b  |**   \n'
        '   **|**\u200b \u200b \u200b \u200bO   \n'
        '   **|**\u200b \u200b \u200b \u200b  |   \n'
        '   **|**\u200b \u200b \u200b \u200b  |   \n'
        '   **|**       \n'
        '   **|**       \n'
    ), (
        '    **___**    \n'
        '   **|\u200b \u200b \u200b \u200b |**   \n'
        '   **|**\u200b \u200b \u200b \u200bO   \n'
        '   **|**       \n'
        '   **|**       \n'
        '   **|**       \n'
        '   **|**       \n'
    ), (
        '    **___**    \n'
        '   **|\u200b \u200b \u200b \u200b     |**   \n'
        '   **|**      \n'
        '   **|**       \n'
        '   **|**       \n'
        '   **|**       \n'
        '   **|**       \n'
    )
]

class Hangman(commands.Cog, discord.Client):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Hangman
            (
                user_id	INTEGER NOT NULL,
                message_id INTEGER,
                guesses_left INTEGER NOT NULL,
                guessed_letters TEXT,
                word TEXT,
                blanks TEXT,
                letters_found INTEGER,
                PRIMARY KEY(user_id)
            )
            ''')
        cursor.close()
        db.close()
        print('Hangman cog is loaded.')

    @commands.command()
    async def hangman(self, ctx, theme=''):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute(f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
        str.lower(theme)
        if row is None and theme != 'themes':
            lines = []
            if theme == 'classic':
                with open("/home/eric/Pokemon-Raid-Helper-Bot-for-Discord/raid_helper/cogs/hangmanwords.txt", "r") as f:
                    lines = f.readlines()
            elif theme == 'pokemon':
                with open("/home/eric/Pokemon-Raid-Helper-Bot-for-Discord/raid_helper/cogs/hangmanpokemon.txt", "r") as f:
                    lines = f.readlines()


            random_line_num = random.randrange(0, len(lines))
            word = lines[random_line_num]
            print(word)
            f.close()
            blanks=[]
            for i in range(1, len(word)):
                blanks.append("_")
            hangmanembed = discord.Embed(description="**Welcome to Hangman" + ctx.message.author.mention + "!** Your current theme is **" + theme + "**. You have 6 guesses to get all of the letters in the word. To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n Use **$hangman themes** for a list of avaialble themes. \n \n \_\_" + "\_\_​​ ​​​​​​​​​​\u200b \u200b \u200b \u200b \_\_".join(blanks) + "\_\_")
            hangmanembed.set_image(url='https://cdn.discordapp.com/attachments/704174855813070901/713472024919670833/dominatehangman-1600.png')
            hangmanmsg = await ctx.message.channel.send(embed=hangmanembed)
            blank = ",".join(blanks)

            cursor.execute(
                """INSERT INTO Hangman (user_id, message_id, guesses_left, word, blanks, letters_found) VALUES (?, ?, ?, ?, ?, ?)""",
                (ctx.message.author.id, hangmanmsg.id, 6, word, blank, 0))
            db.commit()
        elif theme == 'themes':
            await ctx.message.channel.send(embed=discord.Embed(
                description='Use **$hangman {theme}** to play Hangman with specific themes. Themes include: **Classic** and **Pokemon**'))
        else:
            await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751> You are already in a game. Do **$hangmanend** to end your game.'))
        cursor.close()
        db.close()


    @commands.command()
    async def guess(self, ctx, guess):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute(f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
        if row:
            if row[3]:
                if str.isalpha(guess) and len(guess) is 1 and str.lower(guess) not in row[3]:
                    hangmanmsg = await ctx.message.channel.fetch_message(row[1])
                    if hangmanmsg:
                        matches = [x for x, letter in enumerate(row[4]) if letter == guess]
                        if matches:
                            for i in matches:
                                row = cursor.execute(
                                    f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
                                blanks = row[5].split(',')
                                blanks[i] = str.lower(guess)
                                blanks2 = ",".join(blanks)
                                cursor.execute("UPDATE HangMan SET blanks = ? WHERE user_id = ?",
                                               (blanks2, ctx.message.author.id))
                                db.commit()

                                lettersfound = row[6] + 1
                                cursor.execute(
                                    f'UPDATE Hangman SET letters_found = {lettersfound} WHERE user_id = {ctx.message.author.id}')
                                db.commit()

                            # Adds guessed letter to the list and if one value then it's string
                            row[3].split(',')
                            if type(row[3]) is str:
                                guessedletters = []
                                guessedletters.append(row[3])
                                guessedletters.append(guess)
                                guessedletters = ",".join(guessedletters)
                            else:
                                guessedletters = row[3].append(str.lower(guess))
                                guessedletters = ",".join(guessedletters)
                            cursor.execute("UPDATE HangMan SET guessed_letters = ? WHERE user_id = ?",
                                           (guessedletters, ctx.message.author.id))
                            db.commit()
                            row = cursor.execute(
                                f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()

                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman, " + ctx.message.author.mention + "!** \n You have " + str(row[2]) + " guesses to get all of the letters in the word. \n"
                                                                            "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n Use **$hangman themes** for a list of avaialble themes.\n \n \_\_**" + "**\_\_    \_\_**".join(
                                    row[5].split(',')) + "**\_\_ \n Guessed letters: **" + ", ".join(
                                    row[3].split(',')) + '**\n' + man[row[2]]))


                        else:
                            guessesleft = row[2] - 1
                            cursor.execute(
                                f'UPDATE Hangman SET guesses_left = {guessesleft} WHERE user_id = {ctx.message.author.id}')
                            db.commit()
                            row[3].split(',')
                            if type(row[3]) is str:
                                guessedletters = []
                                guessedletters.append(row[3])
                                guessedletters.append(guess)
                                guessedletters = ",".join(guessedletters)
                            else:
                                guessedletters = row[3].append(str.lower(guess))
                                guessedletters = ",".join(guessedletters)
                            cursor.execute("UPDATE HangMan SET guessed_letters = ? WHERE user_id = ?",
                                           (guessedletters, ctx.message.author.id))
                            db.commit()
                            row = cursor.execute(
                                f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman, " + ctx.message.author.mention + "!** \n You have " + str(
                                    row[2]) + " guesses to get all of the letters in the word. \n"
                                              "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n Use **$hangman themes** for a list of avaialble themes.\n \n \_\_**" + "**\_\_    \_\_**".join(
                                    row[5].split(',')) + "**\_\_ \n Guessed letters: **" + ", ".join(
                                    row[3].split(',')) + '**\n' + man[row[2]]))

                        if row[2] == 0:
                            await hangmanmsg.edit(embed=discord.Embed(description=ctx.message.author.mention + " No guesses left. **You lose!** The word was: **" + row[4] + "**\n Guessed letters: **" + ", ".join(
                                row[3].split(',')) + '**\n' + man[row[2]]))
                            cursor.execute(f'DELETE FROM Hangman WHERE user_id = {ctx.message.author.id}')
                            db.commit()
                        if row[6] == len(row[4])-1:
                            await hangmanmsg.edit(embed=discord.Embed(description=ctx.message.author.mention + " You guessed all the letters! **You've won!** The word was: **" + row[4] + '** \n Guessed letters: **' + ", ".join(
                                    row[3].split(',')) + '**\n' + man[row[2]]).set_thumbnail(url='https://cdn.discordapp.com/attachments/704174855813070901/714603464675688508/trophy.png'))
                            cursor.execute(f'DELETE FROM Hangman WHERE user_id = {ctx.message.author.id}')
                            db.commit()
                    else:
                        message2 = await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> " + ctx.message.author.mention + " **Please use the $guess command in the same channel where you started the game**"))
                        await asyncio.sleep(30)
                        await message2.delete()

                else:
                    message2 = await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> " + ctx.message.author.mention + " You can only guess with single letters that haven't already been entered. Guessed letters: **" + ", ".join(row[3].split(',')) + '**'))
                    await asyncio.sleep(30)
                    await message2.delete()

            else:
                if str.isalpha(guess) and len(guess) is 1:
                    hangmanmsg = await ctx.message.channel.fetch_message(row[1])
                    if hangmanmsg:
                        matches = [x for x, letter in enumerate(row[4]) if letter == guess]
                        if matches:
                            for i in matches:
                                row = cursor.execute(
                                    f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
                                blanks = row[5].split(',')
                                blanks[i] = str.lower(guess)
                                blanks2 = ",".join(blanks)
                                cursor.execute("UPDATE HangMan SET blanks = ? WHERE user_id = ?", (blanks2, ctx.message.author.id))
                                db.commit()

                                lettersfound = row[6] + 1
                                cursor.execute(
                                    f'UPDATE Hangman SET letters_found = {lettersfound} WHERE user_id = {ctx.message.author.id}')
                                db.commit()

                            cursor.execute("UPDATE HangMan SET guessed_letters = ? WHERE user_id = ?", (guess, ctx.message.author.id))
                            db.commit()
                            row = cursor.execute(
                                f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()

                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman, " + ctx.message.author.mention + "!** \n You have " + str(row[2]) + " guesses to get all of the letters in the word. \n"
                                                                            "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n Use **$hangman themes** for a list of avaialble themes.\n \n \_\_**" + "**\_\_    \_\_**".join(
                                    row[5].split(',')) + "**\_\_ \n Guessed letters: **" +
                                    str(row[3]) + '**\n' + man[row[2]]))


                        else:
                            guessesleft = row[2] - 1
                            cursor.execute(
                                f'UPDATE Hangman SET guesses_left = {guessesleft} WHERE user_id = {ctx.message.author.id}')
                            db.commit()

                            cursor.execute("UPDATE HangMan SET guessed_letters = ? WHERE user_id = ?",
                                           (guess, ctx.message.author.id))
                            db.commit()
                            row = cursor.execute(
                                f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman, " + ctx.message.author.mention + "!** \n You have " + str(
                                    row[2]) + " guesses to get all of the letters in the word. \n"
                                              "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n Use **$hangman themes** for a list of avaialble themes.\n \n \_\_**" + "**\_\_    \_\_**".join(
                                    row[5].split(',')) + "**\_\_ \n Guessed letters: **" + row[3] + '**\n' + man[row[2]]))

                    else:
                        message2 = await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> " + ctx.message.author.mention + " **Please use the $guess command in the same channel where you started the game**"))
                        await asyncio.sleep(30)
                        await message2.delete()

                else:
                    message2 = await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> " + ctx.message.author.mention + " You can only guess with single letters that haven't already been entered. Guessed letters: **" + " ".join(row[3]) + '**'))
                    await asyncio.sleep(30)
                    await message2.delete()

        else:
            message2 = await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> " + ctx.message.author.mention + " Start a game of Hangman with **$hangman** before trying to guess a letter!"))
            await asyncio.sleep(30)
            await message2.delete()

        await ctx.message.delete()
        cursor.close()
        db.close()


    @commands.command()
    async def hangmanend(self, ctx):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute(f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
        if row:
            hangmanmsg = await ctx.message.channel.fetch_message(row[1])
            if hangmanmsg:
                await hangmanmsg.delete()
            await ctx.message.channel.send(embed=discord.Embed(
                description='<:SeekPng:705124992349896795> ' + ctx.message.author.mention + ' Game successfully ended. The word was: **' +
                            row[4] + '**'))
            cursor.execute(f'DELETE FROM Hangman WHERE user_id = {ctx.message.author.id}')
            db.commit()

        else:
            await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> " + ctx.message.author.mention + " **You do not have a game created**"))
        await ctx.message.delete()
        cursor.close()
        db.close()

    @commands.command()
    @commands.has_role('Owner')
    async def hangmanclear(self, ctx, user_id=''):
        if user_id:
            db = sqlite3.connect('RaidHelper.sqlite')
            cursor = db.cursor()
            row = cursor.execute(
                f'SELECT * FROM Hangman WHERE user_id = {user_id}').fetchone()
            if row:
                cursor.execute(f'DELETE FROM Hangman WHERE user_id = {user_id}')
                db.commit()
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:SeekPng:705124992349896795>  **Database successfully cleared for user.**'))

            else:
                await ctx.message.channel.send(embed=discord.Embed(
                    description='<:x_:705214517961031751>  **User with specified ID does not exist in the database.**'))

            cursor.close()
            db.close()


def setup(client):
    client.add_cog(Hangman(client))