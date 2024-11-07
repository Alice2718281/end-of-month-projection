document.getElementById('predict-btn').addEventListener('click', function() {
    var monthSelect = document.getElementById('month-select');
    var methodSelect = document.getElementById('method-select');
    var month = parseInt(monthSelect.value.split('-')[1]);  // Retain month selection
    var method = methodSelect.value;

    console.log("Month:", month, "Method:", method);

    // send the month and method to the server
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ month: month, method: method })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.image_url) {
            // display the image url returned by the server
            var img = new Image();
            img.src = data.image_url;
            img.alt = "Prediction Result";
            document.getElementById('result-container').innerHTML = '';  // Clear previous results
            document.getElementById('result-container').appendChild(img);
        } else {
            console.error('Error: No image URL returned.');
        }
    })
    .catch(error => console.error('Error in fetch request:', error));
});