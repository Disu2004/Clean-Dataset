from flask import Flask, render_template, request, send_file, after_this_request
import pandas as pd
import os
import tempfile

app = Flask(__name__)

def clean_csv(file_path):
    df = pd.read_csv(file_path)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    cleaned_file_path = os.path.join(tempfile.gettempdir(), "cleaned_" + os.path.basename(file_path))
    df.to_csv(cleaned_file_path, index=False)
    
    return cleaned_file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        cleaned_file_path = clean_csv(file_path)

        @after_this_request
        def remove_files(response):
            try:
                os.remove(file_path)
                os.remove(cleaned_file_path)
            except Exception as e:
                print(f"Error deleting files: {e}")
            return response

        return send_file(cleaned_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
