import os
import shutil
import glob
import re
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
app.debug = True

certificate_folder = r"C:/Users/Javed/Documents/A X/PROJ/API/Details/Certi"
profile_folder = r"C:/Users/Javed/Documents/A X/PROJ/API/Details/Profile"
about_prog_folder = r"C:/Users/Javed/Documents/A X/PROJ/API/Details/About_program"
destination_folder = r"C:/Users/Javed/Documents/A X/PROJ/API/Details/Server"

def check_files(trainee_id, about_prog_image):
    
    certificate_file = glob.glob(os.path.join(certificate_folder, str(trainee_id) + ".*"))
    profile_file = glob.glob(os.path.join(profile_folder, str(trainee_id) + ".*"))
    about_prog_path = os.path.join(about_prog_folder, about_prog_image)
    server_image_path = os.path.join(destination_folder, about_prog_image)

    if not os.path.exists(server_image_path) and not os.path.exists(about_prog_path) or not (len(certificate_file) > 0) or not (len(profile_file) > 0):
        return False

    return True

def copy_files(trainee_id, about_prog_image):
    if not check_files(trainee_id, about_prog_image):
        return False

    destination_folder = r"C:/Users/Javed/Documents/A X/PROJ/API/Details/Server"
    os.makedirs(destination_folder, exist_ok=True)

    certificate_file = glob.glob(os.path.join(certificate_folder, str(trainee_id) + ".*"))

    profile_file = glob.glob(os.path.join(profile_folder, str(trainee_id) + ".*"))

    for pdf in certificate_file:
        shutil.copy(os.path.join(certificate_folder, pdf), destination_folder)

    for jpg in profile_file:
        shutil.copy(os.path.join(profile_folder, jpg), destination_folder)

    
    about_prog_path = os.path.join(about_prog_folder, about_prog_image)
    server_image_path = os.path.join(destination_folder, about_prog_image)

    if os.path.exists(about_prog_path):
        shutil.copy(about_prog_path, server_image_path)

    return True

def generate_trainee_data(opt):
    trainee_id = opt.get('trainee_id')
    about_prog_image = opt.get('about_prog_image')

    pattern = r'^Project(\d+)_title$'
    regex = re.compile(pattern)

    projects_description = {}
    projects_list = []

    for key, value in opt.items():
        match = regex.match(key)
        if match and value:
            project_num = match.group(1)
            desc_key = 'Project' + project_num + '_description'
            desc_value = opt.get(desc_key)
            if desc_value:
                projects_description[value] = desc_value
                projects_list.append(value)

    trainee_data = {
        "name": opt.get("name"),
        "trainee_id": trainee_id,
        "about_prog_image": about_prog_image,
        "designation": opt.get("designation"),
        "company_name": opt.get("company_name"),
        "program_code": opt.get("program_code"),
        "program_name": opt.get("program_name"),
        "cohort#": opt.get("cohort#"),
        "template_name": opt.get("template_name"),
        "projects_description": projects_description,
        "projects_list": projects_list
    }

    return trainee_data

def get_trainee_data(trainee_id):
    server_folder = r"C:/Users/Javed/Documents/A X/PROJ/API/Details/Server"
    trainee_file_path = os.path.join(server_folder, f"{trainee_id}.json")

    if not os.path.exists(trainee_file_path):
        return None

    with open(trainee_file_path, 'r') as trainee_file:
        trainee_data = json.load(trainee_file)

    return trainee_data

def modify_trainee_data(trainee_data):
    trainee_id = trainee_data.get('trainee_id')
    trainee_file_path = os.path.join(data_folder, f"{trainee_id}.json")

    if not os.path.exists(trainee_file_path):
        response = {
            "status": "Failure",
            "message": "Trainee data for trainee_id: {0} does not exist".format(trainee_id)
        }
        return jsonify(response), 404

    with open(trainee_file_path, 'w') as trainee_file:
        json.dump(trainee_data, trainee_file, indent=4)

    response = {
        "status": "success",
        "message": "Trainee data for trainee_id: {0} has been modified successfully".format(trainee_id)
    }
    return jsonify(response), 200

@app.route('/api/trainee_data/', methods=['POST', 'GET'])
def handle_trainee_data():
    opt = request.json
    trainee_id = opt.get('trainee_id')
    about_prog_image = opt.get('about_prog_image')
    copy = int(request.args.get('edit', 1))

    if trainee_id and about_prog_image:
        if copy == 1:
            if not copy_files(trainee_id, about_prog_image):
                response = {
                    "status": "Failure",
                    "message": "Portfolio for trainee_id: {0} is not generated".format(trainee_id)
                }
                return jsonify(response), 400

        trainee_data = generate_trainee_data(opt)

        server_folder = r"C:/Users/Javed/Documents/A X/PROJ/API/Details/Server"
        trainee_file_path = os.path.join(server_folder, f"{trainee_id}.json")

        with open(trainee_file_path, 'w') as trainee_file:
            json.dump(trainee_data, trainee_file, indent=4)

        response = {
            "status": "success",
            "message": "Portfolio for trainee_id: {0} is generated successfully".format(trainee_id)
        }
        return jsonify(response), 200

    elif trainee_id:
        trainee_data = get_trainee_data(trainee_id)

        if not trainee_data:
            response = {
                "status": "Failure",
                "message": "Trainee data for trainee_id: {0} does not exist".format(trainee_id)
            }
            return jsonify(response), 404

        return jsonify(trainee_data), 200

    else:
        response = {
            "status": "Failure",
            "message": "Invalid input"
        }
        return jsonify(response), 400


if __name__ == "__main__":
    app.run()