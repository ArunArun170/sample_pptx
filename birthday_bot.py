import datetime
import os
import requests
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# 1. Poster Slide Creating Function
def create_birthday_poster(emp_name, emp_id, designation, output_path="birthday_poster.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    slide = prs.slides.add_slide(prs.slide_layouts[6]) # Blank Slide

    # Background Color (Dark Royal Blue)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(15, 32, 67)

    # Title Box
    txBox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.add_paragraph()
    p.text = "🎉 HAPPY BIRTHDAY! 🎉"
    p.font.bold = True
    p.font.size = Pt(40)
    p.font.color.rgb = RGBColor(255, 215, 0) # Gold

    # Employee Name
    tx_name = slide.shapes.add_textbox(Inches(1), Inches(2.8), Inches(8), Inches(1.5))
    p_name = tx_name.text_frame.add_paragraph()
    p_name.text = f"{emp_name}"
    p_name.font.bold = True
    p_name.font.size = Pt(36)
    p_name.font.color.rgb = RGBColor(255, 255, 255)

    # Employee Details
    tx_details = slide.shapes.add_textbox(Inches(1), Inches(4.5), Inches(8), Inches(2))
    tf_details = tx_details.text_frame
    
    p_desig = tf_details.add_paragraph()
    p_desig.text = f"Role: {designation} | Emp ID: {emp_id}"
    p_desig.font.size = Pt(22)
    p_desig.font.color.rgb = RGBColor(200, 200, 200)

    p_wish = tf_details.add_paragraph()
    p_wish.text = "\nWishing you a fantastic year filled with success & happiness! 🚀"
    p_wish.font.size = Pt(18)
    p_wish.font.color.rgb = RGBColor(255, 255, 255)

    prs.save(output_path)
    return output_path

# 2. WhatsApp API Sending Function (Green API)
INSTANCE_ID = os.environ.get("GREEN_API_INSTANCE_ID")
API_TOKEN = os.environ.get("GREEN_API_TOKEN")
TARGET_WHATSAPP = os.environ.get("TARGET_WHATSAPP_NUMBER") # e.g. 919876543210@c.us

def send_whatsapp_media(file_path, caption):
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/sendFileByUpload/{API_TOKEN}"
    payload = {'chatId': TARGET_WHATSAPP, 'caption': caption}
    
    with open(file_path, 'rb') as f:
        files = [('file', (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.presentationml.presentation'))]
        response = requests.post(url, data=payload, files=files)
    return response

# 3. Main Logic
def main():
    # Excel or Google Sheet CSV Link
    EXCEL_FILE = "employees.xlsx" 
    
    if not os.path.exists(EXCEL_FILE):
        print("Excel file not found!")
        return

    df = pd.read_excel(EXCEL_FILE)
    df['DOB'] = pd.to_datetime(df['DOB'])

    today = datetime.datetime.now()
    
    # Matching Today's Birthdays
    birthday_list = df[
        (df['DOB'].dt.month == today.month) & 
        (df['DOB'].dt.day == today.day)
    ]

    if birthday_list.empty:
        print("No birthdays today.")
        return

    for _, row in birthday_list.iterrows():
        # Generate Slide Poster
        poster_file = create_birthday_poster(row['Name'], row['EmpID'], row['Designation'])
        
        caption = (
            f"🎉 *TODAY'S BIRTHDAY ALERT!* 🎉\n\n"
            f"👤 *Name:* {row['Name']}\n"
            f"🆔 *Emp ID:* {row['EmpID']}\n"
            f"💼 *Role:* {row['Designation']}\n"
            f"📞 *Phone:* {row['Phone']}"
        )
        
        # Send to WhatsApp
        res = send_whatsapp_media(poster_file, caption)
        print(f"Sent birthday wish for {row['Name']}: Status {res.status_code}")

if __name__ == "__main__":
    main()