import discord
from discord.ext import commands
import csv
import json
import main
from message import *

bot_token_file = 'key.txt'
latin_dict_file = './db/dict_latin.txt'
authors_dict_file = './db/authors.json'
command_dict_file = './db/commands.json'
special_event_file = './db/special_events.json'
special_counter_file = './db/special_counter.json'

""" Init bot """

with open(bot_token_file) as keyfile:
    bot_token = keyfile.read()
description = '''Bot koji broji ko koliko psuje i jos po nesto.'''
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='', description=description, intents=intents)

""" Init files and structures """

forbidden_words = {'Psovkobrojac BOT', 'Psovkobrojac BOT#9107' ,'?Ko je najveci majmun', '?Коя е най-голямата маймуна?'}
curses = dict()
allowed_words = {}
authors = {}
command_dict = {
    "/komande" : "Izlistava sve komande",
    "/psovke" : "Izlistava sve psovke u trenutnom recniku",
    "/obrisi" : "Brise psovku iz trenutnog recnika",
    "/registruj" : "Dodaje rec u trenutni recnik",
    "/Ko je najveci majmun" : "Izlistava najvece majmune",
    "/jebaci" : "Ko je najvise puta rekao onaj sto sam te jebo"
}
special_events = {}
special_counter = {}
update_special_counter = 0

with open(latin_dict_file, newline='') as csvfile:
    allowed_words = [row for row in csv.reader(csvfile, delimiter=',')][0]
with open(authors_dict_file) as f:
    authors = json.load(f)
with open(special_event_file, encoding='UTF-8') as f:
    special_events = json.load(f)
with open(special_counter_file, encoding='UTF-8') as f:
    special_counter = json.load(f)

def register_curse_words(word: str, author: str):
    if author in forbidden_words: return
    if word in forbidden_words: return
    word = word.lower()
    is_cursing = False

    for wrd in word.split(' '):
        if wrd in allowed_words:
            is_cursing = True
            break
    if not is_cursing: return

    for wrd in word.split(' '):
        if wrd not in allowed_words: continue
        if authors.get(author) is None:
            authors[author] = dict()
        if authors[author] is None:
            authors[author] = dict()
        if authors[author].get(wrd) is None:
            authors[author][wrd] = 1
        else:
            authors[author][wrd] += 1
    
    update_authors()

def prepare_output() -> str:
    out = '```'
    for key in authors.keys():
        author = authors[key]
        out += 'Autor: ' + key + '\n'
        for curse in author:
            out += '  ' + curse  + ' : '
            out += str(author[curse])
            out += '\n'
        out += '\n'
    out += '```'
    return out

def add_curse_words(words) -> None:
    for word in words:
        if word in allowed_words: continue
        allowed_words.append(word)

    with open(latin_dict_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(allowed_words)

def remove_curse_words(words):
    for word in words:
        if word in allowed_words:
            allowed_words.remove(word)

def update_authors() -> None:
    with open(authors_dict_file, 'w') as f:
        f.write(str(authors).replace('\'', '\"'))

commands = {
    '/registruj'                    : '/registruj',
    '/obrisi'                       : '/obrisi',
    '/psovke'                       : '/psovke',
    '/Ko je najveci majmun'         : '/izlistaj',
    '/Коя е най-голямата маймуна?'  : '/izlistaj',          
}

def count_special_events(author: str):
    if special_counter.get(author) is None:
        special_counter[author] = 0
    special_counter[author] += 1
    global update_special_counter
    update_special_counter += 1

    if update_special_counter == 10:
        with open(special_counter_file, 'w') as f:
            f.write(str(special_counter).replace('\'', '\"'))
        update_special_counter = 0

async def handle_special(message: discord.message):
    if message.content in special_events.keys():
        count_special_events(str(message.author))
    spec_pair = special_events[message.content.lower()]
    out = discord.Embed(title="", description="")
    out.add_field(name='', value=spec_pair["vid"])
    out.set_image(url=spec_pair["img"])
    await message.channel.send(embed=out)

@bot.event
async def on_message(message: discord.message):   
    if str(message.content).startswith('/'):
        await bot.process_commands(message)
    else:
        if message.content.lower() in special_events.keys():
            await handle_special(message)
        register_curse_words(str(message.content), str(message.author)) 

@bot.command(name='/jebaci')
async def special_count(ctx):
    out = discord.Embed(title="Ko je najvise onaj sto sam te jebao", description="")
    value = ''
    for item in special_counter.items():
        value += '**' + item[0] + '** : ' + str(item[1]) + '\n'
    out.add_field(name='', value=value)
    await ctx.send(embed=out)
  
@bot.command(name='/komande')
async def help(ctx):
    out = discord.Embed(title="Komande", description="")
    value = ''
    for item in command_dict.items():
        value += '**' + item[0] + '** : ' + item[1] + '\n'
    out.add_field(name='', value=value)
    await ctx.send(embed=out)

@bot.command(name='/Ko')
async def analysis(ctx, *args):
    if args == ('je', 'najveci', 'majmun'):
        await ctx.send(prepare_output())
  
@bot.command(name='/registruj')
async def added_word(ctx, *args):
    add_curse_words(args)
    await ctx.send(REGISTROVANO)

@bot.command(name='/obrisi')
async def removed_words(ctx, *args):
    remove_curse_words(args)
    await ctx.send(OBRISANO)

@bot.command(name='/psovke')
async def list_words(ctx):
    out = discord.Embed(title="Sve sto mozes da kazes bratu", description="")
    value = ''
    for i, word in enumerate(allowed_words):
        value += '**' + str(i + 1) + '**. ' + word + ' '
    out.add_field(name='', value=value)
    await ctx.send(embed=out)

def main():
    bot.run(bot_token)

if __name__ == "__main__":
    main()
