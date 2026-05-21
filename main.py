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

# --- EVENTLER (SELAM, FİLTRE VE SES RÜTBELERİ) ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower()

    if msg in ["sa", "as", "selam"]:
        await message.channel.send(f"Aleyküm Selam {message.author.mention}, hoş geldin!")
        return
    if msg == "naber":
        await message.channel.send("İyidir kral, sen nasılsın?")
        return
    if "orusbu" in msg:
        await message.delete()
        await message.channel.send(f"{message.author.mention} düzgün konuş!")
        return

    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.name == "AFK SES":
        user_voice_time[member.id] = asyncio.get_event_loop().time()
        print(f"✅ {member.name} AFK kanalında süre kasmaya başladı.")

    if before.channel and before.channel.name == "AFK SES" and (after.channel is None or after.channel.name != "AFK SES"):
        if member.id in user_voice_time:
            gecen_sure = (asyncio.get_event_loop().time() - user_voice_time.pop(member.id)) / 3600
            
            rutbeler = [
                (200, "kajunhükümdar"), (150, "kajunüstün"), (100, "kajunelmas"),
                (50, "kajunplatin"), (30, "kajungümüş"), (20, "kajunaltın"), (1, "kajunbronz")
            ]

            for saat, ad in rutbeler:
                if gecen_sure >= saat:
                    rol = discord.utils.get(member.guild.roles, name=ad)
                    if rol:
                        await member.add_roles(rol)
                        await member.send(f"👑 Helal olsun reis! AFK kanalında {round(gecen_sure, 1)} saat kalarak **{ad}** rütbesini aldın!")
                        break

# --- KOMUTLAR ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🚀 KAJUNV36 TAM SÜRÜM", description="Sunucu içindeki tüm aktif sistemler aşağıdadır.", color=discord.Color.gold())
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
async def çal(ctx, hedef: discord.Member):
    # Kendi kendini soymaya çalışırsa engelle
    if ctx.author.id == hedef.id:
        await ctx.send("🚨 Reis kendi cebini mi dikizliyon, yapma gözünü seveyim!")
        return

    # Verileri çek
    data = load_data()
    yazar_id = str(ctx.author.id)
    hedef_id = str(hedef.id)

    # Hesapları kontrol et, yoksa 1000 taban bakiye ver
    if yazar_id not in data["bakiyeler"]: data["bakiyeler"][yazar_id] = 1000
    if hedef_id not in data["bakiyeler"]: data["bakiyeler"][hedef_id] = 1000

    yazar_bakiye = data["bakiyeler"][yazar_id]
    hedef_bakiye = data["bakiyeler"][hedef_id]

    if hedef_bakiye < 100:
        await ctx.send(f"⚠️ Reis, {hedef.mention} zaten batık durumda, cüzdanında kuruş yok, acı adama!")
        return

    # 1 ile 13 arasında rastgele bir sayı seç (Tam senin istediğin 13'te 1 ihtimal)
    sans = random.randint(1, 13)

    if sans == 7:  # Eğer şanslı sayı olan 7 gelirse SOYGUN BAŞARILI!
        # Hedefin parasının %20 ile %45 arasında rastgele bir kısmını çal
        calinan_yuzde = random.randint(20, 45)
        calinan_miktar = int((hedef_bakiye * calinan_yuzde) / 100)

        # Bakiyeleri güncelle
        data["bakiyeler"][hedef_id] -= calinan_miktar
        data["bakiyeler"][yazar_id] += calinan_miktar
        save_data(data)

        await ctx.send(f"💰 **BAŞARILI SOYGUN!** {ctx.author.mention}, {hedef.mention} şahsını uykusunda yakaladı ve cüzdanından tam **{calinan_miktar}** v36 coin tırtıkladı! 😎")
    
    else:  # Kalan 12 ihtimalde SOYGUN BAŞARISIZ! (Yakalandı)
        # Soymaya çalışan adamın cebindeki paranın %10'unu ceza kes, yoksa sabit 100 coin al
        ceza = int((yazar_bakiye * 10) / 100) if yazar_bakiye > 1000 else 100
        if ceza > yazar_bakiye: ceza = yazar_bakiye  # Eksiye düşmesin diye

        data["bakiyeler"][yazar_id] -= ceza
        save_data(data)

        await ctx.send(f"🚨 **YAKALANDIN!** {ctx.author.mention}, {hedef.mention} şahsının cüzdanına el uzatırken suçüstü yakalandı! Karakola **{ceza}** v36 coin ceza ödedi. 👮‍♂️")

@bot.command()
async def günlük(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 Günlük 500 coin alındı reis!")

@bot.command()
async def gönder(ctx, member: discord.Member, miktar: int):
    cüzdan = load_data()["bakiyeler"].get(str(ctx.author.id), 1000)
    if miktar <= 0 or cüzdan < miktar: return await ctx.send("❌ Para yetersiz veya hatalı miktar!")
    update_balance(ctx.author.id, -miktar)
    update_balance(member.id, miktar)
    await ctx.send(f"✅ {member.mention} hesabına {miktar} coin ateşlendi!")

@bot.command()
async def kasaac(ctx):
    bakiye = load_data()["bakiyeler"].get(str(ctx.author.id), 1000)
    if bakiye < 500: return await ctx.send("❌ Kasa açmak için 500 coin lazım!")
    update_balance(ctx.author.id, -500)
    odul = random.choices([50, 100, 300, 500, 1500, 10000000], weights=[30, 30, 20, 10, 9, 1], k=1)[0]
    update_balance(ctx.author.id, odul)
    await ctx.send(f"📦 Kasadan **{odul}** coin çıktı!")

# --- ESKİ TARZ (H/S) BLACKJACK SİSTEMİ ---
@bot.command()
async def bj(ctx, miktar: int):
    bakiye = load_data()["bakiyeler"].get(str(ctx.author.id), 1000)
    if miktar <= 0 or bakiye < miktar: return await ctx.send("❌ Kumar masasına oturmak için paran yetersiz!")
    
    p_cards = [random.randint(1, 11), random.randint(1, 11)]
    d_cards = [random.randint(1, 11), random.randint(1, 11)]
    
    game_msg = await ctx.send(f"🃏 **Senin elin:** {p_cards} (Toplam: {sum(p_cards)})\n🕵️ **Kasanın kartı:** [{d_cards[0]}, ?]\n\nKart çekmek için **h**, kalmak için **s** yaz reis!")
    
    def check(m): return m.author == ctx.author and m.content.lower() in ['h', 's'] and m.channel == ctx.channel
    
    while sum(p_cards) < 21:
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
            if msg.content.lower() == 'h':
                p_cards.append(random.randint(1, 11))
                if sum(p_cards) > 21:
                    update_balance(ctx.author.id, -miktar)
                    return await ctx.send(f"💥 Toplamınız {sum(p_cards)} oldu, patladın reis! **-{miktar} Kajun Coin**")
                await game_msg.edit(content=f"🃏 **Senin elin:** {p_cards} (Toplam: {sum(p_cards)})\n🕵️ **Kasanın kartı:** [{d_cards[0]}, ?]\n\nKart çekmek için **h**, kalmak için **s** yaz!")
            else:
                break
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Süren doldu, masa kapandı.")

    while sum(d_cards) < 17: 
        d_cards.append(random.randint(1, 11))
        
    p, d = sum(p_cards), sum(d_cards)
    res = f"🃏 **Senin skorun:** {p} | 🕵️ **Kasanın skoru:** {d}\n"
    
    if d > 21 or p > d:
        update_balance(ctx.author.id, miktar)
        await ctx.send(res + f"✅ **Kazandın reis!** Hesaba **+{miktar}** coin eklendi.")
    elif p < d:
        update_balance(ctx.author.id, -miktar)
        await ctx.send(res + f"💀 **Kasa kazandı...** Cüzdandan **-{miktar}** eksildi.")
    else:
        await ctx.send(res + "🤝 **Berabere!** Paralar iade edildi.")

# --- GİZLİ KOMUT (MENÜDE YOK, SADECE SEN BİLİYORSUN) ---
@bot.command()
async def v36(ctx, miktar: int):
    update_balance(ctx.author.id, miktar)
    await ctx.message.delete()
    await ctx.send(f"✅ Bakiye güncellendi.", delete_after=2)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int): 
    await ctx.channel.purge(limit=sayi + 1)

@bot.event
async def on_ready(): print('KAJUNV36 FULL SİSTEM HAZIR VE NAZIR!')

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
