var colorPicker = new iro.ColorPicker(".colorPicker", {
    width: 280,
    color: "rgb(255, 255, 255)",
    borderWidth: 1,
    borderColor: "#fff"
});

var values = document.getElementById("values");
var isMouseDown = false;

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

hexInput.addEventListener('change', function () {
    colorPicker.color.hexString = this.value;
});

function updateValues(color) {
    values.innerHTML = [
        "hex: " + color.hexString,
        "rgb: " + color.rgbString
    ].join("<br>");
}

function submitColor(color) {
    const colorData = {
        hex: color.hexString,
        rgb: color.rgb
    };

    fetch("/submit-color", {
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






