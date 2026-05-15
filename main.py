import discord
import os
import random
import asyncio
import json
import google.generativeai as genai
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- 7/24 AKTİF TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "KAJUNV36 AI AKTİF!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- YAPAY ZEKA AYARI ---
genai.configure(api_key=os.environ.get("GEMINI_KEY"))
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# --- EKONOMİ SİSTEMİ ---
DATA_FILE = "ekonomi.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {"bakiyeler": {}}
    return {"bakiyeler": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def get_bal(uid):
    data = load_data()
    return data["bakiyeler"].get(str(uid), 1000)

def update_bal(uid, amount):
    data = load_data()
    u_id = str(uid)
    data["bakiyeler"][u_id] = data["bakiyeler"].get(u_id, 1000) + amount
    save_data(data)

# --- ANA OLAYLAR ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # 🧠 YAPAY ZEKA (> ile başlarsa)
    if message.content.startswith('>'):
        soru = message.content[1:].strip()
        if not soru: return await message.reply("Efendim reis?")
        async with message.channel.typing():
            try:
                chat = ai_model.start_chat(history=[])
                response = chat.send_message(f"Sen KAJUNV36 sunucusunun asistanısın. Kısa, delikanlı ve reis diye hitap ederek cevap ver: {soru}")
                await message.reply(response.text)
            except:
                await message.reply("Reis kafam biraz karıştı, API anahtarını kontrol et!")
        return

    # 🤬 KÜFÜR FİLTRESİ
    if "orusbu" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} ne diyon lan hırrım burası KAJUNV36 he istediğine istediğin gibi orusbu diyemezsin burda!")
        return

    # 👋 SELAMLAŞMA
    if message.content.lower() == "naber":
        await message.channel.send("İyidir kral, kumarhanemiz açık! Yapay zekayla sohbet için başına > koyup yazabilirsin.")
        return

    await bot.process_commands(message)

# --- KUMAR VE EKONOMİ KOMUTLARI ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 ZİRVE SİSTEM", color=discord.Color.blue())
    embed.add_field(name="🤖 Yapay Zeka", value="`> [sorun]` : Reis cevaplar.", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük`", inline=True)
    embed.add_field(name="🎰 Kumar", value="`!cf [miktar]`, `!bj [miktar]`", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def cuzdan(ctx):
    await ctx.send(f"💰 Bakiyen: **{get_bal(ctx.author.id)} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    update_bal(ctx.author.id, 500); await ctx.send("💵 500 Coin yattı reis!")

@bot.command()
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_bal(ctx.author.id) < miktar: return await ctx.send("Para yok reis!")
    await ctx.send(f"🃏 {ctx.author.mention} masaya oturdu. (Yakında daha detaylı olacak)")
    # Basit kazanma/kaybetme
    if random.choice([True, False]):
        update_bal(ctx.author.id, miktar); await ctx.send("🎉 Kazandın!")
    else:
        update_bal(ctx.author.id, -miktar); await ctx.send("💀 Kaybettin.")

@bot.event
async def on_ready(): print(f'KAJUNV36 AI ZİRVEDE!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))

