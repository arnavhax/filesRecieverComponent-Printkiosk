# this is the webapp hosted on the cloud
from flask import Flask, jsonify, session, request, send_file
from zipfile import ZipFile
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_DIRECTORY = 'user_uploads'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.route('/startSession', methods=['POST'])
def start_session():
    if 'session_started' in session:
        return jsonify({'error': 'Session is already started.'})
    
    token_id = request.form.get('token_id')  # Using request.form to get data from POST request
    if token_id is None:
        return jsonify({'error': 'Token ID not provided.'})
    
    session['session_started'] = True
    session['token_id'] = token_id
    
    return jsonify({'message': 'Session started successfully.', 'token_id': token_id})

def delete_uploaded_files():
    # Delete all files from the user_uploads directory
    for filename in os.listdir(UPLOAD_DIRECTORY):
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

@app.route('/endSession', methods=['GET'])
def end_session():
    if 'session_started' in session:
        session.clear()
        delete_uploaded_files()  # Call the function to delete uploaded files
        return jsonify({'message': 'Session ended successfully. Uploaded files deleted.'}), 200
    else:
        return jsonify({'error': 'No session to end.'}), 400
    


@app.route('/upload/<token_id>', methods=['POST'])
def upload_files(token_id):
    if 'session_started' not in session or session['token_id'] != token_id:
        return jsonify({'error': 'Unauthorized access.'}), 401
    
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided.'}), 400
    
    uploaded_files = request.files.getlist('files')
    for file in uploaded_files:
        file.save(os.path.join(UPLOAD_DIRECTORY, file.filename))
    
    return jsonify({'message': 'Files uploaded successfully.'}), 200

@app.route('/download/<token_id>', methods=['GET'])
def download_files(token_id):
    if 'session_started' not in session or session['token_id'] != token_id:
        return jsonify({'error': 'Unauthorized access.'}), 401

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