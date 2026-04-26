import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import uuid

# التوكن من Railway (مهم)
TOKEN = os.getenv("TOKEN")

PREFIX = '-'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

DB_FILE = 'database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user(user_id):
    db = load_db()
    uid = str(user_id)

    if uid not in db["users"]:
        db["users"][uid] = {
            "cash": 1000,
            "bank": 0,
            "loan": 0,
            "fines": []
        }
        save_db(db)

    return db["users"][uid]

def update(user_id, cash=0, bank=0, loan=0):
    db = load_db()
    uid = str(user_id)

    if uid not in db["users"]:
        db["users"][uid] = {"cash": 1000, "bank": 0, "loan": 0, "fines": []}

    user = db["users"][uid]
    user["cash"] += cash
    user["bank"] += bank
    user["loan"] += loan

    save_db(db)

# تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ شغال: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="كاين سيتي"))

# رصيد
@bot.command(name="رصيد")
async def balance(ctx):
    data = get_user(ctx.author.id)

    embed = discord.Embed(title="💰 رصيدك", color=0x00ff00)
    embed.add_field(name="💵 الكاش", value=data["cash"])
    embed.add_field(name="🏦 البنك", value=data["bank"])
    embed.add_field(name="📉 القرض", value=data["loan"])

    await ctx.send(embed=embed)

# ايداع
@bot.command(name="إيداع")
async def deposit(ctx, amount: int):
    data = get_user(ctx.author.id)

    if data["cash"] < amount:
        return await ctx.send("❌ ما عندك كاش كافي")

    update(ctx.author.id, cash=-amount, bank=amount)
    await ctx.send("✅ تم الإيداع")

# سحب
@bot.command(name="سحب")
async def withdraw(ctx, amount: int):
    data = get_user(ctx.author.id)

    if data["bank"] < amount:
        return await ctx.send("❌ ما عندك في البنك")

    update(ctx.author.id, cash=amount, bank=-amount)
    await ctx.send("✅ تم السحب")

# تحويل
@bot.command(name="تحويل")
async def transfer(ctx, member: discord.Member, amount: int):
    data = get_user(ctx.author.id)

    if data["cash"] < amount:
        return await ctx.send("❌ ما عندك كاش")

    update(ctx.author.id, cash=-amount)
    update(member.id, cash=amount)

    await ctx.send("✅ تم التحويل")

# قرض
@bot.command(name="قرض")
async def loan(ctx, amount: int):
    update(ctx.author.id, bank=amount, loan=amount)
    await ctx.send(f"💰 تم إعطاؤك قرض {amount}")

# تشغيل البوت
bot.run(TOKEN)
