import logging
import threading

from flask import Flask, request, jsonify, render_template
import paho.mqtt.client as mqtt


class ColorPicker:
    def __init__(self):
        self.logger = self._setup_logger()

        self._is_mqtt_connected = False
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_disconnect  = self._on_mqtt_disconnect

        broker_ip = "192.168.88.210"  # TODO: Move to config
        broker_port = 1883
        self.logger.info(f"Connecting to MQTT broker on {broker_ip}:{broker_port} ...")
        self.mqtt_client.connect(broker_ip, broker_port, 60)

        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG) # TODO: Move to config
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def _on_mqtt_connect(self, client, userdata, flags, reason_code, properties):
        self.logger.info(f"Connected to MQTT broker with result code {reason_code}")
        self._is_mqtt_connected = True
        
    def _on_mqtt_disconnect(self, client, userdata, flags, reason_code, properties):
        self.logger.info(f"Disconnected from MQTT broker with result code {reason_code}")
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
            self.logger.info(f"Selected color is {color}")
            self.mqtt_client.publish("/esp32/set_rgb_color", color)
            return jsonify({"message": f"Selected color is {color}"})
        
        @self.app.route('/is_mqtt_connected', methods=['GET'])
        def is_mqtt_connected():
            return jsonify({"is_mqtt_connected": self._is_mqtt_connected})

    def run(self):
        threading.Thread(target=self.mqtt_client.loop_forever).start()
        self.app.run(debug=True)

color_picker = ColorPicker()

if __name__ == '__main__':
    color_picker.run()
