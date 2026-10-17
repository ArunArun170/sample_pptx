import datetime
import os
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# 1. Direct JPG Poster Image Creating Function
def create_birthday_poster_image(emp_name, emp_id, designation, output_path="birthday_poster.jpg"):
    # 1000x1000 Square Poster Image
    img = Image.new('RGB', (1000, 1000), color=(15, 32, 67)) # Dark Blue Background
    draw = ImageDraw.Draw(img)
    
    # Text Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 55)
        font_name = ImageFont.truetype("arial.ttf", 50)
        font_text = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font_title = font_name = font_text = ImageFont.load_default()

    # Poster Content
    draw.text((500, 150), "🎉 HAPPY BIRTHDAY! 🎉", fill=(255, 215, 0), font=font_title, anchor="mm")
    draw.text((500, 350), f"{emp_name}", fill=(255, 255, 255), font=font_name, anchor="mm")
    draw.text((500, 500), f"Role: {designation}  |  Emp ID: {emp_id}", fill=(200, 200, 200), font=font_text, anchor="mm")
    draw.text((500, 650), "Wishing you a fantastic year filled with success & happiness! 🚀", fill=(255, 255, 255), font=font_text, anchor="mm")

    img.save(output_path, quality=95)
    return output_path

# 2. Green API Config (File upload-ku media.greenapi.com thaan use pannanum)
MEDIA_URL = os.environ.get("GREEN_API_MEDIA_URL", "https://7107.media.greenapi.com")
INSTANCE_ID = os.environ.get("GREEN_API_INSTANCE_ID", "710722767657")
API_TOKEN = os.environ.get("GREEN_API_TOKEN", "89abe524e02344fbb6a2f75e1f8e8cc3f6cef40b430940aab7")
TARGET_WHATSAPP = os.environ.get("TARGET_WHATSAPP_NUMBER", "916374708386@c.us")

def send_whatsapp_media(file_path, caption):
    url = f"{MEDIA_URL}/waInstance{INSTANCE_ID}/sendFileByUpload/{API_TOKEN}"
    payload = {'chatId': TARGET_WHATSAPP, 'caption': caption}
    
    with open(file_path, 'rb') as f:
        files = [('file', (os.path.basename(file_path), f, 'image/jpeg'))]
        response = requests.post(url, data=payload, files=files, timeout=30)
    return response

# 3. Main Function
def main():
    # Google Sheet ID
    SPREADSHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1kHnIgB05VDsJ-XqFdFtHkJkGG6_TUcx5wlbbk4XZgBk")
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
    
    try:
        df = pd.read_csv(SHEET_URL)
    except Exception as e:
        print(f"❌ Google Sheet Data Load Error: {e}")
        return

    df['DOB'] = pd.to_datetime(df['DOB'])
    today = datetime.datetime.now()

    birthday_list = df[
        (df['DOB'].dt.month == today.month) & 
        (df['DOB'].dt.day == today.day)
    ]

    if birthday_list.empty:
        print("ℹ️ Indru pirandhanaal kondadum paniyalaragal evarum illai.")
        return

    for _, row in birthday_list.iterrows():
        print(f"🎉 {row['Name']} -ukku Birthday JPG Poster uruvakkapadugiradhu...")
        poster_file = create_birthday_poster_image(row['Name'], row['EmpID'], row['Designation'])
        
        caption = (
            f"🎉 *TODAY'S BIRTHDAY ALERT!* 🎉\n\n"
            f"👤 *Name:* {row['Name']}\n"
            f"🆔 *Emp ID:* {row['EmpID']}\n"
            f"💼 *Role:* {row['Designation']}\n"
            f"📞 *Phone:* {row['Phone']}"
        )
        
        try:
            res = send_whatsapp_media(poster_file, caption)
            if res.status_code == 200:
                print(f"✅ Success! {row['Name']} -ukku WhatsApp Poster anuppappadtadhu.")
            else:
                print(f"❌ Failed Status ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
