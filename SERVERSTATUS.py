import discord
import os
import asyncio
import re
from discord.ext import commands
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

# Get environment variables from Secrets
TOKEN = os.environ["DISCORD_TOKEN"]
SERVER_IP = os.environ["SERVER_IP"]
SERVER_PORT = int(os.environ["SERVER_PORT"])
CHANNEL_ID = 1354762861116784791  # Replace with your actual Discord channel ID
SERVER_ADDRESS = f"{SERVER_IP}:{SERVER_PORT}"  # Full address

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def remove_minecraft_color_codes(text):
    """Remove Minecraft formatting codes (e.g., §4, §l) from text."""
    return re.sub(r"§[0-9A-FK-OR]", "", text, flags=re.IGNORECASE)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="🌍 Minecraft Server Status", color=discord.Color.orange())
        embed.add_field(name="⏳ Checking status...", value="Please wait...", inline=False)
        embed.set_footer(text="Last updated: Just now ⏳")
        status_msg = await channel.send(embed=embed)  # Send initial message
        bot.loop.create_task(update_status(status_msg))  # Start status update loop
    else:
        print("Channel not found. Make sure the bot has access to it.")

async def update_status(status_msg):
    while True:
        try:
            server = JavaServer.lookup(SERVER_ADDRESS)
            status = server.status()
            server_online = True
        except Exception:
            server_online = False

        if server_online:
            raw_motd = status.description if status.description else "No MOTD set"
            motd = remove_minecraft_color_codes(raw_motd)
            version = status.version.name if status.version else "Unknown"
            player_list = "\n".join([f"➡️ {player.name}" for player in status.players.sample]) if status.players.sample else "No players online"
            ping = round(status.latency, 1)  # Rounds ping to 1 decimal place
            
            embed = discord.Embed(title="🌍 Minecraft Server Status", color=discord.Color.green())
            embed.add_field(name="🔗 **Server Address**", value=f"`{SERVER_ADDRESS}`", inline=False)
            embed.add_field(name="🟢 **Server Status**", value="✅ Online", inline=False)
            embed.add_field(name="📌 **MOTD**", value=f"```{motd}```", inline=False)
            embed.add_field(name="🔢 **Server Version**", value=f"`{version}`", inline=True)
            embed.add_field(name="👥 **Players Online**", value=f"`{status.players.online}/{status.players.max}`", inline=True)
            embed.add_field(name="📡 **Ping**", value=f"`{ping}ms`", inline=True)
            embed.add_field(name="🎮 **Active Players**", value=f"```{player_list}```", inline=False)
            embed.set_footer(text="Last updated:")
            embed.timestamp = discord.utils.utcnow()
        else:
            embed = discord.Embed(title="🌍 Minecraft Server Status", color=discord.Color.red())
            embed.add_field(name="🔗 **Server Address**", value=f"`{SERVER_ADDRESS}`", inline=False)
            embed.add_field(name="🔴 **Server Status**", value="❌ Offline", inline=False)
            embed.add_field(name="📌 **MOTD**", value="N/A", inline=False)
            embed.add_field(name="🔢 **Server Version**", value="N/A", inline=True)
            embed.add_field(name="👥 **Players Online**", value="0/0", inline=True)
            embed.add_field(name="📡 **Ping**", value="N/A", inline=True)
            embed.add_field(name="🎮 **Active Players**", value="N/A", inline=False)
            embed.set_footer(text="Last checked:")
            embed.timestamp = discord.utils.utcnow()
        
        await status_msg.edit(embed=embed)  # Edit the original message
        await asyncio.sleep(30)  # Update every 30 seconds

# Keep bot alive and run it
keep_alive()
bot.run(TOKEN)
