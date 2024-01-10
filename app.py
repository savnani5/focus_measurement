import os
import uuid
import threading
from flask import Flask, render_template, request, jsonify
from sensor import Sensor, calculate_focus_score_sensor
from focus_score import calculate_focus_score_video

class FocusMeasurementApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = 'data/video'
        self.focus_scores_video = {}  # Dictionary to store focus scores with unique identifiers
        self.focus_scores_sensor = {}  # Dictionary to store focus scores with unique identifiers
        self.sensors = {}

        # Define route Handlers
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/upload_video', 'upload_video', self.upload_video, methods=['POST'])
        self.app.add_url_rule('/focus_score/<process_id>', 'get_focus_score', self.get_focus_score, methods=['GET'])
        self.app.add_url_rule('/start_processing', 'start_processing', self.start_processing, methods=['POST'])
        self.app.add_url_rule('/stop_processing', 'stop_processing', self.stop_processing, methods=['POST'])

    def run(self, **kwargs):
        self.app.run(**kwargs)

    def index(self):
        return render_template('index.html')

    def upload_video(self):
        process_id = request.form.get('processId')  # Extract process ID from form data
        if not process_id or process_id not in self.focus_scores_video:
            return jsonify({'error': 'Invalid or missing process ID'}), 400

        # self.sensors[process_id] = None # Initialize sensor for the user 
        video = request.files['video']
        video_path = os.path.join(self.app.config['UPLOAD_FOLDER'], f'user_{process_id}.avi')
        video.save(video_path)

        # Start processing in a background thread
        threading.Thread(target=self.process_video, args=(video_path, process_id)).start()
        return jsonify({'processId': process_id})


    def get_focus_score(self, process_id):
        if process_id in self.focus_scores_video and process_id in self.focus_scores_sensor:
            score_vid = self.focus_scores_video.get(process_id)
            score_sensor = self.focus_scores_sensor.get(process_id)
            score = round(((2*score_vid) + score_sensor)/3, 2)
            if score is not None:
                return jsonify({'focusScore': score})
            else:
                return jsonify({'status': 'processing'}), 202
        return jsonify({'error': 'Invalid process ID'}), 404


    # Route when user clicks start button
    def start_processing(self):
        # Generate unique process id for user
        process_id = self.generate_unique_process_id()
        self.focus_scores_video[process_id] = None  # Initialize with None
        self.focus_scores_sensor[process_id] = None

        # Address and sensor type hardcoded, but ideally will come from edge device
        sensor = Sensor(address = "192.168.4.31:8080", sensor_type="android.sensor.accelerometer")
        sensor.connect() # asynchronous call
        self.sensors[process_id] = sensor
        return jsonify({'message': 'Processing started', 'processId': process_id})

    # Route when user clicks stop button
    def stop_processing(self):
        data = request.get_json()
        process_id = data.get('processId') if data else None
        if not process_id or process_id not in self.sensors:
            return jsonify({'error': 'Invalid or missing process ID'}), 400
        
        sensor = self.sensors[process_id]
        if sensor:
            sensor_data = sensor.data  # Assuming 'data' is an attribute of Sensor
            threading.Thread(target=self.process_sensor_data, args=(sensor_data, process_id)).start()
            # del self.sensors[process_id]  # Remove the sensor instance from the dictionary
            return jsonify({'message': 'Processing stopped for process ID: ' + process_id} )
        else:
            return jsonify({'error': 'Sensor not found for the given process ID'}), 404

    # For each unique user 
    def generate_unique_process_id(self):
        return str(uuid.uuid4())

    def process_video(self, video_path, process_id):
        # Implement asynchronous video processing and focus score logic here
        focus_score_video = calculate_focus_score_video(video_path, process_id)  # Implement this function
        print(f"focus_score_video for PID: {process_id}", focus_score_video)
        self.focus_scores_video[process_id] = focus_score_video
    
    def process_sensor_data(self, sensor_data, process_id):
        focus_score_sensor = calculate_focus_score_sensor(sensor_data, process_id)
        print(f"focus_score_sensor for PID: {process_id} ", focus_score_sensor)
        self.focus_scores_sensor[process_id] = focus_score_sensor


if __name__ == '__main__':  
    app = FocusMeasurementApp().app
    app.run(debug=True)