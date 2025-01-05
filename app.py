from flask import Flask, request, jsonify, render_template, send_from_directory
import paho.mqtt.client as mqtt

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except:
    client = mqtt.Client()

client.connect("192.168.88.210", 1883, 60)
app = Flask(__name__)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-color', methods=['POST'])
def submit_color():
    data = request.json
    color = data.get("hex", "#000000")
    color = color.lstrip("#")
    client.publish("/esp32/set_rgb_color", color)
    print(color)
    return jsonify({"message": f"Selected color is {color}"})

if __name__ == '__main__':
    app.run(debug=True)
