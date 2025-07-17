// Main form submission function for variance confidence interval method
async function submitVarianceCIForm(event) {
    event.preventDefault();

    const form = document.getElementById('hypothesisForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultsSection = document.querySelector('.results');

    // UI State
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';

    try {
        // Validate inputs
        const confidenceLevel = parseFloat(form.confidenceLevel.value);
        const sampleSize = parseInt(form.sampleSize.value);
        const sampleVariance = parseFloat(form.sampleVariance.value);

        if (confidenceLevel <= 0 || confidenceLevel >= 100) {
            throw new Error('Confidence level must be between 0 and 100');
        }

        if (sampleVariance < 0) {
            throw new Error('Sample variance cannot be negative');
        }

        if (sampleSize < 2) {
            throw new Error('Sample size must be at least 2');
        }

        // Prepare form data
        const formData = {
            confidenceLevel: confidenceLevel,
            sampleSize: sampleSize,
            sampleVariance: sampleVariance
        };

        // API Request
        const response = await fetch('/calculate_variance_ci', {
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
            <p><strong>Confidence Level:</strong> ${result.confidenceLevel * 100}%</p>
            <p><strong>Degrees of Freedom:</strong> ${result.degreesOfFreedom}</p>
            <p><strong>Chi-Square Lower:</strong> ${result.chi2Lower}</p>
            <p><strong>Chi-Square Upper:</strong> ${result.chi2Upper}</p>
            <p><strong>Confidence Interval:</strong> (${result.lowerBound}, ${result.upperBound})</p>
            <p><strong>Interpretation:</strong> We are ${result.confidenceLevel * 100}% confident that the true population variance is between ${result.lowerBound} and ${result.upperBound}</p>
        `;

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

// Input validation functions
function validateConfidenceLevel(input) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value <= 0 || value >= 100) {
        input.setCustomValidity('Confidence level must be between 0 and 100');
    } else {
        input.setCustomValidity('');
    }
}

function validateSampleVariance(input) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value < 0) {
        input.setCustomValidity('Sample variance cannot be negative');
    } else {
        input.setCustomValidity('');
    }
}

function validateSampleSize(input) {
    const value = parseInt(input.value);
    if (isNaN(value) || value < 2) {
        input.setCustomValidity('Sample size must be at least 2');
    } else {
        input.setCustomValidity('');
    }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('hypothesisForm');
    form.addEventListener('submit', submitVarianceCIForm);

    // Add validation for confidence level
    const confidenceLevelInput = document.getElementById('confidenceLevel');
    if (confidenceLevelInput) {
        confidenceLevelInput.addEventListener('input', function() {
            validateConfidenceLevel(this);
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
            validateSampleSize(this);
        });
    }
});