import discord
import os
import random
import asyncio
import json
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- SUNUCU AKTİF TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "KAJUNV36 EKONOMİ AKTİF"
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

# --- OLAYLAR ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # 🤬 KÜFÜR FİLTRESİ
    if "orusbu" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} düzgün konuş hırrım, burası KAJUNV36!")
        return

    # 👋 SELAMLAŞMA
    if message.content.lower() == "naber":
        await message.channel.send("İyidir kral, sen nasılsın? Kumarhanemiz açık, !yardım yazarak komutlara bakabilirsin.")
        return

    await bot.process_commands(message)

# --- EKONOMİ & KUMAR KOMUTLARI ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 EKONOMİ SİSTEMİ", color=discord.Color.blue())
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük` ya da `!para`", inline=False)
    embed.add_field(name="🎰 Kumar", value="`!cf [miktar]`, `!bj [miktar]`, `!slot [miktar]`", inline=False)
    embed.add_field(name="🛠️ Yönetim", value="`!sil [sayı]`, `!ban @üye`", inline=False)
    embed.set_footer(text="KAJUNV36 #ZİRVE")
    await ctx.send(embed=embed)

@bot.command(aliases=['para', 'cash'])
async def cuzdan(ctx):
    bal = get_balance(ctx.author.id)
    await ctx.send(f"💰 Bakiyen: **{bal} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 Günlük 500 coin maaşın yattı reis!")

@bot.command()
async def cf(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    if random.choice([True, False]):
        update_balance(ctx.author.id, miktar); await ctx.send(f"🪙 Yazı-Tura kazandın! +{miktar}")
    else:
        update_balance(ctx.author.id, -miktar); await ctx.send(f"🪙 Kaybettin reis... -{miktar}")

@bot.command()
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Bakiyen yetmiyor!")
    sonuc = random.randint(1, 100)
    if sonuc > 50:
        update_balance(ctx.author.id, miktar); await ctx.send(f"🃏 Blackjack! **{miktar}** kazandın!")
    else:
        update_balance(ctx.author.id, -miktar); await ctx.send(f"🃏 Kasa kazandı, **{miktar}** gitti.")

@bot.command()
async def sil(ctx, sayi: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=sayi + 1)
    else:
        await ctx.send("❌ Mesajları silme yetkin yok reis!")

@bot.event
async def on_ready():
    print(f'KAJUNV36 ESKİ TOPRAK AKTİF!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
