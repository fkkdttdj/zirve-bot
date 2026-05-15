import discord
import os
import random
import asyncio
import json
import google.generativeai as genai
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- SUNUCU AKTİF TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "KAJUNV36 AKTIF"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- YAPAY ZEKA ---
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# --- BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# --- EKONOMİ ---
DATA_FILE = "ekonomi.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {"bakiyeler": {}}
    return {"bakiyeler": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def update_bal(uid, amount):
    data = load_data()
    u_id = str(uid)
    data["bakiyeler"][u_id] = data["bakiyeler"].get(u_id, 1000) + amount
    save_data(data)

# --- OLAYLAR ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # 🧠 YAPAY ZEKA
    if message.content.startswith('>'):
        soru = message.content[1:].strip()
        if not soru: return
        async with message.channel.typing():
            try:
                response = ai_model.generate_content(f"Sen KAJUNV36 sunucusunun asistanısın. Kısa ve reis diye hitap ederek cevap ver: {soru}")
                await message.reply(response.text)
            except Exception as e:
                await message.reply("Reis anahtarı Render'da 'GEMINI_KEY' ismiyle kaydettiğinden emin ol!")
        return

    # 🤬 FİLTRE
    if "orusbu" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} düzgün konuş hırrım!")
        return

    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 TAM SÜRÜM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük`", inline=True)
    embed.add_field(name="🎰 Kumar", value="`!cf [miktar]`, `!slot [miktar]`, `!bj [miktar]`", inline=True)
    embed.add_field(name="📦 Diğer", value="`!kasaac`, `!zar`, `!sil [sayı]`", inline=True)
    embed.set_footer(text="Yapay zeka için mesajın başına > koy!")
    await ctx.send(embed=embed)

@bot.command()
async def cuzdan(ctx):
    data = load_data()
    bal = data["bakiyeler"].get(str(ctx.author.id), 1000)
    await ctx.send(f"💰 Bakiyen: **{bal} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    update_bal(ctx.author.id, 500); await ctx.send("💵 500 coin yattı reis!")

@bot.command()
async def bj(ctx, miktar: int):
    if miktar <= 0 or load_data()["bakiyeler"].get(str(ctx.author.id), 1000) < miktar:
        return await ctx.send("Para yok reis!")
    if random.choice([True, False]):
        update_bal(ctx.author.id, miktar); await ctx.send(f"🃏 Kazandın! +{miktar}")
    else:
        update_bal(ctx.author.id, -miktar); await ctx.send(f"💀 Kaybettin! -{miktar}")

@bot.command()
async def sil(ctx, sayi: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=sayi + 1)
    else: await ctx.send("Yetkin yok reis!")

@bot.event
async def on_ready(): print(f'BOT HAZIR!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
