import discord
import os
import random
import asyncio
import json
import google.generativeai as genai
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- 7/24 AKTİF TUTMA (UptimeRobot için) ---
app = Flask('')
@app.route('/')
def home(): return "KAJUNV36 ZIRVE SİSTEM AKTİF!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- YAPAY ZEKA AYARI ---
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# --- EKONOMİ VERİ TABANI ---
DATA_FILE = "ekonomi.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {"bakiyeler": {}}
    return {"bakiyeler": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def get_balance(user_id):
    data = load_data()
    return data["bakiyeler"].get(str(user_id), 1000)

def update_balance(user_id, amount):
    data = load_data()
    u_id = str(user_id)
    data["bakiyeler"][u_id] = data["bakiyeler"].get(u_id, 1000) + amount
    save_data(data)

# --- ANA OLAYLAR (Yapay Zeka & Filtre) ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # 🧠 YAPAY ZEKA MODU (> ile başlarsa)
    if message.content.startswith('>'):
        soru = message.content[1:].strip()
        if not soru: return
        async with message.channel.typing():
            try:
                response = ai_model.generate_content(f"Sen KAJUNV36 sunucusunun asistanısın. Kısa, delikanlı ve reis diye hitap ederek cevap ver: {soru}")
                await message.reply(response.text)
            except Exception as e:
                print(f"AI Hatası: {e}")
                await message.reply("Reis anahtarda bir sıkıntı var gibi, Render ayarlarını kontrol et!")
        return

    # 🤬 KÜFÜR FİLTRESİ
    if "orusbu" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} ne diyon lan hırrım burası KAJUNV36 he istediğine istediğin gibi orusbu diyemezsin burda!")
        return

    # 👋 SELAMLAŞMA
    if message.content.lower() == "naber":
        await message.channel.send("İyidir kral, sen nasılsın? Komutlar için !yardım, yapay zeka için mesajın başına > koyabilirsin.")
        return

    await bot.process_commands(message)

# --- EKONOMİ & KUMAR KOMUTLARI ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 FULL SİSTEM", color=discord.Color.gold())
    embed.add_field(name="🤖 Yapay Zeka", value="`> [sorun]` : Akıllı cevaplar.", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük`", inline=True)
    embed.add_field(name="🎰 Kumar", value="`!cf [miktar]`, `!bj [miktar]`, `!slot [miktar]`", inline=True)
    embed.set_footer(text="KAJUNV36 #PRIME")
    await ctx.send(embed=embed)

@bot.command(aliases=['cash', 'para'])
async def cuzdan(ctx):
    await ctx.send(f"💰 Bakiyen: **{get_balance(ctx.author.id)} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 Günlük 500 coin maaşın yattı reis!")

@bot.command()
async def cf(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    if random.choice([True, False]):
        update_balance(ctx.author.id, miktar); await ctx.send(f"🎉 Yazı-Tura kazandın! +{miktar}")
    else:
        update_balance(ctx.author.id, -miktar); await ctx.send(f"💀 Kaybettin! -{miktar}")

@bot.command(aliases=['21', 'blackjack'])
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yok!")
    # Basit hızlı Blackjack sonucu
    sonuc = random.randint(1, 100)
    if sonuc > 55:
        update_balance(ctx.author.id, miktar); await ctx.send(f"🃏 21 yaptın! **{miktar}** kazandın!")
    elif sonuc < 10:
        await ctx.send("🤝 Berabere, para iade.")
    else:
        update_balance(ctx.author.id, -miktar); await ctx.send(f"💀 Kasa kazandı, **{miktar}** uçtu.")

@bot.command()
async def zar(ctx):
    await ctx.send(f"🎲 Zar: **{random.randint(1, 6)}**")

@bot.event
async def on_ready():
    print(f'KAJUNV36 SİSTEMİ ÇALIŞIYOR!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
