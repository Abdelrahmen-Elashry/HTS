// Main form submission function for p-value method
async function submitProportionPValueForm(event) {
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
        const p0 = parseFloat(form.populationProportion.value);
        const x = parseInt(form.successCount.value);
        const n = parseInt(form.sampleSize.value);
        const alpha = parseFloat(form.alpha.value);

        if (p0 < 0 || p0 > 1) {
            throw new Error('Hypothesized proportion must be between 0 and 1');
        }

        if (x < 0 || x > n) {
            throw new Error('Number of successes must be between 0 and sample size');
        }

        if (n <= 0) {
            throw new Error('Sample size must be positive');
        }

        if (alpha <= 0 || alpha >= 1) {
            throw new Error('Significance level must be between 0 and 1');
        }

        // Prepare form data
        const formData = {
            hypothesisType: form.hypothesisType.value,
            p0: p0,
            alpha: alpha,
            sampleSize: n,
            successCount: x
        };

        // API Request - changed endpoint to p-value version
        const response = await fetch('/calculate_proportion_pvalue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || 'Calculation failed');
        }
        
        // Display results - modified for p-value output
        const result = await response.json();
        document.getElementById('resultContent').innerHTML = `
            <p><strong>Sample Proportion (p̂):</strong> ${result.sampleProportion}</p>
            <p><strong>Test Statistic:</strong> ${result.testStatistic}</p>
            <p><strong>P-value:</strong> ${result.pValue}</p>
            <p><strong>Significance Level (α):</strong> ${result.alpha}</p>
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

// Input validation functions (same as traditional method)
function validateProportionInput(input) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value < 0 || value > 1) {
        input.setCustomValidity('Proportion must be between 0 and 1');
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
    // Changed to use p-value submission function
    form.addEventListener('submit', submitProportionPValueForm);

    // Add validation for proportion inputs
    const proportionInput = document.getElementById('populationProportion');
    if (proportionInput) {
        proportionInput.addEventListener('input', function() {
            validateProportionInput(this);
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

    // Additional validation for alpha (significance level)
    const alphaInput = document.getElementById('alpha');
    if (alphaInput) {
        alphaInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (isNaN(value) || value <= 0 || value >= 1) {
                this.setCustomValidity('Significance level must be between 0 and 1');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});