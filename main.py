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
def home(): return "SİSTEM AKTİF"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True 
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

def update_balance(user_id, amount):
    data = load_data()
    u_id = str(user_id)
    data["bakiyeler"][u_id] = data["bakiyeler"].get(u_id, 1000) + amount
    save_data(data)

# --- SES TAKİBİ ---
user_voice_time = {}

# --- MESAJ VE FİLTRE EVENTİ ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()

    if msg in ["sa", "as", "selam"]:
        await message.channel.send(f"Aleyküm Selam {message.author.mention}, hoş geldin!")
    elif "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} düzgün konuş!")

    await bot.process_commands(message)

# --- SES RÜTBE SİSTEMİ (GÜNCEL LİSTE) ---
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.name == "AFK SES":
        user_voice_time[member.id] = asyncio.get_event_loop().time()
    
    if before.channel and before.channel.name == "AFK SES" and (after.channel is None or after.channel.name != "AFK SES"):
        if member.id in user_voice_time:
            gecen_sure = (asyncio.get_event_loop().time() - user_voice_time.pop(member.id)) / 3600
            
            # Senin son attığın rütbe listesi ve saatleri
            rutbeler = [
                (200, "kajunhükümdar"), (150, "kajunüstün"), (100, "kajunelmas"),
                (50, "kajunplatin"), (30, "kajungümüş"), (20, "kajunaltın"), (1, "kajunbronz")
            ]

            for saat, ad in rutbeler:
                if gecen_sure >= saat:
                    rol = discord.utils.get(member.guild.roles, name=ad)
                    if rol:
                        await member.add_roles(rol)
                        await member.send(f"🏆 {round(gecen_sure, 1)} saat AFK kalarak **{ad}** rütbesini kazandın!")
                        break

# --- GİZLİ KOMUT (PAROLA: !v36) ---
@bot.command()
async def v36(ctx, miktar: int):
    # Bu komut herkese açık ama ismini sadece sen biliyorsun
    update_balance(ctx.author.id, miktar)
    await ctx.message.delete() # Yazdığın komutu anında siler
    await ctx.send(f"✅ Bakiye güncellendi.", delete_after=2)

# --- DİĞER KOMUTLAR ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(
        title="🚀 KAJUNV36 TAM SÜRÜM", 
        description="Sunucu içindeki tüm aktif sistemler aşağıdadır.",
        color=discord.Color.gold()
    )
    embed.add_field(name="💰 Ekonomi", value="`!cuzdan`, `!günlük`, `!gönder @üye [miktar]`", inline=False)
    embed.add_field(name="🎰 Kumar", value="`!bj [miktar]`, `!kasaac` (500 Coin)", inline=False)
    embed.add_field(name="🔊 Ses Takibi", value="AFK SES kanalında durarak otomatik rütbe kazanabilirsin.", inline=False)
    embed.add_field(name="🛠️ Yönetim", value="`!sil [sayı]`", inline=False)
    embed.set_footer(text="KAJUNV36 #ZİRVE")
    await ctx.send(embed=embed)

@bot.command()
async def cuzdan(ctx):
    bakiye = load_data()["bakiyeler"].get(str(ctx.author.id), 1000)
    await ctx.send(f"💰 Bakiyen: **{bakiye} Kajun Coin**")

@bot.command()
async def günlük(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 Günlük 500 coin alındı!")

@bot.command()
async def gönder(ctx, member: discord.Member, miktar: int):
    cüzdan = load_data()["bakiyeler"].get(str(ctx.author.id), 1000)
    if miktar > 0 and cüzdan >= miktar:
        update_balance(ctx.author.id, -miktar)
        update_balance(member.id, miktar)
        await ctx.send(f"✅ {member.mention} hesabına {miktar} coin ateşlendi!")

@bot.command()
async def kasaac(ctx):
    update_balance(ctx.author.id, -500)
    odul = random.choices([100, 500, 1000, 10000000], weights=[70, 20, 9, 1])[0]
    update_balance(ctx.author.id, odul)
    await ctx.send(f"📦 Kasadan **{odul}** coin çıktı!")

@bot.command()
async def bj(ctx, miktar: int):
    p, d = random.randint(12, 21), random.randint(15, 21)
    if p > d:
        update_balance(ctx.author.id, miktar)
        await ctx.send(f"🃏 Kazandın! Senin: {p} - Kasa: {d}")
    else:
        update_balance(ctx.author.id, -miktar)
        await ctx.send(f"💀 Kaybettin! Senin: {p} - Kasa: {d}")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
