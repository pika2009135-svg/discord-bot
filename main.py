import os
import re
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")  # <-- Render: set this env var in service settings
YOUR_ID = 658953333909749781  # ganti kalau perlu

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

last_time = None  # simpan masa sebelum

def extract_time(text):
    """Cari masa (HH:MM:SS) dalam text atau mm:ss"""
    # try HH:MM:SS in parentheses (embed footer style)
    m = re.search(r"\((\d{2}):(\d{2}):(\d{2})\)", text or "")
    if m:
        h, mm, s = map(int, m.groups())
        return h * 3600 + mm * 60 + s
    # try mm:ss like "38:07"
    m2 = re.search(r"(\d{1,2}):(\d{2})(?!:)", text or "")
    if m2:
        mm, s = map(int, m2.groups())
        return mm * 60 + s
    return None

@bot.event
async def on_ready():
    print(f"✅ {bot.user} sudah online!")

@bot.event
async def on_message(message):
    global last_time

    # ignore other users' normal messages; we want webhook/embed or bot messages
    # but allow commands (.r)
    # We'll still process embeds/content for bot/webhook messages
    current_time = None

    # 1) check message.content
    current_time = extract_time(message.content)

    # 2) check embed footer if present
    if current_time is None and message.embeds:
        for embed in message.embeds:
            footer_text = embed.footer.text if embed.footer else None
            current_time = extract_time(footer_text)
            if current_time is not None:
                break

    if current_time is not None:
        # if first time, just store
        if last_time is None:
            last_time = current_time
            return

        diff = abs(current_time - last_time)
        last_time = current_time

        mins, secs = divmod(diff, 60)
        if mins > 0:
            reply = f"{mins} min {secs} secs <@{YOUR_ID}>"
        else:
            reply = f"{secs} secs"

        await message.channel.send(reply)

    await bot.process_commands(message)

# .r reset command
@bot.command(name="r")
async def reset(ctx):
    global last_time
    last_time = None
    await ctx.send("⏱️ Timer sudah direset!")

bot.run(TOKEN)
