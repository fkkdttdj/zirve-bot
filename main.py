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

# --- ANA OLAYLAR ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()
    if msg in ["selam", "slm", "sa"]:
        await message.channel.send(f"Aleyküm Selam {message.author.mention} hoş geldin reis!")
        return
    if msg == "naber":
        await message.channel.send("İyidir kral, sen nasılsın? ne yapacağını bilmiyorsan !yardim yazabilirsin.")
        return
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} düzgün konuş hırrım!")
        return
    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 TAM SÜRÜM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük`, `!gönder @üye [miktar]`")
    embed.add_field(name="🎰 Kumar", value="`!cf [miktar]`, `!bj [miktar]`")
    embed.add_field(name="📦 Kasa", value="`!kasaac` (500 Coin - 10M Çıkma Şansı!)")
    embed.add_field(name="🛠️ Yönetim", value="`!sil [sayı]`, `!ban @üye`")
    await ctx.send(embed=embed)

@bot.command(aliases=['para'])
async def cüzdan(ctx):
    await ctx.send(f"💰 Bakiyen: **{get_balance(ctx.author.id)} Kajun Coin**")

@bot.command()
async def günlük(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 500 coin maaşın yattı reis!")

@bot.command()
async def kasaac(ctx):
    if get_balance(ctx.author.id) < 500: return await ctx.send("❌ Kasa açmak için 500 coin lazım!")
    update_balance(ctx.author.id, -500)
    # 10 Milyon çıkma ihtimalini %1 yaptım (weights içindeki 1)
    odul = random.choices(
        [50, 100, 300, 500, 1500, 10000000], 
        weights=[30, 30, 20, 10, 9, 1], 
        k=1
    )[0]
    update_balance(ctx.author.id, odul)
    await ctx.send(f"📦 Kasadan **{odul}** Kajun Coin çıktı!")

@bot.command()
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    
    player_cards = [random.randint(1, 11), random.randint(1, 11)]
    dealer_cards = [random.randint(1, 11), random.randint(1, 11)]
    
    async def get_msg():
        return f"🃏 Senin elin: **{player_cards}** (Toplam: {sum(player_cards)})\n🕵️ Kasanın kartı: **[{dealer_cards[0]}, ?]**\n\nKart çekmek için **h**, kalmak için **s** yaz."

    game_msg = await ctx.send(await get_msg())

    def check(m):
        return m.author == ctx.author and m.content.lower() in ['h', 's']

    while sum(player_cards) < 21:
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
            if msg.content.lower() == 'h':
                player_cards.append(random.randint(1, 11))
                if sum(player_cards) > 21:
                    update_balance(ctx.author.id, -miktar)
                    return await ctx.send(f"💥 Toplam {sum(player_cards)} oldu, patladın reis! **{miktar}** gitti.")
                await game_msg.edit(content=await get_msg())
            else: break
        except asyncio.TimeoutError:
            return await ctx.send("Zaman doldu, oyun iptal.")

    while sum(dealer_cards) < 17:
        dealer_cards.append(random.randint(1, 11))

    p_total = sum(player_cards)
    d_total = sum(dealer_cards)

    result = f"🃏 Senin: {p_total} | 🕵️ Kasa: {d_total}\n"
    if d_total > 21 or p_total > d_total:
        update_balance(ctx.author.id, miktar)
        await ctx.send(result + f"✅ Kazandın reis! +{miktar}")
    elif p_total < d_total:
        update_balance(ctx.author.id, -miktar)
        await ctx.send(result + f"💀 Kasa kazandı! -{miktar}")
    else:
        await ctx.send(result + "🤝 Berabere, para iade.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    await ctx.channel.purge(limit=sayi + 1)

@bot.event
async def on_ready():
    print(f'KAJUNV36 HAZIR VE NAZIR!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
