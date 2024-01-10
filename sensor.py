import os
import websocket
import json
import csv
import math
import threading
import numpy as np
import matplotlib.pyplot as plt

class Sensor:
    def __init__(self, address, sensor_type):
        self.address = address
        self.sensor_type = sensor_type
        self.data = []
        self.time_data = []

    # called each time when sensor data is recieved
    def on_message(self, ws, message):
        values = json.loads(message)['values']
        timestamp = json.loads(message)['timestamp']

        self.data.append(values)
        self.time_data.append(float(timestamp/1000000))

    def on_error(self, ws, error):
        print("error occurred")
        print(error)

    def on_close(self, ws, close_code, reason):
        print("connection close")
        print("close code : ", close_code)
        print("reason : ", reason  )

    def on_open(self, ws):
        print(f"connected to : {self.address}")

    # Call this method on seperate Thread
    def make_websocket_connection(self):
        ws = websocket.WebSocketApp(f"ws://{self.address}/sensor/connect?type={self.sensor_type}",
                                on_open=self.on_open,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)

        # blocking call
        ws.run_forever() 
    
    # make connection and start recieving data on sperate thread
    def connect(self):
        self.thread = threading.Thread(target=self.make_websocket_connection)
        self.thread.start()   

    def stop_connection(self):
        self.thread._Thread_stop()       


def calculate_focus_score_sensor(data, process_id, threshold=0.5):
    print("Calculating Focus Score from Sensor data")
    csv_out = os.path.join("data", "sensor", f"user_{process_id}.csv")
    # Write data to csv
    with open(csv_out, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'z'])
        writer.writerows(data)
    
    # Plot and Save the data graph
    plot_save_data(data, process_id)

    magnitudes = [calculate_magnitude(point) for point in data]
    movements = []
    for i in range(1, len(magnitudes)):
        if abs(magnitudes[i] - magnitudes[i - 1]) > threshold:
            movements.append((i, magnitudes[i]))
    
    return round((len(magnitudes) - len(movements))*100/len(magnitudes), 2)

def calculate_magnitude(acceleration):
    x, y, z = acceleration
    return math.sqrt(x**2 + y**2 + z**2)

def plot_save_data(data, process_id):
    np_data = np.array(data)
    x = np_data[:, 0]
    y = np_data[:, 1]
    z = np_data[:, 2]

    # Time or sample points (assuming each data point is a separate time unit)
    t = np.arange(len(np_data))

    # Plotting x, y, and z
    plt.figure(figsize=(12, 8))

    # Plot x
    plt.subplot(3, 1, 1)
    plt.plot(t, x, label='X-axis')
    plt.title('Accelerometer Data')
    plt.ylabel('X acceleration')
    plt.legend()

    # Plot y
    plt.subplot(3, 1, 2)
    plt.plot(t, y, color='orange', label='Y-axis')
    plt.ylabel('Y acceleration')
    plt.legend()

    # Plot z
    plt.subplot(3, 1, 3)
    plt.plot(t, z, color='green', label='Z-axis')
    plt.xlabel('Time (or samples)')
    plt.ylabel('Z acceleration')
    plt.legend()

    # Adjust layout and save the figure
    plt.tight_layout()
    plt.savefig(os.path.join("analysis", "sensor", f'accelerometer_data_{process_id}.png'))
    # plt.show()

if __name__=="__main__":
    dummy = [[0.011964113, 0.12622139, 9.945767], [0.0047856453, 0.12203395, 9.940384], [0.010169496, 0.119042926, 9.942777], [-0.00059820566, 0.13220344, 9.944571], [0.013160525, 0.12023934, 9.939187], [0.013160525, 0.1268196, 9.945767], [0.010169496, 0.12502499, 9.938589], [0.010169496, 0.13459627, 9.94158], [0.010169496, 0.1268196, 9.93799], [0.008374879, 0.1268196, 9.942178], [0.017347964, 0.13220344, 9.942178], [0.011365907, 0.12622139, 9.942178], [0.010767702, 0.12801601, 9.945169], [0.008374879, 0.12801601, 9.942178], [0.010169496, 0.1268196, 9.94158], [0.016749758, 0.13280165, 9.939785], [0.0077766734, 0.123828575, 9.939785], [0.013160525, 0.13998012, 9.945169], [0.0023928226, 0.12203395, 9.935597], [0.01794617, 0.13998012, 9.942777], [0.0065802624, 0.11784652, 9.940982], [0.014955142, 0.12921242, 9.942777], [0.008973085, 0.11844472, 9.938589], [0.008973085, 0.11964113, 9.940982], [0.010767702, 0.12502499, 9.940982], [0.18005991, -0.4001996, 10.2107725], [2.9306095, -0.6436693, 10.517652], [-0.34337005, 0.35413775, 10.904691], [-4.6055856, 4.316652, 1.2550355], [-1.9860427, 4.2071805, 9.52164], [0.14237295, 6.003592, 8.438289], [-0.1160519, 6.61436, 6.3924255], [0.26859435, 6.594021, 7.7240314], [-0.06520442, 6.3254266, 7.2963142], [-0.0017946169, 6.094519, 7.973483], [0.051445685, 6.0101724, 7.865806], [0.18664017, 6.1698933, 7.470392], [0.32422748, 6.2009997, 7.7533436], [0.357727, 6.1250277, 7.6797643], [0.32004002, 6.035297, 7.886145], [0.32183465, 6.033502, 7.8059855], [0.33499518, 6.003592, 7.806584], [0.55812585, 6.8763742, 8.015956], [-0.8279166, 7.132406, 5.758926], [-8.476574, 4.7676992, 3.6699917], [-3.5042887, 6.931409, 3.565904], [-2.0817556, 3.5988052, 6.701698], [-0.72382885, 0.19740787, 12.055638], [0.6011967, -0.53659046, 10.479366], [0.1363909, -0.21296121, 9.972089], [0.005383851, 0.12502499, 9.931411], [0.0011964113, 0.13280165, 9.936794], [0.0029910284, 0.12203395, 9.936196], [0.0071784677, 0.13220344, 9.939785], [0.0011964113, 0.1274178, 9.935597], [0.0011964113, 0.13280165, 9.9344015], [0.0, 0.12622139, 9.933205], [0.0041874396, 0.12981063, 9.934999], [0.0017946169, 0.12861422, 9.937392], [0.005383851, 0.12083755, 9.933804], [0.0011964113, 0.1274178, 9.93799], [-0.00059820566, 0.12263216, 9.935597], [0.0011964113, 0.13160525, 9.933205], [-0.0017946169, 0.12622139, 9.940384], [0.0035892338, 0.12921242, 9.933205], [0.04127619, 0.14476576, 9.926026], [1.1509477, 0.12323037, 10.381859], [3.6628132, -0.81236327, 11.171491], [-3.4366915, 2.8205397, 6.2488565], [-3.5970106, 4.438686, 7.673184], [0.6478567, 5.144569, 6.8039913], [1.0815558, 6.4905314, 8.516056], [0.07776674, 6.1304116, 7.225128], [0.34516466, 6.3050876, 7.899306], [0.29072794, 6.206982, 7.283154], [0.40498522, 6.5365934, 7.7629147], [-0.04426722, 6.765706, 6.4845495], [-2.0656042, 7.088139, 7.2957163], [-5.9096737, 7.0863442, 4.569693], [1.2993027, 5.413761, 3.6951163], [-0.95413804, 1.189831, 11.602797], [-0.2727818, -0.15373886, 10.655837], [0.695115, -0.27517462, 10.037891], [0.22851457, -0.37387854, 9.876375], [0.18484555, 0.032303106, 10.263414], [0.0059820567, 0.12981063, 9.921839], [0.0017946169, 0.1363909, 9.940982], [0.0029910284, 0.12861422, 9.9344015], [0.0023928226, 0.13040884, 9.933804], [0.0017946169, 0.12861422, 9.940384], [0.00059820566, 0.12861422, 9.938589], [0.0041874396, 0.13280165, 9.931411], [0.0029910284, 0.13339986, 9.936794], [0.0041874396, 0.12622139, 9.936196], [0.005383851, 0.13280165, 9.937392]]
    print(calculate_focus_score_sensor(dummy, process_id="123"))