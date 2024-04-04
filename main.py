from flask import Flask, jsonify, session, request, send_file
from zipfile import ZipFile
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_DIRECTORY = 'user_uploads'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

def delete_uploaded_files():
    # Delete all files from the user_uploads directory
    for filename in os.listdir(UPLOAD_DIRECTORY):
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

@app.route('/startSession', methods=['POST'])
def start_session():
    # Start a session for the kiosk
    session['session_started'] = True
    return jsonify({'message': 'Session started successfully.'}), 200

@app.route('/endSession', methods=['GET'])
def end_session():
    # Clear the session data
    session.clear()
    delete_uploaded_files()  # Call the function to delete uploaded files
    return jsonify({'message': 'Session ended successfully. Uploaded files deleted.', 'status_code': '200'})

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided.'}), 400
    
    uploaded_files = request.files.getlist('files')
    for file in uploaded_files:
        file.save(os.path.join(UPLOAD_DIRECTORY, file.filename))
    
    return jsonify({'message': 'Files uploaded successfully.'}), 200

@app.route('/download', methods=['GET'])
def download_files():
    # Get a list of all files in the directory
    all_files = os.listdir(UPLOAD_DIRECTORY)

    # Check if any files exist in the directory
    if not all_files:
        return jsonify({'error': 'No files to download.'}), 404

    # Create a zip archive containing all files
    zip_path = 'files.zip'
    with ZipFile(zip_path, 'w') as zip_file:
        for file in all_files:
            file_path = os.path.join(UPLOAD_DIRECTORY, file)
            zip_file.write(file_path, file)

    # Serve the zip archive
    try:
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Error downloading files: {str(e)}'}), 500
    finally:
        # Delete the zip archive after serving
        os.remove(zip_path)

if __name__ == '__main__':
    app.run(debug=True)
