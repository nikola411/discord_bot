import requests
import pandas as pd

import discord
from discord.ext import commands
import random
import csv
import json
import main

with open('key.txt') as keyfile:
    bot_token = keyfile.read()

description = '''Bot koji broji ko koliko psuje. 
Iskoristi komandu: '?Ko je najveci majmun' da dobijes spisak psovaca.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='', description=description, intents=intents)

curses = dict()
allowed_words = {}
authors = {}

forbidden_words = {'Psovkobrojac BOT', 'Psovkobrojac BOT#9107' ,'?Ko je najveci majmun', '?Коя е най-голямата маймуна?'}

with open('dict_latin.txt', newline='') as csvfile:
    allowed_words = [row for row in csv.reader(csvfile, delimiter=',')][0]
with open('authors.json') as f:
    authors = json.load(f)

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

    with open('dict_latin.txt', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(allowed_words)

def remove_curse_words(words):
    for word in words:
        allowed_words.remove(word)

def update_authors() -> None:
    with open('authors.json', 'w') as f:
        f.write(str(authors).replace('\'', '\"'))


@bot.event
async def on_message(message: discord.message):
    arr = message.content.split(' ')
    if message.content == "?Ko je najveci majmun" or message.content == '?Коя е най-голямата маймуна?':
        message.content = 'analysis'
        await bot.process_commands(message)
    elif '/registruj' in arr:
        message.content = 'added_word'
        add_curse_words(arr[1:])
        print(allowed_words)
        await bot.process_commands(message)
    elif '/obrisi' in arr:
        remove_curse_words(arr[1:])
        message.content = 'removed_words'
        await bot.process_commands(message)
    elif message.content == '/psovke':
        message.content = 'list_words'
        await bot.process_commands(message)
    else:
        register_curse_words(str(message.content), str(message.author))      

@bot.command()
async def analysis(ctx):
    await ctx.send(prepare_output())
  
@bot.command()
async def added_word(ctx):
    await ctx.send('Registrovano!')

@bot.command()
async def removed_words(ctx):
    await ctx.send('Obrisano!')

@bot.command()
async def list_words(ctx):
    await ctx.send(str(allowed_words))

def main():
    bot.run(bot_token)

if __name__ == "__main__":
    main()
