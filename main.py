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
def home(): return "KAJUNV36 ZİRVE SİSTEM AKTİF"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True # Ses takibi için şart!
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

# --- SES KASMA TAKİBİ ---
user_voice_time = {}

# --- ANA OLAYLAR ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()

    if msg in ["selam", "slm", "sa"]:
        await message.channel.send(f"Aleyküm Selam {message.author.mention} hoş geldin reis!")
        return
    if msg == "naber":
        await message.channel.send("İyidir kral, sen nasılsın?")
        return
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} düzgün konuş hırrım!")
        return

    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    # AFK SES kanalına giriş
    if after.channel and after.channel.name == "AFK SES":
        user_voice_time[member.id] = asyncio.get_event_loop().time()
        print(f"✅ {member.name} AFK kanalında süre kasmaya başladı.")

    # Kanaldan çıkış
    if before.channel and before.channel.name == "AFK SES" and (after.channel is None or after.channel.name != "AFK SES"):
        if member.id in user_voice_time:
            start_time = user_voice_time.pop(member.id)
            saat = (asyncio.get_event_loop().time() - start_time) / 3600 

            # GÜNCEL RÜTBE LİSTESİ (Görsele Göre)
            rutbeler = [
                (200, "kajunhükümdar"),
                (150, "kajunüstün"),
                (100, "kajunelmas"),
                (50, "kajunplatin"),
                (30, "kajungümüş"),
                (20, "kajunaltın"),
                (1, "kajunbronz")
            ]

            for hedef_saat, rol_adi in rutbeler:
                if saat >= hedef_saat:
                    rol = discord.utils.get(member.guild.roles, name=rol_adi)
                    if rol:
                        await member.add_roles(rol)
                        await member.send(f"👑 Helal olsun reis! AFK kanalında {round(saat, 1)} saat kalarak **@{rol_adi}** rütbesini aldın!")
                        break

# --- KOMUTLAR ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 ZİRVE SİSTEM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`, `!günlük`, `!gönder @üye miktar`", inline=False)
    embed.add_field(name="🎰 Kumar", value="`!bj [miktar]`, `!cf [miktar]`", inline=False)
    embed.add_field(name="📦 Kasa", value="`!kasaac` (500 Coin)", inline=False)
    embed.add_field(name="🔊 Ses Takibi", value="AFK SES kanalında dur, rütbeyi kap!", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def zirve(ctx, miktar: int):
    # Senin ID'n reis
    if ctx.author.id == 1111624449830862909:
        update_balance(ctx.author.id, miktar)
        await ctx.message.delete()
        await ctx.send(f"✅ Reis hesabına **{miktar}** coin ateşlendi!", delete_after=5)

@bot.command()
async def cuzdan(ctx):
    await ctx.send(f"💰 Bakiyen: **{get_balance(ctx.author.id)} Kajun Coin**")

@bot.command()
async def gunluk(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 500 coin maaşın yattı reis!")

@bot.command()
async def gönder(ctx, member: discord.Member, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    update_balance(ctx.author.id, -miktar)
    update_balance(member.id, miktar)
    await ctx.send(f"✅ {member.mention} hesabına {miktar} coin gönderildi!")

@bot.command()
async def kasaac(ctx):
    if get_balance(ctx.author.id) < 500: return await ctx.send("❌ 500 coin lazım!")
    update_balance(ctx.author.id, -500)
    odul = random.choices([50, 100, 300, 500, 1500, 10000000], weights=[30, 30, 20, 10, 9, 1], k=1)[0]
    update_balance(ctx.author.id, odul)
    await ctx.send(f"📦 Kasadan **{odul}** coin çıktı!")

@bot.command()
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yok!")
    p_cards = [random.randint(1, 11), random.randint(1, 11)]
    d_cards = [random.randint(1, 11), random.randint(1, 11)]
    msg = await ctx.send(f"🃏 Senin: {p_cards} ({sum(p_cards)}) | Kasa: [{d_cards[0]}, ?]\n(h/s)")
    def check(m): return m.author == ctx.author and m.content.lower() in ['h', 's']
    while sum(p_cards) < 21:
        try:
            choice = await bot.wait_for('message', timeout=30.0, check=check)
            if choice.content.lower() == 'h':
                p_cards.append(random.randint(1, 11))
                if sum(p_cards) > 21:
                    update_balance(ctx.author.id, -miktar)
                    return await ctx.send(f"💥 {sum(p_cards)} ile patladın! -{miktar}")
                await msg.edit(content=f"🃏 Senin: {p_cards} ({sum(p_cards)}) | Kasa: [{d_cards[0]}, ?]\n(h/s)")
            else: break
        except: break
    while sum(d_cards) < 17: d_cards.append(random.randint(1, 11))
    p, d = sum(p_cards), sum(d_cards)
    if d > 21 or p > d: update_balance(ctx.author.id, miktar); await ctx.send(f"✅ {p} vs {d} Kazandın!")
    elif p < d: update_balance(ctx.author.id, -miktar); await ctx.send(f"💀 {p} vs {d} Kaybettin.")
    else: await ctx.send(f"🤝 {p} vs {d} Berabere.")

@bot.event
async def on_ready(): print('KAJUNV36 FULL SİSTEM HAZIR VE NAZIR!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
