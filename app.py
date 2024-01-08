from flask import Flask, render_template, request, jsonify
import threading
import os
import uuid
import time
from focus_score import calculate_focus_score

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload_data/'
focus_scores = {}  # Dictionary to store focus scores with unique identifiers

# Scalablility 
def generate_unique_process_id():
    return str(uuid.uuid4())

def process_video(video_path, process_id):
    # Implement your asynchronous video processing and focus score logic here
    focus_score = calculate_focus_score(video_path, process_id)  # Implement this function
    # focus_score = 85
    focus_scores[process_id] = focus_score


# def calculate_focus_score(video_path):
#     time.sleep(2)
#     return 100

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    # Generate unique process id
    process_id = generate_unique_process_id()  # Implement this function
    focus_scores[process_id] = None  # Initialize with None

    video = request.files['video']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f'user_{process_id}.mp4')
    video.save(video_path)

    # Start processing in a background thread
    threading.Thread(target=process_video, args=(video_path, process_id)).start()

    return jsonify({'processId': process_id})


@app.route('/focus_score/<process_id>', methods=['GET'])
def get_focus_score(process_id):
    if process_id in focus_scores:
        score = focus_scores.get(process_id)
        if score is not None:
            return jsonify({'focusScore': score})
        else:
            return jsonify({'status': 'processing'}), 202
    return jsonify({'error': 'Invalid process ID'}), 404



if __name__ == '__main__':
    app.run(debug=True)