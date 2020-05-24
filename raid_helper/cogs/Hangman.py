import discord
from discord.ext import commands
import random
import sqlite3
import marshal




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
                blanks BLOB,
                letters_found INTEGER,
                PRIMARY KEY(user_id)
            )
            ''')
        cursor.close()
        db.close()
        print('Hangman cog is loaded.')

    @commands.command()
    async def hangman(self, ctx):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute(f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
        if row is None:
            lines = []
            with open("C:/Users/Eric/Desktop/Pokemon-Raid-Helper-Bot-for-Discord/raid_helper/cogs/hangmanwords.txt", "r") as f:
                lines = f.readlines()
            random_line_num = random.randrange(0, len(lines))
            word = lines[random_line_num]
            print(word)
            f.close()
            blanks=[]
            for i in range(1, len(word)):
                blanks.append("_")
            hangmanembed = discord.Embed(description="**Welcome to Hangman!** You have 6 guesses to get all of the letters in the word. To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n \n \_\_" + "\_\_​​ ​​​​​​​​​​\u200b \u200b \u200b \u200b \_\_".join(blanks) + "\_\_")
            hangmanembed.set_image(url='https://cdn.discordapp.com/attachments/704174855813070901/713472024919670833/dominatehangman-1600.png')
            hangmanmsg = await ctx.message.channel.send(embed=hangmanembed)
            blank = marshal.dumps(blanks)
            print(blank)
            cursor.execute(
                """INSERT INTO Hangman (user_id, message_id, guesses_left, word, blanks, letters_found) VALUES (?, ?, ?, ?, ?, ?)""",
                (ctx.message.author.id, hangmanmsg.id, 6, word, blank, 0))
            db.commit()
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
                        if str.lower(guess) in row[4]:
                            for i in range(0, len(row[4])):
                                if row[4][i] == str.lower(guess):
                                    blanks = marshal.loads(row[5])
                                    blanks[i] = str.lower(guess)
                                    blanks2 = marshal.dumps(blanks)
                                    cursor.execute(
                                        f'UPDATE Hangman SET blanks = {str(blanks2)} WHERE user_id = {ctx.message.author.id}')
                                    db.commit()
                                    lettersfound = row[6] + 1
                                    cursor.execute(
                                        f'UPDATE Hangman SET letters_found = {lettersfound} WHERE user_id = {ctx.message.author.id}')
                                    db.commit()
                            guessedletters = row[3].append(str.lower(guess))
                            cursor.execute(
                                f'UPDATE Hangman SET guessed_letters = {guessedletters} WHERE user_id = {ctx.message.author.id}')
                            db.commit()

                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman!** You have " + str(row[2]) + " guesses to get all of the letters in the word.  "
                                                                            "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n \n \_\_**" + "**\_\_    \_\_**".join(
                                    json.loads(row[5])) + "**\_\_ \n Guessed letters: **" + ", ".join(
                                    row[3]) + '**\n' + man[row[2]]))


                        else:
                            guessesleft = row[2] - 1
                            cursor.execute(
                                f'UPDATE Hangman SET guesses_left = {guessesleft} WHERE user_id = {ctx.message.author.id}')
                            db.commit()
                            guessedLetters = row[3].append(str.lower(guess))
                            cursor.execute(
                                f'UPDATE Hangman SET guesses_letters = {guessedLetters} WHERE user_id = {ctx.message.author.id}')
                            db.commit()

                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman!** You have " + str(
                                    row[2]) + " guesses to get all of the letters in the word.  "
                                              "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n \n \_\_**" + "**\_\_    \_\_**".join(
                                    json.loads(row[5])) + "**\_\_ \n Guessed letters: **" + ", ".join(
                                    row[3]) + '**\n' + man[row[2]]))

                        if row[2] == 0:
                            await hangmanmsg.edit(embed=discord.Embed(description="No guesses left. **You lose!** The word was: **" + row[4] + "**\n Guessed letters: **" + ", ".join(
                                row[3]) + '**\n' + man[row[2]]))
                        if row[6] == len(row[4])-1:
                            await hangmanmsg.edit(embed=discord.Embed(description="You guessed all the letters! **You've won!** The word was: **" + row[4] + '**').set_image(url='https://cdn.discordapp.com/attachments/704174855813070901/713472024919670833/dominatehangman-1600.png'))
                    else:
                        ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> **Please use the $guess command in the same channel where you started the game**"))

                else:
                    await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> You can only guess with single letters that haven't already been entered. Guessed letters: **" + " ".join(row[3]) + '**'))

            else:
                if str.isalpha(guess) and len(guess) is 1:
                    hangmanmsg = await ctx.message.channel.fetch_message(row[1])
                    if hangmanmsg:
                        if str.lower(guess) in row[4]:
                            for i in range(0, len(row[4])):
                                if row[4][i] == str.lower(guess):
                                    blanks = marshal.loads(row[5])
                                    blanks[i] = str.lower(guess)
                                    blanks2 = marshal.dumps(blanks)
                                    cursor.execute(
                                        f'UPDATE Hangman SET blanks = {blanks2} WHERE user_id = {ctx.message.author.id}')
                                    db.commit()
                                    lettersfound = row[6] + 1
                                    cursor.execute(
                                        f'UPDATE Hangman SET letters_found = {lettersfound} WHERE user_id = {ctx.message.author.id}')
                                    db.commit()
                            guessedletters = []
                            guessedletters2 = guessedletters.append(str.lower(guess))
                            guessedletters = json.dumps(guessedletters2)
                            cursor.execute(
                                f'UPDATE Hangman SET guessed_letters = {guessedletters} WHERE user_id = {ctx.message.author.id}')
                            db.commit()

                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman!** You have " + str(row[2]) + " guesses to get all of the letters in the word.  "
                                                                            "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n \n \_\_**" + "**\_\_    \_\_**".join(
                                    json.loads(row[5])) + "**\_\_ \n Guessed letters: **" + ", ".join(
                                    row[3]) + '**\n' + man[row[2]]))


                        else:
                            guessesleft = row[2] - 1
                            cursor.execute(
                                f'UPDATE Hangman SET guesses_left = {guessesleft} WHERE user_id = {ctx.message.author.id}')
                            db.commit()

                            guessedLetters = []
                            guessedletters2 = guessedLetters.append(str.lower(guess))
                            cursor.execute(
                                f'UPDATE Hangman SET guessed_letters = {guessedletters2} WHERE user_id = {ctx.message.author.id}')
                            db.commit()

                            await hangmanmsg.edit(
                                embed=discord.Embed(description="**Welcome to Hangman!** You have " + str(
                                    row[2]) + " guesses to get all of the letters in the word.  "
                                              "To guess a letter, type **$guess {letter}** \n To end the game, type **$hangmanend** \n \n \_\_**" + "**\_\_    \_\_**".join(
                                    json.loads(row[5])) + "**\_\_ \n Guessed letters: **" + ", ".join(
                                    row[3]) + '**\n' + man[row[2]]))

                        if row[2] == 0:
                            await hangmanmsg.edit(embed=discord.Embed(description="No guesses left. **You lose!** The word was: **" + row[4] + "**\n Guessed letters: **" + ", ".join(
                                row[3]) + '**\n' + man[row[2]]))
                        if row[6] == len(row[4])-1:
                            await hangmanmsg.edit(embed=discord.Embed(description="You guessed all the letters! **You've won!** The word was: **" + row[4] + '**').set_image(url='https://cdn.discordapp.com/attachments/704174855813070901/713472024919670833/dominatehangman-1600.png'))
                    else:
                        ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> **Please use the $guess command in the same channel where you started the game**"))

                else:
                    await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> You can only guess with single letters that haven't already been entered. Guessed letters: **" + " ".join(row[3]) + '**'))

        else:
            await ctx.message.channel.send(embed=discord.Embed(description="<:x_:705214517961031751> Start a game of Hangman with **$hangman** before trying to guess a letter!"))
        await ctx.message.delete()


    @commands.command()
    async def hangmanend(self, ctx):
        db = sqlite3.connect('RaidHelper.sqlite')
        cursor = db.cursor()
        row = cursor.execute(f'SELECT * FROM Hangman WHERE user_id = {ctx.message.author.id}').fetchone()
        if row:
            hangmanmsg = await ctx.message.channel.fetch_message(row[1])
            if hangmanmsg:
                await ctx.message.channel.send(embed=discord.Embed(description='<:SeekPng:705124992349896795> ' + ctx.message.author.mention + ' Game successfully ended. The word was: **' + row[4] + '**'))
                await hangmanmsg.delete()
                cursor.execute(f'DELETE FROM Hangman WHERE user_id = {ctx.message.author.id}')
                db.commit()
            else:
                await ctx.message.channel.send(
                    embed=discord.Embed(description='<:x_:705214517961031751> **You must use $hangmanend in the same channel as where you started the game**'))
        else:
            await ctx.message.channel.send(embed=discord.Embed(description='<:x_:705214517961031751> **You do not have a game created**'))
        await ctx.message.delete()
        cursor.close()
        db.close()


def setup(client):
    client.add_cog(Hangman(client))