import discord
import os
import random
import asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- 7/24 AKTİF TUTMA SİSTEMİ ---
app = Flask('')
@app.route('/')
def home(): return "KAJUNV36 Bot Zirve'de!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Üyeleri banlamak/atmak için bu şart!

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

envanterler = {}

# --- MODERASYON KOMUTLARI ---

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    await member.ban(reason=reason)
    await ctx.send(f"🚫 **{member.name}** sunucudan banlandı! Sebep: {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    await member.kick(reason=reason)
    await ctx.send(f"👞 **{member.name}** sunucudan şutlandı! Sebep: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)
    mesaj = await ctx.send(f"🧹 {miktar} adet mesaj temizlendi reis!")
    await asyncio.sleep(3)
    await mesaj.delete()

# --- ANIMASYONLU OYUNLAR ---

@bot.command()
async def zar(ctx):
    mesaj = await ctx.send("🎲 Zar atılıyor...")
    await asyncio.sleep(1)
    await mesaj.edit(content="🎲 Zar dönüyor: ⚀")
    await asyncio.sleep(0.5)
    sonuc = random.randint(1, 6)
    await mesaj.edit(content=f"🎲 Zar durdu! Sonuç: **{sonuc}** geldi!")

@bot.command()
async def kasaac(ctx):
    mesaj = await ctx.send("📦 Kasa hazırlanıyor...")
    await asyncio.sleep(1)
    await mesaj.edit(content="🔓 Kasa kilidi açılıyor... 🔑")
    await asyncio.sleep(1)
    oduller = ["100 XP", "Bronz Kasa", "Gümüş Kasa", "Altın Kasa", "Elmas Anahtar"]
    kazanilan = random.choice(oduller)
    user_id = str(ctx.author.id)
    if user_id not in envanterler: envanterler[user_id] = []
    envanterler[user_id].append(kazanilan)
    await mesaj.edit(content=f"🎉 {ctx.author.mention}, kasadan şansına **{kazanilan}** çıktı!")

# --- KÜFÜR FİLTRESİ ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if "orusbu" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} ne diyon lan hırrım burası KAJUNV36 he istediğine istediğin gibi orusbu diyemezsin burda!")
    await bot.process_commands(message)

@bot.event
async def on_ready(): print(f'KAJUNV36 Botu Hazır! Bot: {bot.user}')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
