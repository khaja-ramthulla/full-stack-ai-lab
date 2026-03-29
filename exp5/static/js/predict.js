// Example datasets
const examples = {
    1: { // Setosa
        sepal_length: 5.1,
        sepal_width: 3.5,
        petal_length: 1.4,
        petal_width: 0.2
    },
    2: { // Versicolor
        sepal_length: 5.7,
        sepal_width: 2.8,
        petal_length: 4.1,
        petal_width: 1.3
    },
    3: { // Virginica
        sepal_length: 6.7,
        sepal_width: 3.0,
        petal_length: 5.2,
        petal_width: 2.3
    }
};

// Fill example data
function fillExample(num) {
    const ex = examples[num];
    document.getElementById('sepal_length').value = ex.sepal_length;
    document.getElementById('sepal_width').value = ex.sepal_width;
    document.getElementById('petal_length').value = ex.petal_length;
    document.getElementById('petal_width').value = ex.petal_width;
}

// Handle form submission
document.getElementById('predictionForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    document.getElementById('result').style.display = 'none';
    document.getElementById('error').style.display = 'none';

    const features = [
        parseFloat(document.getElementById('sepal_length').value),
        parseFloat(document.getElementById('sepal_width').value),
        parseFloat(document.getElementById('petal_length').value),
        parseFloat(document.getElementById('petal_width').value)
    ];

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({features: features})
        });

        const data = await response.json();

        if (response.ok) {
            displayResult(data);
        } else {
            displayError(data.error);
        }

    } catch (err) {
        displayError('Server connection failed');
    }
});

// Display result
function displayResult(data) {
    document.getElementById('result').style.display = 'block';
    document.getElementById('predictedClass').textContent = data.prediction;

    // Probabilities
    const probBars = document.getElementById('probBars');
    probBars.innerHTML = '';

    for (const [cls, prob] of Object.entries(data.probabilities)) {
        probBars.innerHTML += `${cls}: ${(prob * 100).toFixed(2)}%<br>`;
    }

    // Input values
    const inputValues = document.getElementById('inputValues');
    inputValues.innerHTML = '';

    for (const [name, value] of Object.entries(data.input_features)) {
        inputValues.innerHTML += `${name}: ${value} cm<br>`;
    }
}

// Display error
function displayError(msg) {
    const errDiv = document.getElementById('error');
    errDiv.textContent = 'Error: ' + msg;
    errDiv.style.display = 'block';
}
