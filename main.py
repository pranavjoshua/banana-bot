import discord
from discord.ext import commands, tasks
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
from keep_alive import keep_alive
keep_alive()
from dotenv import load_dotenv
load_dotenv()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load balances
if os.path.exists("balances.json"):
    with open("balances.json", "r") as f:
        balances = json.load(f)
else:
    balances = {}

cooldowns = {}

def save_balances():
    with open("balances.json", "w") as f:
        json.dump(balances, f)

@bot.event
async def on_ready():
    print(f"🍌 BananaBot is online as {bot.user}!")

# 🎯 Earn per message
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = str(message.author.id)
    balances[user_id] = balances.get(user_id, 0) + random.randint(1, 3)
    save_balances()
    await bot.process_commands(message)

@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    bal = balances.get(user_id, 0)
    await ctx.send(f"🍌 You have **{bal} bananas**!")

@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    now = datetime.now()
    if user_id in cooldowns:
        last = cooldowns[user_id]
        if now - last < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last)
            await ctx.send(f"⏳ Come back in {remaining.seconds // 3600} hours for your next daily bananas!")
            return
    balances[user_id] = balances.get(user_id, 0) + 100
    cooldowns[user_id] = now
    save_balances()
    await ctx.send("✅ You claimed **100 bananas** today!")

@bot.command()
async def addbananas(ctx, member: discord.Member, amount: int):
    if ctx.author.guild_permissions.administrator:
        user_id = str(member.id)
        balances[user_id] = balances.get(user_id, 0) + amount
        save_balances()
        await ctx.send(f"💸 Gave **{amount} bananas** to {member.mention}")
    else:
        await ctx.send("❌ You don't have permission.")

@bot.command()
async def shop(ctx):
    shop_items = {
        "🍌 Banana Lover": 200,
        "🐵 Jungle King": 500,
        "💎 Banana Billionaire": 1000
    }
    msg = "**🛒 Banana Shop:**\n"
    for item, price in shop_items.items():
        msg += f"{item}: {price} bananas\n"
    msg += "\nUse `!buy <item name>` to purchase."
    await ctx.send(msg)

@bot.command()
async def buy(ctx, *, item):
    user_id = str(ctx.author.id)
    item_prices = {
        "banana lover": 200,
        "jungle king": 500,
        "banana billionaire": 1000
    }
    item = item.lower()
    if item not in item_prices:
        await ctx.send("❌ Item not found in shop.")
        return
    if balances.get(user_id, 0) >= item_prices[item]:
        balances[user_id] -= item_prices[item]
        save_balances()
        await ctx.send(f"🎉 You bought **{item.title()}**!")
    else:
        await ctx.send("⚠️ Not enough bananas.")

@bot.command()
async def topbananas(ctx):
    sorted_users = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:5]
    msg = "**🏆 Top Banana Holders:**\n"
    for user_id, amount in sorted_users:
        user = await bot.fetch_user(int(user_id))
        msg += f"{user.name}: {amount} bananas\n"
    await ctx.send(msg)

@bot.command()
async def gamble(ctx, amount: int):
    user_id = str(ctx.author.id)
    bal = balances.get(user_id, 0)
    if amount > bal:
        await ctx.send("😢 You don’t have enough bananas.")
        return
    win = random.choice([True, False])
    if win:
        balances[user_id] += amount
        await ctx.send(f"🎉 You won! Now you have {balances[user_id]} bananas!")
    else:
        balances[user_id] -= amount
        await ctx.send(f"💀 You lost! Now you have {balances[user_id]} bananas.")
    save_balances()

@bot.command()
async def heist(ctx, amount: int):
    user_id = str(ctx.author.id)
    bal = balances.get(user_id, 0)
    if amount > bal or amount <= 0:
        await ctx.send("🚫 Invalid banana amount.")
        return
    success = random.random() < 0.5
    if success:
        gain = int(amount * 1.5)
        balances[user_id] += gain
        await ctx.send(f"🦍 You pulled off a successful banana heist! You earned {gain} bananas!")
    else:
        balances[user_id] -= amount
        await ctx.send("🚨 You got caught during the heist and lost your bananas!")
    save_balances()

@bot.command()
async def invite(ctx):
    await ctx.send("📩 Invite BananaBot to your server:\nhttps://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot")

import os
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
