# ═══════════════════════════════════════════════════════════════
#              L U X X Y   B O T   v1.0
#      Discord Bot untuk Luxxy Hub - Soreya Edition
# ═══════════════════════════════════════════════════════════════

import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# KONFIGURASI
# ═══════════════════════════════════════════════════════════════

TOKEN = os.getenv("DISCORD_TOKEN")
DATA_FILE = Path("data.json")

# Warna embed default (ungu Luxxy)
EMBED_COLOR = 0x9B00FF

# ═══════════════════════════════════════════════════════════════
# DATABASE SEDERHANA (JSON)
# ═══════════════════════════════════════════════════════════════

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"channels": {}, "stats": {}, "catches": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

DATA = load_data()

# ═══════════════════════════════════════════════════════════════
# SETUP BOT
# ═══════════════════════════════════════════════════════════════

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class LuxxyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        await self.tree.sync()
        print("[LuxxyBot] Slash commands synced!")

bot = LuxxyBot()

# ═══════════════════════════════════════════════════════════════
# EVENT: BOT READY
# ═══════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"═══════════════════════════════════════")
    print(f"  LUXXY BOT ONLINE!")
    print(f"  Logged in as: {bot.user}")
    print(f"  Guilds: {len(bot.guilds)}")
    print(f"═══════════════════════════════════════")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🎣 Luxxy Hub users"
        )
    )

# ═══════════════════════════════════════════════════════════════
# COMMAND: /ping
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="ping", description="Cek apakah bot masih hidup")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=EMBED_COLOR
    )
    embed.set_footer(text="Luxxy Bot v1.0")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════
# COMMAND: /setup channel
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="setup", description="Setup bot Luxxy")
@app_commands.describe(channel="Channel untuk notifikasi ikan")
@app_commands.default_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if channel is None:
        channel = interaction.channel
    
    guild_id = str(interaction.guild_id)
    DATA["channels"][guild_id] = channel.id
    save_data(DATA)
    
    embed = discord.Embed(
        title="✅ Setup Berhasil!",
        description=f"Notifikasi ikan akan dikirim ke {channel.mention}",
        color=0x00FF96
    )
    embed.add_field(
        name="🔗 Webhook URL",
        value=f"```\nhttps://{os.getenv('REPL_SLUG', 'luxxy-bot')}.{os.getenv('REPL_OWNER', 'user')}.repl.co/webhook\n```",
        inline=False
    )
    embed.add_field(
        name="📋 Cara Pakai",
        value="Copy URL di atas, paste ke menu **Settings → Webhook** di Luxxy Hub.",
        inline=False
    )
    embed.set_footer(text="Luxxy Bot v1.0")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════
# COMMAND: /stats
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="stats", description="Lihat statistik auto fishing")
async def stats(interaction: discord.Interaction):
    total_catch = len(DATA["catches"])
    total_weight = sum(c.get("weight", 0) for c in DATA["catches"])
    
    rarity_count = {}
    for catch in DATA["catches"]:
        rar = catch.get("rarity", "Common")
        rarity_count[rar] = rarity_count.get(rar, 0) + 1
    
    embed = discord.Embed(
        title="📊 Statistik Luxxy Hub",
        color=EMBED_COLOR
    )
    embed.add_field(name="🐟 Total Catch", value=str(total_catch), inline=True)
    embed.add_field(name="⚖️ Total Weight", value=f"{total_weight:.1f} kg", inline=True)
    embed.add_field(name="🎣 Session", value="Aktif" if total_catch > 0 else "Belum ada", inline=True)
    
    if rarity_count:
        rarity_text = "\n".join([f"**{k}**: {v}" for k, v in rarity_count.items()])
        embed.add_field(name="🏆 Rarity Breakdown", value=rarity_text, inline=False)
    
    embed.set_footer(text="Luxxy Bot v1.0")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════
# COMMAND: /leaderboard
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="leaderboard", description="Top 10 ikan terberat")
async def leaderboard(interaction: discord.Interaction):
    if not DATA["catches"]:
        await interaction.response.send_message("❌ Belum ada ikan yang tertangkap!", ephemeral=True)
        return
    
    top = sorted(DATA["catches"], key=lambda x: x.get("weight", 0), reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 Top 10 Ikan Terberat",
        color=0xFFD700
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    desc = ""
    for i, catch in enumerate(top):
        name = catch.get("name", "Unknown")
        weight = catch.get("weight", 0)
        rarity = catch.get("rarity", "Common")
        desc += f"{medals[i]} **{name}** — {weight:.1f}kg ({rarity})\n"
    
    embed.description = desc
    embed.set_footer(text="Luxxy Bot v1.0")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════
# COMMAND: /reset
# ═══════════════════════════════════════════════════════════════

@bot.tree.command(name="reset", description="Reset semua data statistik")
@app_commands.default_permissions(administrator=True)
async def reset(interaction: discord.Interaction):
    DATA["catches"] = []
    save_data(DATA)
    
    embed = discord.Embed(
        title="🔄 Data Direset",
        description="Semua data statistik sudah dihapus.",
        color=0xFF6060
    )
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════
# WEB SERVER UNTUK TERIMA DATA DARI ROBLOX
# ═══════════════════════════════════════════════════════════════

from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "🎣 Luxxy Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        
        # Simpan ke database
        DATA["catches"].append({
            "name": data.get("name", "Unknown"),
            "rarity": data.get("rarity", "Common"),
            "weight": float(data.get("weight", 0)),
            "zone": data.get("zone", "Unknown"),
            "time": datetime.datetime.now().isoformat()
        })
        save_data(DATA)
        
        # Kirim ke Discord
        if len(DATA["channels"]) > 0:
            channel_id = list(DATA["channels"].values())[0]
            channel = bot.get_channel(channel_id)
            
            if channel:
                rarity_colors = {
                    "Common": 0xB4B4B4, "UnCommon": 0x64FF64,
                    "Rare": 0x64B4FF, "Epic": 0xB464FF,
                    "Legendary": 0xFFB432, "Mythical": 0xFF64C8,
                    "Secret": 0xFF5050
                }
                
                embed = discord.Embed(
                    title="🎣 Ikan Tertangkap!",
                    color=rarity_colors.get(data.get("rarity"), EMBED_COLOR),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="🐟 Nama", value=data.get("name", "?"), inline=True)
                embed.add_field(name="⭐ Rarity", value=data.get("rarity", "?"), inline=True)
                embed.add_field(name="⚖️ Berat", value=f"{data.get('weight', 0)} kg", inline=True)
                embed.add_field(name="📍 Zona", value=data.get("zone", "?"), inline=True)
                embed.set_footer(text="Luxxy Bot v1.0")
                
                # Kirim secara async
                bot.loop.create_task(channel.send(embed=embed))
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"[Webhook Error] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_web_server():
    app.run(host="0.0.0.0", port=5000)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN tidak ditemukan!")
        print("Setup di Replit → Tools → Secrets → DISCORD_TOKEN")
        exit(1)
    
    # Jalankan web server di thread terpisah
    Thread(target=run_web_server, daemon=True).start()
    
    # Jalankan bot Discord
    print("[LuxxyBot] Starting...")
    bot.run(TOKEN)
