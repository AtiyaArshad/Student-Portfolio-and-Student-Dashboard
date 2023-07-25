from flask import Flask, render_template, jsonify, request
import pdfkit
from datetime import datetime
import os
import hashlib

app = Flask(__name__)
app.debug = True

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    program = data.get('program_file')
    data['date'] = datetime.now().strftime('%B %d, %Y')

    rendered_template = render_template( program + '.html', data=data)

    phone = str(data['Mobile']).split("-")[-1]
    uuid_path = "uuids/" + phone + ".txt"
    if not os.path.exists(uuid_path):
        response = {
            "message": "You are not a valid user.",
            "status": "error"
        }
        return jsonify(response)

    uuid_file = open(uuid_path)
    user_uuid = uuid_file.readline()
    uuid_file.close()

    filetype = data.get('filetype')
    filename = (user_uuid + "|" + filetype).encode()
    filename = hashlib.sha256(filename).hexdigest()
    documents_folder_path = program + "/" + phone

    output_path = os.path.join(documents_folder_path, filename + '.pdf')

    pdf = pdfkit.from_string(rendered_template, output_path, configuration=pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'))

    response = {
        "message": 'PDF created successfully',
        "pdf_path": output_path,
        "status": "success" 
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run()