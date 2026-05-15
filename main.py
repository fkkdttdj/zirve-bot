import discord
import os
import random
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- 7/24 AKTİF TUTMA SİSTEMİ ---
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif ve Zirve'de!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

# --- ENVANTER SİSTEMİ (Basit Veritabanı) ---
envanterler = {}

# --- KÜFÜR FİLTRESİ VE SELAMLAŞMA ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.lower()

    # Küfür Filtresi
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} ne diyon lan hırrım burası KAJUNV36 he istediğine istediğin gibi orusbu diyemezsin burda!")
        return

    # Selamlaşma
    if msg == "naber":
        await message.channel.send(f"İyidir reis, senden naber? KAJUNV36 akıyor!")

    await bot.process_commands(message)

# --- OYUN KOMUTLARI ---

@bot.command()
async def kasaac(ctx):
    oduller = ["100 XP", "Bronz Kasa", "Gümüş Kasa", "Altın Kasa", "Elmas Anahtar"]
    kazanilan = random.choice(oduller)
    
    user_id = str(ctx.author.id)
    if user_id not in envanterler:
        envanterler[user_id] = []
    envanterler[user_id].append(kazanilan)
    
    await ctx.send(f"🎰 {ctx.author.mention}, kasadan şunu kazandın: **{kazanilan}**! (Envanterine eklendi)")

@bot.command()
async def zar(ctx):
    sonuc = random.randint(1, 6)
    await ctx.send(f"🎲 Zar atıldı: **{sonuc}** geldi!")

@bot.command()
async def yazitura(ctx):
    sonuc = random.choice(["Yazı", "Tura"])
    await ctx.send(f"🪙 Para havada dönüyor... **{sonuc}** geldi!")

@bot.command()
async def envanter(ctx):
    user_id = str(ctx.author.id)
    if user_id in envanterler and envanterler[user_id]:
        items = ", ".join(envanterler[user_id])
        await ctx.send(f"🎒 {ctx.author.mention} Envanterin: {items}")
    else:
        await ctx.send(f"🎒 {ctx.author.mention} Envanterin bomboş reis, biraz kasa aç!")

# --- BOTUN AÇILIŞI ---
@bot.event
async def on_ready():
    print(f'Reis, sistem 7/24 modunda hazır! Bot: {bot.user}')

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Hata: DISCORD_TOKEN bulunamadı!")
