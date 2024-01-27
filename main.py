from flask import Flask, request, jsonify, send_from_directory
import os
from urllib.parse import urlparse, parse_qs
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#----------------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'string' not in request.form:
        return jsonify({'error': 'Missing file or string parameter'}), 400

    file = request.files['file']
    string_to_find = request.form['string'].lower()

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
            file_content = f.read()

        metadata = {
            'length_of_whole_text': len(file_content),
            'amount_of_alphanumeric_symbols': sum(c.isalnum() for c in file_content),
            'number_of_occurrences': file_content.lower().count(string_to_find)
        }
        return jsonify(metadata), 200


#----------------------------------------------------------
@app.route('/parse_url', methods=['POST', 'GET'])
def parse_url():
    url = request.form.get('url')
    try:
        parsed_url = urlparse(url)
        query_p = parse_qs(parsed_url.query)

        output = f"It has {parsed_url.scheme} protocol,\n" \
                   f"Domain is '{parsed_url.netloc}',\n" \
                   f"The path to the resource has {len(parsed_url.path.split('/')) - 1} steps - {', '.join(parsed_url.path.split('/')[1:])},\n" \
                   f"Query parameters ({len(query_p)}) are present: {query_p}" if query_p else ""
        return jsonify({'result': output}), 200
    except Exception as e:
        return jsonify({'error': f'Error parsing URL: {str(e)}'}), 400


#----------------------------------------------------------
@app.route('/images/<path:image_path>', methods=['GET'])
def get_image(image_path):
    image_folder = 'images'
    image_path = os.path.join(image_folder, image_path)

    if os.path.exists(image_path):
        return jsonify({'status': 200, 'message': 'Image exists'}), 200
    else:
        return jsonify({'status': 404, 'message': 'Image not found'}), 404


#----------------------------------------------------------
@app.route('/')
def docs():
    return send_from_directory('.', 'documentation.json', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
