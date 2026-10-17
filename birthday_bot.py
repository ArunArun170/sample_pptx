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

# 2. Main Function
def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    })

    api_host = "https://api.greenapi.com"
    instance_id = os.environ.get("GREEN_API_INSTANCE_ID", "710722767657").strip()
    api_token = os.environ.get("GREEN_API_TOKEN", "89abe524e02344fbb6a2f75e1f8e8cc3f6cef40b430940aab7").strip()
    target_whatsapp = os.environ.get("TARGET_WHATSAPP_NUMBER", "916374708386@c.us").strip()

    # Instance state check
    state_url = f"{api_host}/waInstance{instance_id}/getStateInstance/{api_token}"
    try:
        st_res = session.get(state_url, timeout=20)
        print(f"📡 Green API State Status Code: {st_res.status_code}")
        print(f"📡 Green API State Text: {st_res.text[:200]}")
    except Exception as e:
        print(f"⚠️ State Check Error: {e}")

    spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID", "1kHnIgB05VDsJ-XqFdFtHkJkGG6_TUcx5wlbbk4XZgBk").strip()
    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"❌ Google Sheet Load Error: {e}")
        raise e

    df['Parsed_DOB'] = pd.to_datetime(df['DOB'], format='mixed', errors='coerce')

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

    success_count = 0
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
        
        send_url = f"{api_host}/waInstance{instance_id}/sendFileByUpload/{api_token}"
        payload = {'chatId': target_whatsapp, 'caption': caption}
        
        print(f"🚀 Sending poster to {target_whatsapp}...")
        try:
            with open(poster_file, 'rb') as f:
                files = {'file': ('birthday_poster.jpg', f, 'image/jpeg')}
                res = session.post(send_url, data=payload, files=files, timeout=30)
                print(f"📩 Send Status Code: {res.status_code}")
                print(f"📩 Send Response Body: {res.text[:300]}")
                if res.status_code == 200:
                    print(f"✅ Success! Poster sent to {name}.")
                    success_count += 1
                else:
                    print(f"❌ API Response Failed with Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Exception sending media: {e}")

    if success_count == 0:
        raise Exception("Green API deliverability test failed. Check Instance ID/Token state.")

if __name__ == "__main__":
    main()
