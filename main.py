import discord
import os
import random
import asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread

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
envanterler = {}

# --- YARDIM KOMUTU ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(
        title="🚀 Ezxayomisari Bot Kullanım Kılavuzu",
        description="Sunucudaki tüm komutlar aşağıdadır. Bu mesajı sabitleyerek her zaman görebilirsiniz!",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎮 Oyunlar", value="`!zar`: Animasyonlu zar atar.\n`!yazitura`: Para çevirir.\n`!kasaac`: Kasa açıp ödül kazandırır.\n`!envanter`: Kazandığın ödülleri gösterir.", inline=False)
    embed.add_field(name="🛠️ Yönetim", value="`!ban @üye`: Üyeyi yasaklar.\n`!unban İsim#0000`: Banı kaldırır.\n`!sil [sayı]`: Mesajları temizler.", inline=False)
    embed.add_field(name="🛡️ Koruma", value="**Küfür Filtresi**: 'orusbu' kelimesini anında siler.", inline=False)
    embed.add_field(name="💬 Sohbet", value="**naber**: Botla selamlaşmanı sağlar.", inline=False)
    embed.set_footer(text="KAJUNV36 #PRIME")
    await ctx.send(embed=embed)

# --- MODERASYON ---
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    await member.ban(reason=reason)
    await ctx.send(f"🚫 **{member.name}** banlandı!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned_users = [entry async for entry in ctx.guild.bans()]
    for ban_entry in banned_users:
        user = ban_entry.user
        if (f"{user.name}#{user.discriminator}" == member_name) or (user.name == member_name):
            await ctx.guild.unban(user)
            await ctx.send(f"✅ **{user.name}** kullanıcısının banı kaldırıldı reis, buyursun gelsin!")
            return
    await ctx.send(f"❓ Reis bu isimde birini banlılar listesinde bulamadım.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)

# --- ANIMASYONLU OYUNLAR ---
@bot.command()
async def zar(ctx):
    mesaj = await ctx.send("🎲 Zar dönüyor...")
    await asyncio.sleep(1)
    sonuc = random.randint(1, 6)
    await mesaj.edit(content=f"🎲 Zar durdu! Sonuç: **{sonuc}**")

@bot.command()
async def yazitura(ctx):
    mesaj = await ctx.send("🪙 Para havada dönüyor... 🔄")
    await asyncio.sleep(1.5)
    sonuc = random.choice(["Yazı", "Tura"])
    await mesaj.edit(content=f"🪙 Para yere düştü! **{sonuc}** geldi!")

@bot.command()
async def kasaac(ctx):
    mesaj = await ctx.send("📦 Kasa açılıyor... 🔑")
    await asyncio.sleep(1.5)
    oduller = ["100 XP", "Bronz Kasa", "Gümüş Kasa", "Altın Kasa", "Elmas Anahtar"]
    kazanilan = random.choice(oduller)
    user_id = str(ctx.author.id)
    if user_id not in envanterler: envanterler[user_id] = []
    envanterler[user_id].append(kazanilan)
    await mesaj.edit(content=f"🎉 {ctx.author.mention}, kasadan **{kazanilan}** çıktı!")

@bot.command()
async def envanter(ctx):
    user_id = str(ctx.author.id)
    if user_id in envanterler and envanterler[user_id]:
        items = ", ".join(envanterler[user_id])
        await ctx.send(f"🎒 {ctx.author.mention} Envanterin: {items}")
    else:
        await ctx.send(f"🎒 Envanterin boş reis!")

# --- KÜFÜR VE NABER KONTROLÜ ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} ne diyon lan hırrım burası KAJUNV36 he istediğine istediğin gibi orusbu diyemezsin burda!")
        return
    if msg == "naber":
        await message.channel.send(f"İyi kral sen nasılsın beni nasıl kullanabileceğini öğrenmek için !yardim yazabilirsin.")
        return
    await bot.process_commands(message)

@bot.event
async def on_ready(): print(f'KAJUNV36 Hazır!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
