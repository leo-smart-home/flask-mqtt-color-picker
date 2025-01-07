import logging
import threading
import time
from flask import Flask, request, jsonify, render_template
import paho.mqtt.client as mqtt

MQTT_BROKER_IP = "192.168.88.210"
MQTT_BROKER_PORT = 1883

ESP_CONNECTION_STATUS_TOPIC = "/esp32/ping"
ESP_CONNECTION_STATUS_TIMEOUT = 1.0

class ColorPicker:
    def __init__(self):
        self._is_mqtt_connected = False
        self._is_esp_connected = False
        self._last_esp_ping_time = time.perf_counter()

        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT, 60)
        self.mqtt_client.subscribe(ESP_CONNECTION_STATUS_TOPIC)

        self._esp_timeout_thread = threading.Thread(target=self._update_esp_connection_status, daemon=True)
        self._esp_timeout_thread.start()

        self.app = Flask(__name__)
        self._setup_routes()

    def _update_esp_connection_status(self):
        while True:
            if time.perf_counter() - self._last_esp_ping_time > 1.0:
                self._is_esp_connected = False
            time.sleep(0.1)

    def _on_mqtt_message(self, client, userdata, message):
        topic = message.topic
        # payload = message.payload.decode("utf-8")

        if topic == ESP_CONNECTION_STATUS_TOPIC:
            self._is_esp_connected = True
            self._last_esp_ping_time = time.perf_counter()
    
    def _on_mqtt_connect(self, *_):
        self._is_mqtt_connected = True
        
    def _on_mqtt_disconnect(self, *_):
        self._is_mqtt_connected = False

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/submit_color', methods=['POST'])
        def submit_color():
            data = request.json
            color = data.get("hex", "#000000")
            color = color.lstrip("#")
            self.mqtt_client.publish("/esp32/set_rgb_color", color)
            return jsonify({"message": f"Selected color is {color}"})
        
        @self.app.route('/is_mqtt_connected', methods=['GET'])
        def is_mqtt_connected():
            return jsonify({"is_mqtt_connected": self._is_mqtt_connected})

        @self.app.route('/is_esp_connected', methods=['GET'])
        def is_esp_connected():
            return jsonify({"is_esp_connected": self._is_esp_connected})

    def run(self, host: str):
        threading.Thread(target=self.mqtt_client.loop_forever).start()
        self.app.run(host=host, debug=True)


if __name__ == '__main__':
    color_picker = ColorPicker()
    color_picker.run(host="0.0.0.0")
