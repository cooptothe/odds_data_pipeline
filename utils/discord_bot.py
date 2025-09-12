import discord
from dotenv import load_dotenv
load_dotenv()
import os
import subprocess


TOKEN = os.getenv("DISCORD_TOKEN")  # Put your bot token in .env
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
if CHANNEL_ID:
    CHANNEL_ID = int(CHANNEL_ID)

SPORT_KEYS = [
    "baseball_mlb", "basketball_nba", "basketball_wnba",
    "americanfootball_nfl", "americanfootball_ncaaf",
    "mma_mixed_martial_arts", "boxing_boxing", "hockey_nhl",
    "soccer_epl", "soccer_usa_mls", "soccer_italy_serie_a",
    "soccer_germany_bundesliga", "soccer_france_ligue_one",
    "soccer_mexico_ligamx", "tennis_atp_wimbledon", "tennis_wta_wimbledon", "upcoming"
]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Discord bot logged in as {client.user}")

@client.event
async def on_message(message):
    print(f"Received message: {message.content} in channel {message.channel.id}")
    if message.author == client.user:
        return

    if CHANNEL_ID and message.channel.id != int(CHANNEL_ID):
        return

    if message.content.startswith("!ev"):
        parts = message.content.split()
        if len(parts) < 2 or len(parts) > 3:
            await message.channel.send("Usage: `!ev <sport_key> [bankroll]`\nExample: `!ev baseball_mlb 250`")
            return

        sport_key = parts[1].strip().lower()
        if sport_key not in SPORT_KEYS:
            await message.channel.send(f"Invalid sport key. Valid keys:\n" + ", ".join(SPORT_KEYS))
            return

        bankroll = parts[2] if len(parts) == 3 else "100"

        await message.channel.send(
            f"🔄 Running EV analysis for `{sport_key}` with bankroll ${bankroll}. Please wait..."
        )
        try:
            # Run calculate_ev.py directly; it will send Discord alerts via webhook
            result = subprocess.run(
                [
                    "python", "-m", "analysis.calculate_ev",
                    "--sport", sport_key,
                    "--bankroll", bankroll
                ],
                capture_output=True, text=True, timeout=300,
                cwd=os.path.abspath(os.path.dirname(__file__) + "/..")
            )
            if result.returncode == 0:
                await message.channel.send(
                    f"✅ EV calculation complete for `{sport_key}` with bankroll ${bankroll}."
                )
            else:
                await message.channel.send(f"❌ Error calculating EV:\n{result.stderr}")
        except Exception as e:
            await message.channel.send(f"❌ Exception: {e}")

client.run(TOKEN)