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

# --- EKONOMİ VERİ TABANI (JSON) ---
DATA_FILE = "ekonomi.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"bakiyeler": {}, "last_daily": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def get_balance(user_id):
    data = load_data()
    return data["bakiyeler"].get(str(user_id), 1000) # Başlangıç parası 1000

def update_balance(user_id, amount):
    data = load_data()
    user_id = str(user_id)
    data["bakiyeler"][user_id] = data["bakiyeler"].get(user_id, 1000) + amount
    save_data(data)

# --- YARDIM KOMUTU ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 EKONOMİ & YÖNETİM", color=discord.Color.gold())
    embed.add_field(name="💰 Ekonomi", value="`!cüzdan`: Paranızı gösterir.\n`!günlük`: Günlük 500 Kajun Coin verir.\n`!gönder @üye [miktar]`: Para transferi yapar.", inline=False)
    embed.add_field(name="🎰 Kumar (OwO Style)", value="`!cf [miktar]`: Yazı-tura ile parayı katla.\n`!slot [miktar]`: Şansını meyvelerde dene.", inline=False)
    embed.add_field(name="🛠️ Yönetim", value="`!ban @üye`, `!unban`, `!sil [sayı]`", inline=False)
    embed.set_footer(text="KAJUNV36 #PRIME")
    await ctx.send(embed=embed)

# --- EKONOMİ KOMUTLARI ---
@bot.command(aliases=['cash', 'money', 'para'])
async def cuzdan(ctx):
    bal = get_balance(ctx.author.id)
    await ctx.send(f"💰 {ctx.author.mention}, şu anki bakiyen: **{bal} Kajun Coin**")

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
            await ctx.send(f"⏳ Reis daha çok çalıştın, dinlen biraz! {kalan.seconds // 3600} saat sonra gel.")
            return

    update_balance(user_id, 500)
    data["last_daily"][user_id] = now.strftime("%Y-%m-%d %H:%M:%S")
    save_data(data)
    await ctx.send(f"💵 {ctx.author.mention}, bugünkü **500 Kajun Coin** maaşın yattı! Güle güle harca.")

@bot.command(aliases=['send'])
async def gonder(ctx, member: discord.Member, miktar: int):
    if miktar <= 0: return await ctx.send("❓ Şaka mı yapıyon reis?")
    if get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Cüzdanın boş, önce biraz para kazan!")
    
    update_balance(ctx.author.id, -miktar)
    update_balance(member.id, miktar)
    await ctx.send(f"✅ {ctx.author.mention}, {member.mention} kullanıcısına **{miktar} Kajun Coin** ateşledi!")

# --- KUMAR KOMUTLARI ---
@bot.command()
async def cf(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Yetersiz bakiye reis!")
    
    await ctx.send(f"🪙 {ctx.author.mention}, **{miktar}** coinine yazı-tura atıyor... 🔄")
    await asyncio.sleep(2)
    
    if random.choice([True, False]):
        update_balance(ctx.author.id, miktar)
        await ctx.send(f"🎉 Kazandın! Hesabına **{miktar}** eklendi. Yeni bakiye: {get_balance(ctx.author.id)}")
    else:
        update_balance(ctx.author.id, -miktar)
        await ctx.send(f"💀 Kaybettin reis... **{miktar}** coin uçtu gitti.")

@bot.command()
async def slot(ctx, miktar: int):
    if miktar <= 0 or get_balance(ctx.author.id) < miktar: return await ctx.send("❌ Paran yetmiyor reis!")
    
    emoji_list = ["🍎", "🍋", "🍒", "💎", "⭐"]
    r1, r2, r3 = [random.choice(emoji_list) for _ in range(3)]
    
    mesaj = await ctx.send(f"🎰 | {ctx.author.mention} slot çeviriyor...\n[ ❓ | ❓ | ❓ ]")
    await asyncio.sleep(1.5)
    
    if r1 == r2 == r3:
        win = miktar * 5
        update_balance(ctx.author.id, win)
        status = f"JACKPOT! 🏆 **{win}** kazandın!"
    elif r1 == r2 or r2 == r3 or r1 == r3:
        win = int(miktar * 1.5)
        update_balance(ctx.author.id, win)
        status = f"Fena değil! **{win}** kazandın."
    else:
        update_balance(ctx.author.id, -miktar)
        status = "Hiçbiri tutmadı, kasa kazandı! 💀"

    await mesaj.edit(content=f"🎰 | {ctx.author.mention} sonucu:\n[ {r1} | {r2} | {r3} ]\n{status}")

# --- STANDART MODERASYON & MESAJ ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} KAJUNV36 burası, racona ters konuşma!")
        return
    if msg == "naber":
        await message.channel.send(f"İyidir kral, kumarhanemiz açıldı haberin olsun! !yardım yaz gör.")
        return
    await bot.process_commands(message)

@bot.event
async def on_ready(): print(f'KAJUNV36 Zirve Kumarhanesi Hazır!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
