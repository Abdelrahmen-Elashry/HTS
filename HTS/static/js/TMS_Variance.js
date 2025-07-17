// Main form submission function for variance traditional method
async function submitVarianceForm(event) {
    event.preventDefault();

    const form = document.getElementById('hypothesisForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultsSection = document.querySelector('.results');

    // Hide visualization at start
    document.getElementById('visualization-container').style.display = 'none';

    // UI State
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';

    try {
        // Validate inputs
        const hypothesisType = form.hypothesisType.value;
        const populationVariance = parseFloat(form.populationVariance.value);
        const alpha = parseFloat(form.alpha.value);
        const sampleSize = parseInt(form.sampleSize.value);
        const sampleVariance = parseFloat(form.sampleVariance.value);

        if (!hypothesisType) {
            throw new Error('Please select a hypothesis type');
        }

        if (populationVariance <= 0) {
            throw new Error('Population variance must be positive');
        }

        if (sampleVariance < 0) {
            throw new Error('Sample variance cannot be negative');
        }

        if (sampleSize < 2) {
            throw new Error('Sample size must be at least 2');
        }

        if (alpha <= 0 || alpha >= 1) {
            throw new Error('Significance level must be between 0 and 1');
        }

        // Prepare form data
        const formData = {
            hypothesisType: hypothesisType,
            populationVariance: populationVariance,
            alpha: alpha,
            sampleSize: sampleSize,
            sampleVariance: sampleVariance
        };

        // API Request
        const response = await fetch('/calculate_variance_traditional', {
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
        document.getElementById('resultContent').innerHTML = `
            <p><strong>Test Statistic:</strong> ${result.testStatistic}</p>
            <p><strong>Degrees of Freedom:</strong> ${result.degreesOfFreedom}</p>
            <p><strong>Critical Value(s):</strong> ${result.criticalValue}</p>
            <p><strong>Distribution:</strong> ${result.distribution}</p>
            <p><strong>Conclusion:</strong> ${result.conclusion}</p>
        `;

        // Show visualization if available
        if (result.plot) {
            document.getElementById('distPlot').src = `data:image/png;base64,${result.plot}`;
            document.getElementById('visualization-container').style.display = 'block';
        }

        // Display calculation steps
        if (result.steps) {
            const stepsList = document.getElementById('stepsList');
            stepsList.innerHTML = '';
            result.steps.forEach(step => {
                const li = document.createElement('li');
                li.innerHTML = step;
                stepsList.appendChild(li);
            });
            document.getElementById('calculationSteps').style.display = 'block';
        } else {
            document.getElementById('calculationSteps').style.display = 'none';
        }
        
        resultsSection.style.display = 'block';
        
    } catch (error) {
        console.error('Submission error:', error);
        alert(`Error: ${error.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Calculate Results';
    }
}

// Input validation for variance fields
function validateVarianceInput(input) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value <= 0) {
        input.setCustomValidity('Variance must be a positive number');
    } else {
        input.setCustomValidity('');
    }
}

// Input validation for sample variance
function validateSampleVariance(input) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value < 0) {
        input.setCustomValidity('Sample variance cannot be negative');
    } else {
        input.setCustomValidity('');
    }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('hypothesisForm');
    form.addEventListener('submit', submitVarianceForm);

    // Add validation for population variance
    const populationVarianceInput = document.getElementById('populationVariance');
    if (populationVarianceInput) {
        populationVarianceInput.addEventListener('input', function() {
            validateVarianceInput(this);
        });
    }

    // Add validation for sample variance
    const sampleVarianceInput = document.getElementById('sampleVariance');
    if (sampleVarianceInput) {
        sampleVarianceInput.addEventListener('input', function() {
            validateSampleVariance(this);
        });
    }

    // Add validation for sample size
    const sampleSizeInput = document.getElementById('sampleSize');
    if (sampleSizeInput) {
        sampleSizeInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (isNaN(value) || value < 2) {
                this.setCustomValidity('Sample size must be at least 2');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});