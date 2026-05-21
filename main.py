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
    embed.add_field(name="💰 Ekonomi", value="`!cuzdan`, `!zenginler`, `!günlük`, `!gönder @üye [miktar]`", inline=False)
    embed.add_field(name="🎰 Kumar", value="`!bj [miktar]`, `!rulet [bahis]`, `!kasaac` (500 Coin)", inline=False)
    embed.add_field(name="🔊 Ses Takibi", value="AFK SES kanalında durarak otomatik rütbe kazanabilirsin.", inline=False)
    embed.add_field(name="🛠️ Yönetim", value="`!sil [sayı]`", inline=False)
    embed.add_field(name="💸 hırsızlık", value="`!çal`", inline=False)
    embed.add_field(name="🛡 güvenlik", value="`!yelekal`", inline=False)
    embed.set_footer(text="KAJUNV36 #PRIME")
    await ctx.send(embed=embed)

@bot.command()
async def cuzdan(ctx):
    bakiye = load_data()["bakiyeler"].get(str(ctx.author.id), 1000)
    await ctx.send(f"💰 Bakiyen: **{bakiye} Kajun Coin**")

@bot.command()
async def yelekal(ctx):
    data = load_data()
    yazar_id = str(ctx.author.id)

    if yazar_id not in data["bakiyeler"]: data["bakiyeler"][yazar_id] = 1000
    # Eğer yelekler tablosu json'da yoksa ilk defa oluşturur
    if "yelekler" not in data: data["yelekler"] = {}
    if yazar_id not in data["yelekler"]: data["yelekler"][yazar_id] = 0

    if data["bakiyeler"][yazar_id] < 2500:
        await ctx.send("❌ Reis cüzdan boş! Çelik yelek 2500 v36 coin, önce biraz çalış veya kumar oyna.")
        return

    data["bakiyeler"][yazar_id] -= 2500
    data["yelekler"][yazar_id] += 1
    save_data(data)

    await ctx.send(f"🛡️ **İŞLEM BAŞARILI!** {ctx.author.mention}, 2500 coine çelik yeleği sırtına geçirdin! Artık seni soymaya çalışanlar düşünsün. (Kalan Yelek: {data['yelekler'][yazar_id]})")

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

    # === ÇAL KOMUTUNUN İÇİNE EKLENECEK YELEK KORUMASI ===
    if "yelekler" not in data: data["yelekler"] = {}
    if hedef_id not in data["yelekler"]: data["yelekler"][hedef_id] = 0

    if data["yelekler"][hedef_id] > 0:
        # Hedefin yeleği var! Soygunu otomatik engelle ve yeleği kır
        data["yelekler"][hedef_id] -= 1
        save_data(data)
        await ctx.send(f"🛡️ **YELEK DEVREDE!** {ctx.author.mention}, {hedef.mention} şahsını soymaya çalıştın ama adam çelik yelek giymiş! Soygun başarısız oldu ve {hedef.mention}'ın yeleği parçalandı! 🧱")
        return
    # ===================================================

@bot.command()
async def rulet(ctx, bahis: int):
    if bahis <= 0:
        await ctx.send("⚠️ Reis düzgün bir bahis miktarı gir gözünü seveyim!")
        return

    data = load_data()
    yazar_id = str(ctx.author.id)

    if yazar_id not in data["bakiyeler"]: data["bakiyeler"][yazar_id] = 1000
    
    if data["bakiyeler"][yazar_id] < bahis:
        await ctx.send("❌ Reis bu kadar coinin yok ki ortaya koyasın!")
        return

    # Şarjördeki 6 yuvayı temsil eden liste (1 tanesi dolu mermi -> True)
    # Her oyunda merminin yeri rastgele değişir
    sarjor = [False, False, False, False, False, False]
    mermi_konumu = random.randint(0, 5)
    sarjor[mermi_konumu] = True

    tur = 1
    guncel_bahis = bahis

    await ctx.send(f"🎲 **RUS RULETİ BAŞLADI!** {ctx.author.mention} ortaya **{guncel_bahis}** coin koydu. Şarjör çevrildi, namlu şakağa dayandı... İlk el zorunlu sıkılıyor! 💥")
    await asyncio.sleep(1.5)

    # 1. EL (OTOMATİK SIKILMA)
    if sarjor[0] == True:
        data["bakiyeler"][yazar_id] -= guncel_bahis
        save_data(data)
        await ctx.send(f"💥 **GÜÜÜM!** İlk elden mermiye denk geldin reis! **{guncel_bahis}** coin kasaya uçtu... Geçmiş olsun 💀")
        return
    else:
        # İlk elden sağ çıkarsa ödül havuzu %50 katlanarak başlasın (Heyecan artsın)
        guncel_bahis = int(guncel_bahis * 1.5)
        await ctx.send(f"🔫 *Tık...* İlk el boş çıktı! Canlısın reis. Ödül şu an **{guncel_bahis}** coin. Devam etmek istiyor musun?")

    # 2. EL VE SONRASI İÇİN DÖNGÜ (Maksimum 5 kere sıkabilir, çünkü 6. zaten kesin mermidir)
    for i in range(1, 5):
        await ctx.send(f"❓ {ctx.author.mention}, ne yapacaksın? Sohbet kanalına **sık** veya **dur** yaz!")

        # Kullanıcının "sık" veya "dur" yazmasını bekleme fonksiyonu
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["sık", "dur", "sik"]

        try:
            # Kullanıcıya cevap vermesi için 30 saniye süre tanıyalım, vermezse korktu sayıp durduralım
            msg = await bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(f"⏱️ Süren bitti reis! Çok tırstın herhalde, oyun senin adına **durdu**.")
            break

        # DURURSA PARAYI ALIR VE OYUN BİTER
        if msg.content.lower() == "dur":
            data["bakiyeler"][yazar_id] += (guncel_bahis - bahis) # Net karı ekle
            save_data(data)
            await ctx.send(f"💰 **ZİRVEDE BIRAKTIN!** {ctx.author.mention} masadan çekildi ve **{guncel_bahis}** coini cüzdanına indirdi. Korkak ama zengin! 😎")
            return

        # SIKARSA
        elif msg.content.lower() in ["sık", "sik"]:
            await ctx.send(f"🔄 {ctx.author.mention} tetiği tekrar çekiyor... Nefesler tutuldu...")
            await asyncio.sleep(1.5)

            if sarjor[i] == True: # Mermiye denk gelirse her şey gider
                data["bakiyeler"][yazar_id] -= bahis # Ana bahsi kaybettir
                save_data(data)
                await ctx.send(f"💥 **GÜÜÜM! {i+1}. elde beyin bedava!** Mermi patladı, **{bahis}** coinin havaya uçtu reis... 💀")
                return
            else:
                # Yaşarsa bahis çarpanı katlanarak artar!
                guncel_bahis = int(guncel_bahis * 1.8)
                await ctx.send(f"🔫 *Tık...* Yine boş! Şansına tüküreyim reis harbi bordo berelisin. Güncel ödülün: **{guncel_bahis}** coin!")

    # Eğer 5 kere sıkıp hala ölmediyse (Zorunlu son el kalır, kasa parayı verir)
    data["bakiyeler"][yazar_id] += (guncel_bahis - bahis)
    save_data(data)
    await ctx.send(f"🏆 **İNANILMAZ BAŞARI!** {ctx.author.mention} ölümün kıyısından 5 kere geçti ve ölmedi! Toplam **{guncel_bahis}** coini söke söke aldı! Sunucu ağası ilan ediyoruz!")

@bot.command()
async def günlük(ctx):
    update_balance(ctx.author.id, 500)
    await ctx.send("💵 Günlük 500 coin alındı reis!")

@bot.command()
async def zenginler(ctx):
    data = load_data()
    bakiyeler = data["bakiyeler"]

    # Bakiyeleri paraya göre büyükten küçüğe sırala
    sirali_liste = sorted(bakiyeler.items(), key=lambda x: x[1], reverse=True)

    mesaj = "🏆 **KAJUNV36 #ZİRVE - ZENGİNLER LİSTESİ** 🏆\n"
    mesaj += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    # İlk 5 zengini listele (Sunucuda real 5 kişi olduğu için tam uyar)
    for sira, (kullanici_id, para) in enumerate(sirali_liste[:5], 1):
        try:
            # Kullanıcı adını Discord'dan çekmeye çalışır
            uye = await ctx.guild.fetch_member(int(kullanici_id))
            isim = uye.display_name
        except:
            isim = f"Bilinmeyen Şahıs ({kullanici_id})"
        
        madalya = "🥇" if sira == 1 else "🥈" if sira == 2 else "🥉" if sira == 3 else "💸"
        mesaj += f"{madalya} **{sira}.** {isim} ➔ **{para}** v36 coin\n"

    mesaj += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    mesaj += "*Zirvedekiler yerini korusun, arkadakiler cüzdan dikizlesin!*"
    
    await ctx.send(mesaj)

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
