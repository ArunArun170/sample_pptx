import datetime
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from whatsapp_api_client_python import API

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

# 2. Main Function using Official Green API SDK
def main():
    instance_id = os.environ.get("GREEN_API_INSTANCE_ID", "710722767657").strip()
    api_token = os.environ.get("GREEN_API_TOKEN", "89abe524e02344fbb6a2f75e1f8e8cc3f6cef40b430940aab7").strip()
    target_whatsapp = os.environ.get("TARGET_WHATSAPP_NUMBER", "916374708386@c.us").strip()

    # Green API Official SDK Initialise
    greenAPI = API.GreenAPI(instance_id, api_token)

    # Check Instance status
    try:
        state_res = greenAPI.account.getStateInstance()
        print(f"📡 Green API State Response Code: {state_res.code}")
        print(f"📡 Green API State Data: {state_res.data}")
    except Exception as e:
        print(f"⚠️ State check warning: {e}")

    spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID", "1kHnIgB05VDsJ-XqFdFtHkJkGG6_TUcx5wlbbk4XZgBk").strip()
    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    
    try:
        df = pd.read_csv(sheet_url)
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"❌ Google Sheet Load Error: {e}")
        raise e

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
        
        print(f"🚀 Sending poster to {target_whatsapp}...")
        try:
            # SDK Official Method
            res = greenAPI.sending.sendFileByUpload(
                chatId=target_whatsapp,
                path=poster_file,
                fileName="birthday_poster.jpg",
                caption=caption
            )
            print(f"📩 Green API SDK Code: {res.code}")
            print(f"📩 Green API SDK Data: {res.data}")

            if res.code == 200:
                print(f"✅ Success! Poster sent to {name}.")
                success_count += 1
            else:
                print(f"❌ SDK Send Failed with Code: {res.code}")
        except Exception as e:
            print(f"❌ Exception sending media: {e}")

    if success_count == 0:
        raise Exception("Green API deliverability test failed. Check Green API Console QR connection.")

if __name__ == "__main__":
    main()
