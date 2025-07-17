document.getElementById('calculateBtn').addEventListener('click', calculateStatistics);

async function calculateStatistics() {
    const inputElement = document.getElementById('dataInput');
    const errorElement = document.getElementById('inputError');
    const resultsDiv = document.getElementById('results');
    
    // Clear previous errors and hide results
    errorElement.textContent = '';
    errorElement.style.display = 'none';
    resultsDiv.style.display = 'none';
    
    // Get and clean input
    const input = inputElement.value.trim();
    
    if (!input) {
        errorElement.textContent = 'Please enter some data';
        errorElement.style.display = 'block';
        return;
    }
    
    try {
        // Prepare data for API
        const formData = {
            data: input
        };

        // API Request
        const response = await fetch('/calculate_statistics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || 'Calculation failed');
        }
        
        // Display results
        const result = await response.json();
        
        // Update basic results
        document.getElementById('dataCount').textContent = result.dataCount;
        document.getElementById('meanResult').textContent = result.mean;
        document.getElementById('varianceResult').textContent = result.variance;
        document.getElementById('stdDevResult').textContent = result.stdDev;
        document.getElementById('sortedData').textContent = result.sortedData.join(', ');

        // Update your existing JavaScript to include this modification
        if (result.steps) {
            const stepsContainer = document.createElement('ol');
            stepsContainer.className = 'steps-list';
            
            result.steps.forEach(step => {
                const stepElement = document.createElement('li');
                stepElement.innerHTML = step;
                stepsContainer.appendChild(stepElement);
            });
            
            // Clear previous steps and add new ones
            const existingSteps = document.querySelector('.steps-list');
            if (existingSteps) {
                existingSteps.replaceWith(stepsContainer);
            } else {
                // Create a container for the steps if it doesn't exist
                const stepsSection = document.createElement('div');
                stepsSection.className = 'steps-container';
                stepsSection.innerHTML = '<h3>Calculation Steps</h3>';
                stepsSection.appendChild(stepsContainer);
                resultsDiv.appendChild(stepsSection);
            }
        }
        
        
        resultsDiv.style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        errorElement.textContent = error.message;
        errorElement.style.display = 'block';
    }
}