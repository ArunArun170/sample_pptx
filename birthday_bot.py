import datetime
import os
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# 1. Dynamic Poster Generation (Birthday / Anniversary)
def create_event_poster(emp_name, emp_id, designation, event_type="BIRTHDAY", output_path="event_poster.jpg"):
    img = Image.new('RGB', (1000, 1000), color=(15, 32, 67)) # Dark Blue Background
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 50)
        font_name = ImageFont.truetype("arial.ttf", 55)
        font_text = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font_title = font_name = font_text = ImageFont.load_default()

    if event_type == "ANNIVERSARY":
        title_text = "💍 HAPPY ANNIVERSARY! 💍"
        wish_text = "Wishing you both a lifetime of love, happiness & togetherness! ❤️"
    else:
        title_text = "🎉 HAPPY BIRTHDAY! 🎉"
        wish_text = "Wishing you a fantastic year filled with success & happiness! 🚀"

    draw.text((500, 150), title_text, fill=(255, 215, 0), font=font_title, anchor="mm")
    draw.text((500, 350), f"{emp_name}", fill=(255, 255, 255), font=font_name, anchor="mm")
    draw.text((500, 500), f"Role: {designation}  |  Emp ID: {emp_id}", fill=(200, 200, 200), font=font_text, anchor="mm")
    draw.text((500, 650), wish_text, fill=(255, 255, 255), font=font_text, anchor="mm")

    img.save(output_path, quality=95)
    return output_path

# 2. Green API Config
MEDIA_URL = "https://7107.api.greenapi.com"
INSTANCE_ID = (os.environ.get("GREEN_API_INSTANCE_ID") or "710722767657").strip()
API_TOKEN = (os.environ.get("GREEN_API_TOKEN") or "89abe524e02344fbb6a2f75e1f8e8cc3f6cef40b430940aab7").strip()
TARGET_WHATSAPP = (os.environ.get("TARGET_WHATSAPP_NUMBER") or "916374708386@c.us").strip()

def send_whatsapp_media(file_path, caption):
    url = f"{MEDIA_URL}/waInstance{INSTANCE_ID}/sendFileByUpload/{API_TOKEN}"
    payload = {'chatId': TARGET_WHATSAPP, 'caption': caption}
    
    with open(file_path, 'rb') as f:
        files = [('file', (os.path.basename(file_path), f, 'image/jpeg'))]
        response = requests.post(url, data=payload, files=files, timeout=30)
    return response

# 3. Main Function
def main():
    SPREADSHEET_ID = (os.environ.get("GOOGLE_SHEET_ID") or "1kHnIgB05VDsJ-XqFdFtHkJkGG6_TUcx5wlbbk4XZgBk").strip()
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
    
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"❌ Google Sheet Read Error: {e}")
        raise e

    if 'DOB' in df.columns:
        df['Parsed_DOB'] = pd.to_datetime(df['DOB'], format='mixed', errors='coerce')
    if 'Anniversary' in df.columns:
        df['Parsed_Anniversary'] = pd.to_datetime(df['Anniversary'], format='mixed', errors='coerce')

    # Indian Timezone (IST)
    ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    today = datetime.datetime.now(ist_tz)
    print(f"📅 Today Date (IST): {today.strftime('%Y-%m-%d')}")

    # Check Birthday Matches
    if 'Parsed_DOB' in df.columns:
        bday_list = df[
            (df['Parsed_DOB'].dt.month == today.month) & 
            (df['Parsed_DOB'].dt.day == today.day)
        ]
        for _, row in bday_list.iterrows():
            name = row.get('Name', 'Employee')
            emp_id = row.get('EmpID', 'N/A')
            desig = row.get('Designation', row.get('Department', 'Team Member'))
            phone = row.get('Phone', row.get('Phone No.', 'N/A'))

            print(f"🎉 Creating Birthday poster for {name}...")
            poster_file = create_event_poster(name, emp_id, desig, event_type="BIRTHDAY")
            caption = f"🎉 *TODAY'S BIRTHDAY ALERT!* 🎉\n\n👤 *Name:* {name}\n🆔 *Emp ID:* {emp_id}\n💼 *Role:* {desig}\n📞 *Phone:* {phone}"
            
            res = send_whatsapp_media(poster_file, caption)
            if res.status_code == 200:
                print(f"✅ Success! Birthday Poster sent to {name}.")

    # Check Anniversary Matches
    if 'Parsed_Anniversary' in df.columns:
        anniv_list = df[
            (df['Parsed_Anniversary'].dt.month == today.month) & 
            (df['Parsed_Anniversary'].dt.day == today.day)
        ]
        for _, row in anniv_list.iterrows():
            name = row.get('Name', 'Employee')
            emp_id = row.get('EmpID', 'N/A')
            desig = row.get('Designation', row.get('Department', 'Team Member'))
            phone = row.get('Phone', row.get('Phone No.', 'N/A'))

            print(f"💍 Creating Anniversary poster for {name}...")
            poster_file = create_event_poster(name, emp_id, desig, event_type="ANNIVERSARY")
            caption = f"💍 *TODAY'S ANNIVERSARY ALERT!* 💍\n\n👤 *Name:* {name}\n🆔 *Emp ID:* {emp_id}\n💼 *Role:* {desig}\n📞 *Phone:* {phone}"
            
            res = send_whatsapp_media(poster_file, caption)
            if res.status_code == 200:
                print(f"✅ Success! Anniversary Poster sent to {name}.")

if __name__ == "__main__":
    main()