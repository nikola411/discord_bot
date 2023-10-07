import discord
from discord.ext import commands
from discord.ext import tasks
import requests
import os
import logging

from Commands.Authors.authors import Authors
from Commands.CurseWords.curses import Curses
from Commands.Custom.custom import Custom, TYPE, AUTHOR, LINK, TITLE, PHRASE, REMOVE, LIST
from Commands.Scheduled.scheduled import Schedule

from datetime import datetime
from Commands.Scheduled.scheduled import ACTIONS, TIMESTAMP, CONTENT, TYPE, CHANNEL_ID

BOT_TOKEN_FILE = './key'
ADMINS = ['nikola411', '.mokosha', 'chewdlaka']

with open(BOT_TOKEN_FILE) as keyfile:
    bot_token = keyfile.read()
description = '''Bot koji broji ko koliko psuje i jos po nesto.'''
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='', description=description, intents=intents)

logger = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

curses = Curses()
authors = Authors()
custom = Custom()
schedule = Schedule()

command_set = {
    '**/Ko je najveci majmun**' : 'Izlistaj sve ljude koji su psovali na serveru.',
    '**/psovke**' : 'Izlistaj sve psovke iz recnika psovki na osnovu koga se broji psovanje.',
    '**/registruj**' : 'Dodaj psovku u recnik.',
    '**/obrisi**' : 'Obrisi psovku iz recnika psovki kitakitakita.',
    '**/komande**' : 'Pokazuje sve dostupne komande.',
    '**/zakazi**' : 'Zakazi slanje poruke ili slike.\n \
        * /zakazi tip=[img|msg] sadrzaj=[link ili sadrzaj poruke] vreme=[DD.MM.YYYY HH:MM:SS]',
    '**/meme**' : 'Nalazi random meme.'
} 

MEME_API_ENDPOINT = 'https://meme-api.com/gimme'

def MakeEmbed(packet: dict) -> discord.Embed:
    title = ''
    if packet.get(TITLE):
        title = packet[TITLE]
    print(packet)
    out = discord.Embed(title=title, description="")
    if packet[TYPE] == 'img':
        out.set_image(url=packet[LINK])

    return out

channelFrom = None

@bot.event
async def on_message(message: discord.message):
    global channelFrom
    channelFrom = message.channel.id

    content = str(message.content).split(' ')
    author = str(message.author)

    if content[0].startswith('/'):
        await bot.process_commands(message)
    else:
        customEvents = None
        customEvents = custom.CheckForCustomEventSingle(author, content)
        if customEvents is None:
            customEvents = custom.CheckForCustomEventRegex(author, content)
        if customEvents is None:
            customEvents = custom.CheckForCustomEventAll(content)

        if customEvents is not None:
            for event in customEvents:
                response = MakeEmbed(event)
                await message.channel.send(embed=response)

        authors.RegisterAuthorCursing(author, curses.CheckIfCursing(content))

@bot.command(name='/komande')
async def help(ctx):
    out = discord.Embed(title='Komande', description="")
    for key, value in command_set.items():
        out.add_field(name=key, value=value, inline=False)
    await ctx.send(embed=out)

@bot.command(name='/Ko')
async def list_all(ctx, *args):
    if args == ('je', 'najveci', 'majmun'):
        await ctx.send(authors.FormatOutputString())

@bot.command(name='/obrisi')
async def delete_curse_word(ctx, *args):
    deleted = curses.RemoveCurseWords(args)
    if deleted is True:
        authors.DeleteFromHistory(args)
    await ctx.send("Obrisano! :white_check_mark:" if deleted else "Neuspesno brisanje! Rec nije u recniku!")

@bot.command(name='/registruj')
async def register_curse_word(ctx, *args):
    curses.AddAllowedWords(args)
    await ctx.send("Uspesno registrovano!  :white_check_mark:")

@bot.command(name='/psovke')
async def register_curse_word(ctx):
    curse_list = curses.PrepareOutput()
    await ctx.send(curse_list)

@bot.command(name='/custom')
async def register_custom(ctx, *args):
    if str(ctx.author) in ADMINS:
        out = ''
        if args[0] == LIST:
            out = custom.PrintCustomCommands(args[1])
        elif args[0]:
            ret = custom.ProcessCommand(args)
            action = 'obrisan' if args[0] == REMOVE else 'dodat'
        
            if ret:
                out = 'Uspesno ' + action + ' custom dogadjaj! :white_check_mark:'
            else:
                out = 'Neuspesan pokusaj!'

        await ctx.send(out)

@bot.command(name='/meme')
async def get_meme(ctx):
    response = requests.get(MEME_API_ENDPOINT).json()

    out = discord.Embed(title=response["title"], description="")
    out.set_image(url=response["url"])

    await ctx.send(embed=out)

@bot.command(name='/zakazi')
async def schedule_event(ctx, *args):
    ret = schedule.AddScheduledEvent(args, int(channelFrom))
    out = ''
    if ret:
        out = 'Uspesno zakazana akcija dogadjaj! :white_check_mark:'
    else:
        out = 'Neuspesan pokusaj!'
    await ctx.send(out)

# never touch this code, bot will die if this is not executed correctly
shouldUpdate = False

@bot.command(name='/azuriraj')
async def update_bot_code(ctx, *args):
    global shouldUpdate
    shouldUpdate = True

    await bot.close()
#end of critical code

lastDbUpdate = None

@tasks.loop(seconds=1)
async def task_loop():
    global lastDbUpdate
    if lastDbUpdate is None:
        lastDbUpdate = datetime.now()
    
    if (datetime.now() - lastDbUpdate).total_seconds() > 30 * 60:
        lastDbUpdate = datetime.now()
        curses.UpdateDB()
        authors.UpdateDB()
        custom.UpdateDB()
        print('Updating..')
    
    scheduled = schedule.GetExpired()
    for event in scheduled:
        title = '' if event[TYPE] == 'img' else event[CONTENT]
        out = discord.Embed(title=title, description='')
        if event[TYPE] == 'img':
            out.set_image(url=event[CONTENT])
        channel = bot.get_channel(event[CHANNEL_ID])
        await channel.send(embed=out)
   
@bot.event
async def on_ready():
    task_loop.start()

def main():
    bot.run(token=bot_token)

    # never touch this code, bot will die if this is not executed correctly
    if shouldUpdate:
        os.system('git pull')
        os.system('nohup python3 main.py &')
    #end of critical code
    
if __name__ == "__main__":
    main()