// Main form submission function for confidence interval method
async function submitProportionCIForm(event) {
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
        const x = parseInt(form.successCount.value);
        const n = parseInt(form.sampleSize.value);

        if (confidenceLevel <= 0 || confidenceLevel >= 100) {
            throw new Error('Confidence level must be between 0 and 100');
        }

        if (x < 0 || x > n) {
            throw new Error('Number of successes must be between 0 and sample size');
        }

        if (n <= 0) {
            throw new Error('Sample size must be positive');
        }

        // Prepare form data
        const formData = {
            confidenceLevel: confidenceLevel,
            sampleSize: n,
            successCount: x
        };

        // API Request
        const response = await fetch('/calculate_proportion_ci', {
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
            <p><strong>Sample Proportion (p̂):</strong> ${result.sampleProportion}</p>
            <p><strong>Confidence Level:</strong> ${result.confidenceLevel * 100}%</p>
            <p><strong>Critical Value:</strong> ${result.criticalValue}</p>
            <p><strong>Standard Error:</strong> ${result.standardError}</p>
            <p><strong>Margin of Error:</strong> ${result.marginOfError}</p>
            <p><strong>Confidence Interval:</strong> (${result.lowerBound}, ${result.upperBound})</p>
            <p><strong>Interpretation:</strong> We are ${result.confidenceLevel * 100}% confident that the true population proportion is between ${result.lowerBound} and ${result.upperBound}</p>
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

function validateSuccessCount(input, sampleSizeInput) {
    const x = parseInt(input.value);
    const n = parseInt(sampleSizeInput.value);
    if (isNaN(x) || x < 0 || (n && x > n)) {
        input.setCustomValidity('Successes must be between 0 and sample size');
    } else {
        input.setCustomValidity('');
    }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('hypothesisForm');
    form.addEventListener('submit', submitProportionCIForm);

    // Add validation for confidence level
    const confidenceLevelInput = document.getElementById('confidenceLevel');
    if (confidenceLevelInput) {
        confidenceLevelInput.addEventListener('input', function() {
            validateConfidenceLevel(this);
        });
    }

    // Add validation for success count
    const successInput = document.getElementById('successCount');
    const sampleSizeInput = document.getElementById('sampleSize');
    if (successInput && sampleSizeInput) {
        successInput.addEventListener('input', function() {
            validateSuccessCount(this, sampleSizeInput);
        });
        sampleSizeInput.addEventListener('input', function() {
            validateSuccessCount(successInput, this);
        });
    }
});