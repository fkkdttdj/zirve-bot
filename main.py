import discord
import os
from discord.ext import commands
import random
from flask import Flask
from threading import Thread

--- 7/24 AKTİF TUTMA SİSTEMİ (WEB SERVER) ---
app = Flask('')

@app.route('/')
def home():
return "Bot aktif ve Zirve'de!"

def run():
app.run(host='0.0.0.0', port=8080)

def keep_alive():
t = Thread(target=run)
t.start()

--- BOT SİSTEMİ ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
print(f'Reis, sistem 7/24 modunda hazır! Bot: {bot.user}')

# En alttaki çalıştırma kısmı böyle olacak:
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
