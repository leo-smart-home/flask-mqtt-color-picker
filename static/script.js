var colorPicker = new iro.ColorPicker(".colorPicker", {
    width: 280,
    color: "rgb(255, 255, 255)",
    borderWidth: 1,
    borderColor: "#fff"
});

var values = document.getElementById("values");
var isMouseDown = false;
var mqttStatusValue = document.getElementById("mqtt-status-value");
var espStatusValue = document.getElementById("esp-status-value");

document.addEventListener("mousedown", function () {
    isMouseDown = true;
});

document.addEventListener("mouseup", function () {
    isMouseDown = false;
    updateValues(colorPicker.color);
});

colorPicker.on(["color:init", "color:change"], function (color) {
    // if (!isMouseDown) {
        updateValues(color);
        submitColor(color);
    // }
});

setInterval(updateMqttStatus, 1000);
setInterval(updateEsp32Status, 1000);

function updateValues(color) {
    values.innerHTML = [
        color.hexString,
        // "rgb: " + color.rgbString
    ].join("<br>");
    values.style.color = color.hexString;
}

function submitColor(color) {
    const colorData = {
        hex: color.hexString,
        rgb: color.rgb
    };

    fetch("/submit_color", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(colorData)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to submit color: " + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log("Color submitted successfully:", data);
        })
        .catch(error => {
            console.error("Error submitting color:", error);
        });
}

function updateMqttStatus() {
    fetch("/is_mqtt_connected")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch MQTT status: " + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log("MQTT status:", data);
            if (data.is_mqtt_connected) {
                mqttStatusValue.textContent = "Connected";
                mqttStatusValue.style.color = "green";
            } else {
                mqttStatusValue.textContent = "Disconnected";
                mqttStatusValue.style.color = "red";
            }
        })
        .catch(error => {
            console.error("Error fetching MQTT status:", error);
            mqttStatusValue.textContent = "Error fetching status";
            mqttStatusValue.style.color = "gray";
        });
}

function updateEsp32Status() {
    fetch("/is_esp_connected")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch ESP32 status: " + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log("ESP32 status:", data);
            if (data.is_esp_connected) {
                espStatusValue.textContent = "Connected";
                espStatusValue.style.color = "green";
            } else {
                espStatusValue.textContent = "Disconnected";
                espStatusValue.style.color = "red";
            }
        })
        .catch(error => {
            console.error("Error fetching ESP32 status:", error);
            espStatusValue.textContent = "Error fetching status";
            espStatusValue.style.color = "gray";
        });
}
