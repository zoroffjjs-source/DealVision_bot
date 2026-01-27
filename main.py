import logging
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# بياناتك من الصور السابقة
TELEGRAM_TOKEN = "8129202725:AAFksWTy7PXyn_tO_K9ycxzveOEam0iYXRA"
GEMINI_API_KEY = "AIzaSyCZHVuNdSWigF4O9mUgGaIUBVVJJYprOlU"
AMAZON_TAG = "chop07c-20"
AMAZON_DOMAIN = "www.amazon.com"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def search_amazon(query):
    search_url = f"https://{AMAZON_DOMAIN}/s?k={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    result = soup.find("div", {"data-component-type": "s-search-result"})
    if result:
        asin = result['data-asin']
        title = result.find("h2").text.strip()
        img = result.find("img")['src']
        link = f"https://{AMAZON_DOMAIN}/dp/{asin}?tag={AMAZON_TAG}"
        return {"title": title, "link": link, "image": img}
    return None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    await update.message.reply_text("🔎 Analyzing image...")
    contents = [{"mime_type": "image/jpeg", "data": bytes(image_bytes)}, "Identify this product, name and brand only."]
    response = model.generate_content(contents)
    data = search_amazon(response.text)
    if data:
        keyboard = [[InlineKeyboardButton("🛒 View on Amazon", url=data['link'])]]
        await update.message.reply_photo(photo=data['image'], caption=f"📦 {data['title']}", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u,c: u.message.reply_text("Welcome! Send a product photo.")))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
  
