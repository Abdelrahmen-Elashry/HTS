// Main form submission function for two-variance p-value test
async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById('hypothesisForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultsSection = document.querySelector('.results');

    // UI State
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';

    try {
        // Validate inputs
        const n1 = parseInt(form.sampleSize1.value);
        const n2 = parseInt(form.sampleSize2.value);
        const s1_squared = parseFloat(form.sampleVariance1.value);
        const s2_squared = parseFloat(form.sampleVariance2.value);

        if (n1 < 2 || n2 < 2) {
            throw new Error('Sample sizes must be at least 2');
        }

        if (s1_squared <= 0 || s2_squared <= 0) {
            throw new Error('Sample variances must be positive');
        }

        // Prepare form data
        const formData = {
            hypothesisType: form.hypothesisType.value,
            alpha: parseFloat(form.alpha.value),
            sampleSize1: n1,
            sampleVariance1: s1_squared,
            sampleSize2: n2,
            sampleVariance2: s2_squared
        };

        // API Request - changed endpoint to p-value version
        const response = await fetch('/calculate_two_variances_pvalue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Calculation failed');
        }
        
        // Display results
        const result = await response.json();
        document.getElementById('resultContent').innerHTML = `
            <p><strong>Larger Variance:</strong> ${result.largerVariance}</p>
            <p><strong>Test Statistic (F):</strong> ${result.testStatistic}</p>
            <p><strong>P-value:</strong> ${result.pValue}</p>
            <p><strong>Degrees of Freedom (numerator):</strong> ${result.df1}</p>
            <p><strong>Degrees of Freedom (denominator):</strong> ${result.df2}</p>
            <p><strong>Conclusion:</strong> ${result.conclusion}</p>
        `;

        // Display the plot if it exists
        if (result.plot) {
            document.getElementById('resultPlot').src = `data:image/png;base64,${result.plot}`;
            document.getElementById('plotContainer').style.display = 'block';
        } else {
            document.getElementById('plotContainer').style.display = 'none';
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

// Input validation for variances
function validateVariance(input) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value <= 0) {
        input.setCustomValidity('Variance must be a positive number');
    } else {
        input.setCustomValidity('');
    }
}

// Input validation for sample sizes
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
    form.addEventListener('submit', submitForm);

    // Add validation for variances
    const varianceInput1 = document.getElementById('sampleVariance1');
    const varianceInput2 = document.getElementById('sampleVariance2');
    const sizeInput1 = document.getElementById('sampleSize1');
    const sizeInput2 = document.getElementById('sampleSize2');

    if (varianceInput1) {
        varianceInput1.addEventListener('input', function() {
            validateVariance(this);
        });
    }

    if (varianceInput2) {
        varianceInput2.addEventListener('input', function() {
            validateVariance(this);
        });
    }

    if (sizeInput1) {
        sizeInput1.addEventListener('input', function() {
            validateSampleSize(this);
        });
    }

    if (sizeInput2) {
        sizeInput2.addEventListener('input', function() {
            validateSampleSize(this);
        });
    }
});