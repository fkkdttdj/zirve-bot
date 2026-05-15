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

def get_balance(user_id):
    data = load_data()
    return data["bakiyeler"].get(str(user_id), 1000)

def update_balance(user_id, amount):
    data = load_data()
    u_id = str(user_id)
    data["bakiyeler"][u_id] = data["bakiyeler"].get(u_id, 1000) + amount
    save_data(data)

# --- GLOBAL DEĞİŞKENLER ---
user_voice_time = {}

# --- 1. EVENT: MESAJLAR (SELAM & FİLTRE) ---
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

# --- 2. EVENT: SES RÜTBELERİ ---
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.name == "AFK SES":
        user_voice_time[member.id] = asyncio.get_event_loop().time()
    
    if before.channel and before.channel.name == "AFK SES" and (after.channel is None or after.channel.name != "AFK SES"):
        if member.id in user_voice_time:
            start_time = user_voice_time.pop(member.id)
            saat = (asyncio.get_event_loop().time() - start_time) / 3600 
            rutbeler = [(200, "kajunhükümdar"), (150, "kajunüstün"), (100, "kajunelmas"), (50, "kajunplatin"), (30, "kajungümüş"), (20, "kajunaltın"), (1, "kajunbronz")]
            for hedef_saat, rol_adi in rutbeler:
                if saat >= hedef_saat:
                    rol = discord.utils.get(member.guild.roles, name=rol_adi)
                    if rol:
                        await member.add_roles(rol)
                        await member.send(f"👑 Helal olsun reis! AFK kanalında {round(saat, 1)} saat kalarak **{rol_adi}** rütbesini aldın!")
                        break

# --- KOMUTLAR (YARDIM, KASA, BLACKJACK) ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 ZİRVE SİSTEM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cuzdan`, `!gunluk`", inline=True)
    embed.add_field(name="🎰 Kumar", value="`!bj [miktar]`, `!cf [miktar]`", inline=True)
    embed.add_field(name="📦 Kasa", value="`!kasaac` (500 Coin - 10M Şansı)", inline=False)
    embed.add_field(name="🔊 Ses Rütbe", value="AFK SES kanalında dur rütbeyi kap!", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def cuzdan(ctx):
    await ctx.send(f"💰 Bakiyen: **{get_balance(ctx.author.id)} Kajun Coin**")

@bot.command()
async def para(ctx, miktar: int):
    # Senin profilinden aldığım ID'n reis
    SAHIP_ID = 1111624449830862909 

    if ctx.author.id == SAHIP_ID:
        update_balance(ctx.author.id, miktar)
        await ctx.message.delete() # Senin yazdığın komutu siler, kimse çakmaz
        await ctx.send(f"✅ Reis hesabına **{miktar}** Kajun Coin ateşlendi. Kimse görmedi, rahat ol.", delete_after=5)
    else:
        # Başkası yazarsa bot sanki böyle bir komut yokmuş gibi davransın
        pass

@bot.command()
async def gunluk(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 500 coin maaşın yattı reis!")

@bot.command()
async def kasaac(ctx):
    if get_balance(ctx.author.id) < 500: return await ctx.send("❌ Kasa açmak için 500 coin lazım!")
    update_balance(ctx.author.id, -500)
    odul = random.choices([50, 100, 300, 500, 1500, 10000000], weights=[30, 30, 20, 10, 9, 1], k=1)[0]
    update_balance(ctx.author.id, odul)
    await ctx.send(f"📦 Kasadan **{odul}** Kajun Coin çıktı!")

@bot.command()
async def bj(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Para yetersiz!")
    p_cards = [random.randint(1, 11), random.randint(1, 11)]
    d_cards = [random.randint(1, 11), random.randint(1, 11)]
    game_msg = await ctx.send(f"🃏 Senin: {p_cards} ({sum(p_cards)}) | 🕵️ Kasa: [{d_cards[0]}, ?]\n(h/s)")
    def check(m): return m.author == ctx.author and m.content.lower() in ['h', 's']
    while sum(p_cards) < 21:
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
            if msg.content.lower() == 'h':
                p_cards.append(random.randint(1, 11))
                if sum(p_cards) > 21:
                    update_balance(ctx.author.id, -miktar)
                    return await ctx.send(f"💥 {sum(p_cards)} ile patladın reis! -{miktar}")
                await game_msg.edit(content=f"🃏 Senin: {p_cards} ({sum(p_cards)}) | 🕵️ Kasa: [{d_cards[0]}, ?]\n(h/s)")
            else: break
        except: break
    while sum(d_cards) < 17: d_cards.append(random.randint(1, 11))
    p, d = sum(p_cards), sum(d_cards)
    res = f"🃏 Senin: {p} | 🕵️ Kasa: {d}\n"
    if d > 21 or p > d: update_balance(ctx.author.id, miktar); await ctx.send(res + "✅ Kazandın!")
    elif p < d: update_balance(ctx.author.id, -miktar); await ctx.send(res + "💀 Kaybettin.")
    else: await ctx.send(res + "🤝 Berabere.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int): await ctx.channel.purge(limit=sayi + 1)

@bot.event
async def on_ready(): print(f'KAJUNV36 FULL SISTEM AKTIF!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
