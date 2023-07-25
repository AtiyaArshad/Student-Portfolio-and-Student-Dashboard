from flask import Flask, jsonify, request
import csv
import shutil
import os
import re
import pandas as pd

app = Flask(__name__)
app.debug = True

CSV_PATH = 'students.csv'
DOCUMENT_FOLDER = r"C:\Users\Javed\Documents\A X\PROJ\Pr_2\emasters_selection_letters\new" 
UUID_FOLDER = r"C:\Users\Javed\Documents\A X\PROJ\Pr_2\emasters_selection_letters\new\uuid"


def extract_numeric_digits(phone_no):
    return (re.search(r'\d{10}$', phone_no)).group()


@app.route('/update_data', methods=['POST'])
def get_student_data():
    data = request.get_json()

    if 'phone_no' in data:
        phone_no = extract_numeric_digits(data.get('phone_no'))
        response = retrieve_student_data(phone_no)
    elif 'old_phone' in data and 'phone' in data:
        old_phone, phone_no = map(extract_numeric_digits, (data.get('old_phone'), data.get('phone')))
        response = update_student_data(old_phone, phone_no, data)
    else:
        response = {"message": "Invalid input data.", "status": "error"}

    return jsonify(response)


def retrieve_student_data(phone_no):
    old_folder_path = os.path.join(DOCUMENT_FOLDER, phone_no)
    response = {"message": "You are not a valid user.","status": "failure"}
    try:
        df = pd.read_csv(CSV_PATH)
        row = df.loc[df['phone'].astype(str).str.replace(r'\D', '').str.endswith(phone_no)]

        if not row.empty and os.path.exists(old_folder_path):
            student_data = row.dropna(axis=1).to_dict(orient='records')[0]

            response = {"message": "Student data retrieved successfully.","student_data": student_data,"status": "success"}
        
    except Exception as e:
        response = {"message": str(e),"status": "error"}
    
    return response


def update_student_data(old_phone, phone, data): 
    response = {}
    try:
        df = pd.read_csv(CSV_PATH)
        mask = df['phone'].astype(str).str.replace(r'\D', '').str.endswith(old_phone)

        if old_phone != phone:
            create_folder(phone, old_phone)

        for key, value in data.items():
            if key != 'old_phone' and key in df.columns:
                df.loc[mask, key] = value

        df.to_csv(CSV_PATH, index=False)

        response = {"message": "Student data updated successfully.","status": "success"}

    except Exception as e:
        response = {"status": "Failure", "error": "Something went wrong"}
    return response


def create_folder(new_folder, old_folder):
    new_folder_path = os.path.join(DOCUMENT_FOLDER, new_folder)
    old_folder_path = os.path.join(DOCUMENT_FOLDER, old_folder)
    old_file_path = os.path.join(UUID_FOLDER, old_folder)
    new_file_path = os.path.join(UUID_FOLDER, new_folder)
    
    try:
        shutil.copytree(old_folder_path, new_folder_path)
        shutil.copy2(old_file_path, new_file_path)
            
    except Exception as e:
        print(f"Old folder does not exist or there is a problem in transferring folder content: {str(e)}")

if __name__ == '__main__':
    app.run()