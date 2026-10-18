import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key"

EXCEL_FILE = "employees.xlsx"
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Excel File Initialization with DOB & Anniversary Columns
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['EmpID', 'Name', 'Course', 'Role', 'Status', 'DOB', 'Anniversary', 'PhotoPath', 'BgColor'])
        df.to_excel(EXCEL_FILE, index=False)

def read_data():
    init_excel()
    df = pd.read_excel(EXCEL_FILE).fillna('')
    for col in ['EmpID', 'Name', 'Course', 'Role', 'Status', 'DOB', 'Anniversary', 'PhotoPath', 'BgColor']:
        if col not in df.columns:
            df[col] = ''
    return df

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    df = read_data()
    records = df.to_dict(orient='records')
    return render_template('index.html', records=records)

@app.route('/save', methods=['POST'])
def save_record():
    original_emp_id = request.form.get('original_emp_id')
    emp_id = request.form.get('emp_id')
    name = request.form.get('name')
    course = request.form.get('course')
    role = request.form.get('role')
    status = request.form.get('status')
    dob = request.form.get('dob')
    anniversary = request.form.get('anniversary')
    bg_color = request.form.get('bg_color', '#ffffff')
    
    df = read_data()

    file = request.files.get('photo')
    filename = None
    if file and allowed_file(file.filename):
        s_filename = secure_filename(file.filename)
        filename = f"{emp_id}_{s_filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # EDIT Mode
    if original_emp_id:
        idx = df[df['EmpID'].astype(str) == str(original_emp_id)].index
        if not idx.empty:
            i = idx[0]
            df.at[i, 'EmpID'] = emp_id
            df.at[i, 'Name'] = name
            df.at[i, 'Course'] = course
            df.at[i, 'Role'] = role
            df.at[i, 'Status'] = status
            df.at[i, 'DOB'] = dob
            df.at[i, 'Anniversary'] = anniversary
            df.at[i, 'BgColor'] = bg_color
            if filename:
                df.at[i, 'PhotoPath'] = filename
            flash("விவரங்கள் வெற்றிகரமாகப் புதுப்பிக்கப்பட்டன (Updated)!")
    # ADD Mode
    else:
        if not filename:
            filename = 'default.jpg'
        new_row = {
            'EmpID': emp_id,
            'Name': name,
            'Course': course,
            'Role': role,
            'Status': status,
            'DOB': dob,
            'Anniversary': anniversary,
            'PhotoPath': filename,
            'BgColor': bg_color
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        flash("புதிய விவரங்கள் சேர்க்கப்பட்டன (Added)!")

    save_data(df)
    return redirect(url_for('index'))

@app.route('/delete/<emp_id>')
def delete_record(emp_id):
    df = read_data()
    df = df[df['EmpID'].astype(str) != str(emp_id)]
    save_data(df)
    flash("விவரம் நீக்கப்பட்டது (Deleted)!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)