import datetime
import os
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# 1. Direct JPG Poster Image Creating Function
def create_birthday_poster_image(emp_name, emp_id, designation, output_path="birthday_poster.jpg"):
    img = Image.new('RGB', (1000, 1000), color=(15, 32, 67)) # Dark Blue Background
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 55)
        font_name = ImageFont.truetype("arial.ttf", 50)
        font_text = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font_title = font_name = font_text = ImageFont.load_default()

    draw.text((500, 150), "🎉 HAPPY BIRTHDAY! 🎉", fill=(255, 215, 0), font=font_title, anchor="mm")
    draw.text((500, 350), f"{emp_name}", fill=(255, 255, 255), font=font_name, anchor="mm")
    draw.text((500, 500), f"Role: {designation}  |  Emp ID: {emp_id}", fill=(200, 200, 200), font=font_text, anchor="mm")
    draw.text((500, 650), "Wishing you a fantastic year filled with success & happiness! 🚀", fill=(255, 255, 255), font=font_text, anchor="mm")

    img.save(output_path, quality=95)
    return output_path

# 2. Green API Config
API_HOST = "https://api.greenapi.com"
INSTANCE_ID = os.environ.get("GREEN_API_INSTANCE_ID", "710722767657").strip()
API_TOKEN = os.environ.get("GREEN_API_TOKEN", "89abe524e02344fbb6a2f75e1f8e8cc3f6cef40b430940aab7").strip()
TARGET_WHATSAPP = os.environ.get("TARGET_WHATSAPP_NUMBER", "916374708386@c.us").strip()

def check_green_api_state():
    """Green API Instance Active-ah irukkaa-nu Check panna"""
    url = f"{API_HOST}/waInstance{INSTANCE_ID}/getStateInstance/{API_TOKEN}"
    try:
        res = requests.get(url, timeout=15)
        print(f"📡 Green API Instance State Response: {res.status_code} - {res.text}")
        return res.json().get("stateInstance")
    except Exception as e:
        print(f"⚠️ Green API State Check Failed: {e}")
        return None

def send_whatsapp_media(file_path, caption):
    """Green API via Media Poster Send"""
    url = f"{API_HOST}/waInstance{INSTANCE_ID}/sendFileByUpload/{API_TOKEN}"
    payload = {'chatId': TARGET_WHATSAPP, 'caption': caption}
    
    with open(file_path, 'rb') as f:
        files = {'file': ('birthday_poster.jpg', f, 'image/jpeg')}
        response = requests.post(url, data=payload, files=files, timeout=30)
    return response

def send_whatsapp_text(message):
    """Media fail aanaal Fallback Text Message Send"""
    url = f"{API_HOST}/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
    payload = {'chatId': TARGET_WHATSAPP, 'message': message}
    return requests.post(url, json=payload, timeout=30)

# 3. Main Function
def main():
    # Green API QR Code / Auth Check
    state = check_green_api_state()
    if state != "authorized":
        print(f"⚠️ Warning: Green API State is '{state}'. Dashboard-la QR code connected-ah irukkaa-nu check pannunga.")

    SPREADSHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1kHnIgB05VDsJ-XqFdFtHkJkGG6_TUcx5wlbbk4XZgBk").strip()
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
    
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"❌ Google Sheet Load Error: {e}")
        raise e

    if 'DOB' not in df.columns:
        print(f"❌ Error: 'DOB' column missing. Columns: {list(df.columns)}")
        raise ValueError("DOB column missing")

    df['Parsed_DOB'] = pd.to_datetime(df['DOB'], format='mixed', errors='coerce')

    # Indian Standard Time (IST = UTC + 5:30)
    ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    today = datetime.datetime.now(ist_tz)
    
    print(f"📅 Today Date (IST): {today.strftime('%Y-%m-%d')}")

    birthday_list = df[
        (df['Parsed_DOB'].dt.month == today.month) & 
        (df['Parsed_DOB'].dt.day == today.day)
    ]

    if birthday_list.empty:
        print("ℹ️ Indru pirandhanaal kondadum paniyalaragal evarum illai.")
        return

    for _, row in birthday_list.iterrows():
        name = row.get('Name', 'Employee')
        emp_id = row.get('EmpID', 'N/A')
        desig = row.get('Designation', row.get('Department', 'Team Member'))
        phone = row.get('Phone', row.get('Phone No.', 'N/A'))

        print(f"🎉 Creating poster for {name}...")
        poster_file = create_birthday_poster_image(name, emp_id, desig)
        
        caption = (
            f"🎉 *TODAY'S BIRTHDAY ALERT!* 🎉\n\n"
            f"👤 *Name:* {name}\n"
            f"🆔 *Emp ID:* {emp_id}\n"
            f"💼 *Role:* {desig}\n"
            f"📞 *Phone:* {phone}"
        )
        
        print(f"🚀 Sending WhatsApp poster to {TARGET_WHATSAPP}...")
        res = send_whatsapp_media(poster_file, caption)
        print(f"📩 Green API Response Status: {res.status_code}")
        print(f"📩 Green API Response Text: {res.text}")

        if res.status_code == 200:
            print(f"✅ Success! Poster sent to {name}.")
        else:
            print(f"⚠️ Media send status {res.status_code}. Trying text message fallback...")
            text_res = send_whatsapp_text(caption)
            print(f"📩 Fallback Text Response: {text_res.status_code} - {text_res.text}")
            if text_res.status_code != 200:
                raise Exception(f"Green API Error: {res.status_code} - {res.text}")

if __name__ == "__main__":
    main()
