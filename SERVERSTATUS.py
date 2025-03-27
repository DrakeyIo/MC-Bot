import requests
import time
from mcstatus import JavaServer

# Server details
SERVER_IP = "TideCleansers.aternos.me"
PORT = 26326  # No quotes for integer
WEBHOOK_URL = "https://discord.com/api/webhooks/1354763177161654364/6xrNzpS0P5F_ytMrIuoXwbOyJg5E-DnPJ36LJSFO06NGH6UFMmyiziGM8fi8Hi7mJFsw"

message_id = None  # Stores the Discord message ID

def get_server_status():
    """Fetch server status using mcstatus with a fallback method."""
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{PORT}")
        status = server.status()

        return {
            "status": "🟢 Online",
            "players": f"{status.players.online} / {status.players.max}",
            "motd": status.motd.formatted if hasattr(status.motd, "formatted") else "No MOTD",
            "version": status.version.name,
            "ping": f"{status.latency:.2f} ms",
        }

    except Exception:
        # Alternative API if mcstatus fails
        url = f"https://api.mcsrvstat.us/2/{SERVER_IP}"
        response = requests.get(url).json()
        
        if response.get("online"):
            return {
                "status": "🟢 Online",
                "players": f"{response['players']['online']} / {response['players']['max']}",
                "motd": response['motd']['clean'] if 'motd' in response else "No MOTD",
                "version": response['version'] if 'version' in response else "Unknown Version",
                "ping": "N/A",
            }
        else:
            return {"status": "🔴 Offline"}

def format_embed(status):
    """Format the server status into an embed message."""
    embed = {
        "title": "🌍 Minecraft Server Status",
        "color": 3066993 if "Online" in status["status"] else 15158332,
        "fields": [
            {"name": "🖥️ Server IP", "value": f"`{SERVER_IP}:{PORT}`", "inline": True},
            {"name": "📡 Status", "value": status["status"], "inline": True},
        ],
        "footer": {"text": "Last updated"},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if "players" in status:
        embed["fields"].append({"name": "👥 Players Online", "value": status["players"], "inline": True})
    if "motd" in status:
        embed["fields"].append({"name": "📢 Server MOTD", "value": f"```{status['motd']}```", "inline": False})
    if "version" in status:
        embed["fields"].append({"name": "🛠 Version", "value": status["version"], "inline": True})
    if "ping" in status:
        embed["fields"].append({"name": "📶 Ping", "value": status["ping"], "inline": True})

    return {"embeds": [embed]}

def send_initial_message():
    """Send the first message to Discord and get its message ID."""
    global message_id
    data = format_embed(get_server_status())
    response = requests.post(WEBHOOK_URL, json=data)
    
    if response.status_code == 200:
        message_id = response.json().get("id")
        print(f"Message sent successfully! ID: {message_id}")
    else:
        print(f"Failed to send initial message: {response.text}")

def update_message():
    """Edit the existing message to update the status."""
    global message_id
    if message_id is None:
        send_initial_message()  # Send the first message if it doesn't exist
        return

    data = format_embed(get_server_status())
    edit_url = f"{WEBHOOK_URL}/messages/{message_id}"
    response = requests.patch(edit_url, json=data)

    if response.status_code not in [200, 204]:
        print(f"Failed to update message: {response.text}")

# Start the loop
send_initial_message()  # Send the first message
while True:
    update_message()  # Update the existing message
    time.sleep(60)  # Updates every 1 minute (optimized for performance)
