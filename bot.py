import os
import urllib.parse
import urllib.request
import re
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Kulcsok beolvasása a Render-ről
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Szia Noé! A felhős AI ágensed elindult. Írj egy feladatot, vagy kérj meg, hogy keressek egy zenét a YouTube-on!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # 1. Funkció: YouTube keresés
    if "zene" in user_text.lower() or "youtube" in user_text.lower() or "játszd le" in user_text.lower():
        await update.message.reply_text("Keresem a videót a YouTube-on...")
        try:
            # Keresési kifejezés URL formátumba alakítása
            query = urllib.parse.quote(user_text)
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + query)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            
            if video_ids:
                await update.message.reply_text(f"Itt a zene, amit kértél:\nhttps://www.youtube.com/watch?v={video_ids[0]}")
            else:
                await update.message.reply_text("Sajnos nem találtam videót.")
            return # Kilépünk, hogy ne válaszoljon a Gemini is rá
        except Exception as e:
            await update.message.reply_text("Hiba történt a YouTube keresés közben.")
            return

    # 2. Funkció: Normál AI beszélgetés
    await update.message.reply_text("Gondolkodom...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction="Egy segítőkész személyes AI asszisztens vagy. Beszélgess természetesen, és ha kódolásról van szó, adj tiszta és pontos megoldásokat."
            ),
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Hiba a Gemini API-val: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("A bot sikeresen elindult!")
    app.run_polling()
