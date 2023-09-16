import discord
from discord.ext import commands
from discord.ext import tasks
import re

from Commands.Authors.authors import Authors
from Commands.CurseWords.curses import Curses
from Commands.Custom.custom import Custom, TYPE, AUTHOR, LINK, TITLE, PHRASE, REMOVE

BOT_TOKEN_FILE = './key'

with open(BOT_TOKEN_FILE) as keyfile:
    bot_token = keyfile.read()
description = '''Bot koji broji ko koliko psuje i jos po nesto.'''
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='', description=description, intents=intents)

curses = Curses()
authors = Authors()
custom = Custom()

command_set = {
    '/Ko je najveci majmun' : 'Izlistaj sve ljude koji su psovali na serveru.',
    '/psovke' : 'Izlistaj sve psovke iz recnika psovki na osnovu koga se broji psovanje.',
    '/registruj' : 'Dodaj psovku u recnik psovki.',
    '/obrisi' : 'Obrisi psovku iz recnika.',
    '/komande' : 'Pokazuje sve dostupne komande.',
    '/custom' : 'Dodaj custom dogadjaj. Custom dogadjaji su odgovori koje ce BOT da posalje kada neko napise nesto.\n\
    * primer: /custom dodaj fraza=[vucic] tip=[img] link=[http://jebac.com]\n\
        svaki put kad neko napise vucic, bot ce odgovoriti sa slikom koja je zakacena u linku.\n\n\
    * /custom dodaj **fraza**=[fraza na koju bot reaguje] **tip**=[img|msg] **link**=[link do slike] **naslov**=[bilo koji naslov]\n\n\
    * /custom obrisi **fraza**=[fraza na koju bot vise nece da reaguje]'
} 

def MakeEmbed(packet: dict) -> discord.Embed:
    title = ''
    if packet.get(TITLE):
        title = packet[TITLE]
    print(packet)
    out = discord.Embed(title=title, description="")
    if packet[TYPE] == 'img':
        out.set_image(url=packet[LINK])

    return out

@bot.event
async def on_message(message: discord.message):
    content = str(message.content).split(' ')
    author = str(message.author)

    if content[0].startswith('/'):
        await bot.process_commands(message)
    else:
        isCustomSingle = custom.CheckForCustomEventSingle(author, content)
        if isCustomSingle is not None:
            for event in isCustomSingle:
                response = MakeEmbed(event)
                await message.channel.send(embed=response)
        else:
            isCustomGeneral = custom.CheckForCustomEventAll(content)
            if isCustomGeneral is not None:
                for event in isCustomGeneral:
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
    curses.RemoveCurseWords(*args)
    authors.DeleteFromHistory(*args)
    await ctx.send("Obrisano! :white_check_mark:")

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
    ret = custom.ProcessCommand(args)
    action = 'obrisan' if args[0] == REMOVE else 'dodat'
    out = ''
    if ret:
        out = 'Uspesno ' + action + ' custom dogadjaj! :white_check_mark:'
    else:
        out = 'Neuspesan pokusaj!'
    await ctx.send(out)

@tasks.loop(minutes=30)
async def task_loop():
    curses.UpdateDB()
    authors.UpdateDB()
    custom.UpdateDB()
    print('Updating..')

@bot.event
async def on_ready():
    task_loop.start()

def main():
    bot.run(bot_token)


if __name__ == "__main__":
    main()