import discord
import asyncio
from discord.ext import commands, tasks
from mcstatus import JavaServer
from flask import Flask
from threading import Thread

# Flask app to keep the bot alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 🔒 Hardcoded bot token and server details (⚠️ Do not expose publicly)
TOKEN = "MTM1NDc4NzQ1NTY5NzY4Njc0OQ.GnfLjL.yHtdEshstFJWzrvsyV-GvBXNS9rzKw5yPozsyU"
SERVER_IP = "TideCleansers.aternos.me"
SERVER_PORT = 26326
CHANNEL_ID = 1354762861116784791  # Replace with your actual Discord channel ID

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    
    if channel:
        embed = discord.Embed(
            title="🌍 Minecraft Server Status",
            description=f"Tracking status for `{SERVER_IP}:{SERVER_PORT}`",
            color=discord.Color.green()
        )
        embed.set_footer(text="Status updates every 30 seconds")
        msg = await channel.send(embed=embed)
        
        # Start updating the message every 30 seconds
        update_status.start(msg)
    else:
        print("⚠️ Channel not found. Make sure the bot has access!")

@tasks.loop(seconds=30)
async def update_status(msg):
    """ Updates the embed message with the latest server status """
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = server.status()
        
        embed = discord.Embed(
            title="✅ Server is Online!",
            description=f"🌐 **IP:** `{SERVER_IP}:{SERVER_PORT}`",
            color=discord.Color.green()
        )
        embed.add_field(name="👥 Players Online", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="📶 Ping", value=f"{status.latency}ms", inline=True)
        embed.add_field(name="📝 MOTD", value=status.description.replace("§", ""), inline=False)
        embed.set_footer(text="🔄 Status updates every 30 seconds")
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Server is Offline!",
            description="The Minecraft server is currently unreachable.",
            color=discord.Color.red()
        )
        embed.set_footer(text="🔄 Checking again in 30 seconds")
        print(e)

    await msg.edit(embed=embed)

# Keep bot alive and run it
keep_alive()
bot.run(TOKEN)
