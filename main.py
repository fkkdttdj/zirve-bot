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
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"bakiyeler": {}, "last_daily": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def get_balance(user_id):
    data = load_data()
    return data["bakiyeler"].get(str(user_id), 1000)

def update_balance(user_id, amount):
    data = load_data()
    user_id = str(user_id)
    data["bakiyeler"][user_id] = data["bakiyeler"].get(user_id, 1000) + amount
    save_data(data)

# --- YARDIM KOMUTU ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 FULL SİSTEM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cuzdan`, `!gunluk`, `!gönder @üye [miktar]`", inline=False)
    embed.add_field(name="🎰 Kumar & Kasa", value="`!cf [miktar]`, `!slot [miktar]`, `!kasaac` (250 Coin)", inline=False)
    embed.add_field(name="🛠️ Yönetim", value="`!ban`, `!unban`, `!sil` (Zar: `!zar`)", inline=False)
    embed.set_footer(text="KAJUNV36 #ZİRVE")
    await ctx.send(embed=embed)

# --- EKONOMİ & KUMAR ---
@bot.command(aliases=['cash', 'money', 'para'])
async def cuzdan(ctx):
    bal = get_balance(ctx.author.id)
    await ctx.send(f"💰 {ctx.author.mention}, bakiyen: **{bal} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    now = datetime.now()
    last_daily = data["last_daily"].get(user_id)
    if last_daily:
        last_time = datetime.strptime(last_daily, "%Y-%m-%d %H:%M:%S")
        if now < last_time + timedelta(days=1):
            kalan = (last_time + timedelta(days=1)) - now
            return await ctx.send(f"⏳ Dinlen biraz reis! {kalan.seconds // 3600} saat sonra gel.")
    update_balance(user_id, 500)
    data["last_daily"][user_id] = now.strftime("%Y-%m-%d %H:%M:%S")
    save_data(data)
    await ctx.send(f"💵 **500 Kajun Coin** maaşın yattı!")

@bot.command()
async def cf(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yok reis!")
    await ctx.send("🪙 Yazı-tura atılıyor... 🔄")
    await asyncio.sleep(1.5)
    if random.choice([True, False]):
        update_balance(ctx.author.id, miktar)
        await ctx.send(f"🎉 Kazandın! +{miktar} coin.")
    else:
        update_balance(ctx.author.id, -miktar)
        await ctx.send(f"💀 Gitti paralar... -{miktar} coin.")

# --- KASA SİSTEMİ (GERİ GELDİ) ---
@bot.command()
async def kasaac(ctx):
    maliyet = 250
    if get_balance(ctx.author.id) < maliyet:
        return await ctx.send(f"❌ Kasa açmak için **{maliyet} coin** lazım reis!")
    
    update_balance(ctx.author.id, -maliyet)
    mesaj = await ctx.send("📦 Kasa açılıyor... 🔑")
    await asyncio.sleep(2)
    
    oduller = [
        ("Bronz Ödül", 100), ("Gümüş Ödül", 300), 
        ("Altın Ödül", 750), ("ELMAS ÖDÜL", 2500), ("Boş Çıktı", 0)
    ]
    isim, miktar = random.choices(oduller, weights=[40, 30, 20, 5, 5])[0]
    
    if miktar > 0:
        update_balance(ctx.author.id, miktar)
        await mesaj.edit(content=f"🎉 {ctx.author.mention}, kasadan **{isim}** çıktı ve **{miktar} Kajun Coin** kazandın!")
    else:
        await mesaj.edit(content=f"💀 {ctx.author.mention}, kasanın içi boş çıktı... Şansına küs!")

# --- EĞLENCE & MODERASYON ---
@bot.command()
async def zar(ctx):
    await ctx.send(f"🎲 Zar durdu: **{random.randint(1, 6)}**")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Belirtilmedi"):
    await member.ban(reason=reason); await ctx.send(f"🚫 **{member.name}** banlandı!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()
    if "orusbu" in msg:
        await message.delete(); await message.channel.send("Racon kesme, mesajın silindi!")
        return
    if msg == "naber":
        await message.channel.send("İyidir kral, kumarhanemiz açıldı !yardim yaz gör")
        return
    await bot.process_commands(message)

@bot.event
async def on_ready(): print(f'KAJUNV36 FULL SİSTEM HAZIR!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
