import discord
import os
import random
import asyncio
import json
from discord.ext import commands
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

# --- 7/24 AKTİF TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "KAJUNV36 Zirve'de!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True, help_command=None)

# --- EKONOMİ VERİ TABANI ---
DATA_FILE = "ekonomi.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {"bakiyeler": {}, "last_daily": {}}
    return {"bakiyeler": {}, "last_daily": {}}

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

# --- YARDIM KOMUTU ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 TAM SÜRÜM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük`, `!gönder @üye [miktar]`")
    embed.add_field(name="🎰 Kumar", value="`!cf [miktar]`, `!slot [miktar]`, `!bj [miktar]` (21)")
    embed.add_field(name="📦 Kasa & Eğlence", value="`!kasaac` (250 Coin), `!zar`")
    embed.add_field(name="🛠️ Yönetim", value="`!ban`, `!unban`, `!sil [sayı]`")
    embed.set_footer(text="KAJUNV36 #PRIME")
    await ctx.send(embed=embed)

# --- BLACKJACK (21) OYUNU ---
@bot.command(aliases=['21', 'blackjack'])
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar:
        return await ctx.send("❌ Bu masaya oturmaya paran yetmiyor reis!")

    def kart_ver(): return random.randint(1, 11)
    oyuncu = [kart_ver(), kart_ver()]
    bot_el = [kart_ver(), kart_ver()]
    
    msg = await ctx.send(f"🃏 | {ctx.author.mention}, Masadasın!\n💰 **Bahis:** {miktar}\n🃏 **Sen:** {oyuncu} ({sum(oyuncu)})\n🎲 **Bot:** [{bot_el[0]}, ?]\n👉 Çekmek için **'h'**, durmak için **'s'** yaz.")

    while sum(oyuncu) < 21:
        try:
            r = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.content.lower() in ['h', 's'], timeout=30.0)
            if r.content.lower() == 'h':
                oyuncu.append(kart_ver())
                if sum(oyuncu) > 21: break
                await msg.edit(content=f"🃏 | Kart çekildi!\n🃏 **Sen:** {oyuncu} ({sum(oyuncu)})\n🎲 **Bot:** [{bot_el[0]}, ?]\n👉 **'h'** mi **'s'** mi?")
            else: break
        except: break

    o_top = sum(oyuncu)
    b_top = sum(bot_el)
    if o_top <= 21:
        while b_top < 17: b_top += kart_ver()

    if o_top > 21:
        update_balance(ctx.author.id, -miktar); res = "💀 **PATLADIN!** 21'i geçtin."
    elif b_top > 21 or o_top > b_top:
        update_balance(ctx.author.id, miktar); res = f"🎉 **KAZANDIN!** Bot {b_top} kaldı."
    elif o_top == b_top:
        res = "🤝 **BERABERE!** Para iade."
    else:
        update_balance(ctx.author.id, -miktar); res = f"💀 **KAYBETTİN!** Bot {b_top} ile geçti."

    await msg.edit(content=f"🃏 | **Sonuç**\nSen: {o_top} | Bot: {b_top}\n{res}")

# --- DİĞER KOMUTLAR ---
@bot.command(aliases=['cash', 'para'])
async def cuzdan(ctx): await ctx.send(f"💰 Bakiyen: **{get_balance(ctx.author.id)} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    update_balance(ctx.author.id, 500); await ctx.send("💵 Günlük 500 coin maaşın yattı!")

@bot.command()
async def cf(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    if random.choice([True, False]):
        update_balance(ctx.author.id, miktar); await ctx.send(f"🎉 +{miktar} kazandın!")
    else:
        update_balance(ctx.author.id, -miktar); await ctx.send(f"💀 -{miktar} kaybettin!")

@bot.command()
async def slot(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    e = ["🍒", "💎", "⭐"]; r = [random.choice(e) for _ in range(3)]
    if r[0] == r[1] == r[2]: update_balance(ctx.author.id, miktar*5); s = "JACKPOT! 🏆"
    else: update_balance(ctx.author.id, -miktar); s = "Kasa kazandı. 💀"
    await ctx.send(f"🎰 [ {r[0]} | {r[1]} | {r[2]} ]\n{s}")

@bot.command()
async def kasaac(ctx):
    if get_balance(ctx.author.id) < 250: return await ctx.send("❌ 250 Coin lazım!")
    update_balance(ctx.author.id, -250); o = random.randint(0, 1000)
    update_balance(ctx.author.id, o); await ctx.send(f"📦 Kasadan **{o} Coin** çıktı!")

@bot.command()
async def zar(ctx): await ctx.send(f"🎲 Zar: **{random.randint(1, 6)}**")

# --- MODERASYON & SELAM ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()
    
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} ne diyon lan hırrım burası KAJUNV36 he istediğine istediğin gibi orusbu diyemezsin burda!")
        return

    if msg == "naber":
        await message.channel.send("İyidir kral, sen nasılsın? Beni nasıl kullanacağını öğrenmek için !yardim yazabilirsin.")
        return

    await bot.process_commands(message)

@bot.event
async def on_ready(): print(f'KAJUNV36 FULL SİSTEM HAZIR!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
