document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const resultDiv = document.getElementById('result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        // Convert string values to numbers for numeric fields
        const numericFields = ['CHILDREN', 'Annual_income', 'Birthday_count', 'Employed_days', 'Family_Members'];
        numericFields.forEach(field => {
            data[field] = parseFloat(data[field]);
        });

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            resultDiv.innerHTML = `
                <h2>Prediction Result</h2>
                <p>Prediction: ${result.prediction}</p>
                <p>Probability of approval: ${(result.probability_approved * 100).toFixed(2)}%</p>
                <p>Probability of rejection: ${(result.probability_rejected * 100).toFixed(2)}%</p>
            `;
            resultDiv.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            resultDiv.innerHTML = `<p>An error occurred: ${error.message}</p>`;
            resultDiv.style.display = 'block';
        }
    });
});