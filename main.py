import discord
import os
import random
import asyncio
import json
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- SUNUCU AKTİF TUTMA (UptimeRobot İçin) ---
app = Flask('')
@app.route('/')
def home(): return "KAJUNV36 ZIRVE SISTEM AKTIF"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

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

# --- ANA OLAYLAR (Selamlaşma & Filtre) ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    msg = message.content.lower()

    # 👋 SELAMLAŞMA KOMUTLARI
    if msg == "selam" or msg == "slm" or msg == "sa":
        await message.channel.send(f"Aleyküm Selam {message.author.mention} hoş geldin reis! Mekanın sahibi KAJUNV36 burada.")
        return

    if msg == "naber":
        await message.channel.send("İyidir kral, sen nasılsın? Kumarhanemiz açık, !yardım yazarak ortamı şenlendirebilirsin.")
        return

    # 🤬 KÜFÜR FİLTRESİ
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} düzgün konuş hırrım, burası KAJUNV36!")
        return

    await bot.process_commands(message)

# --- KOMUTLAR (Yardım, Ekonomi, Kumar) ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 TAM SÜRÜM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük`, `!gönder @üye [miktar]`", inline=False)
    embed.add_field(name="🎰 Kumar", value="`!cf [miktar]`, `!slot [miktar]`, `!bj [miktar]`", inline=False)
    embed.add_field(name="📦 Kasa & Eğlence", value="`!kasaac` (500 Coin), `!zar` ve 'selam/sa/naber'", inline=False)
    embed.add_field(name="🛠️ Yönetim", value="`!ban @üye`, `!unban ID`, `!sil [sayı]`", inline=False)
    embed.set_footer(text="KAJUNV36 #ZİRVE")
    await ctx.send(embed=embed)

@bot.command(aliases=['para', 'cash'])
async def cuzdan(ctx):
    await ctx.send(f"💰 Bakiyen: **{get_balance(ctx.author.id)} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 Günlük 500 coin maaşın yattı reis!")

@bot.command()
async def gönder(ctx, member: discord.Member, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    update_balance(ctx.author.id, -miktar)
    update_balance(member.id, miktar)
    await ctx.send(f"✅ {ctx.author.mention}, {member.mention} kullanıcısına **{miktar}** coin ateşledi!")

@bot.command()
async def kasaac(ctx):
    if get_balance(ctx.author.id) < 500: return await ctx.send("❌ Kasa açmak için 250 coin lazım!")
    update_balance(ctx.author.id, -500)
    odul = random.choice([50, 100, 300, 500, 1500, 100000000, 50000, 20000, 100000])
    update_balance(ctx.author.id, odul)
    await ctx.send(f"📦 Kasadan **{odul}** Kajun Coin çıktı!")

@bot.command()
async def cf(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    if random.choice([True, False]):
        update_balance(ctx.author.id, miktar); await ctx.send(f"🪙 Yazı-Tura kazandın! +{miktar}")
    else:
        update_balance(ctx.author.id, -miktar); await ctx.send(f"💀 Kaybettin reis... -{miktar}")

@bot.command()
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yok!")
    if random.randint(1, 100) > 50:
        update_balance(ctx.author.id, miktar); await ctx.send(f"🃏 Blackjack kazandın! +{miktar}")
    else:
        update_balance(ctx.author.id, -miktar); await ctx.send(f"🃏 Kasa kazandı, **{miktar}** uçtu.")

@bot.command()
async def zar(ctx):
    await ctx.send(f"🎲 Zar: **{random.randint(1, 6)}**")

# --- YÖNETİM KOMUTLARI ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    await ctx.channel.purge(limit=sayi + 1)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep=None):
    await member.ban(reason=sebep)
    await ctx.send(f"❌ {member.name} sunucudan banlandı!")

@bot.event
async def on_ready():
    print(f'KAJUNV36 FULL SİSTEM BAŞLATILDI!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))

