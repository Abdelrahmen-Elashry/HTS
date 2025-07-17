// Main form submission function for two-proportion p-value test
async function submitTwoProportionPValueForm(event) {
    event.preventDefault();

    const form = document.getElementById('hypothesisForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultsSection = document.querySelector('.results');

    // UI State
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';

    try {
        // Validate inputs
        const x1 = parseInt(form.successCount1.value);
        const n1 = parseInt(form.sampleSize1.value);
        const x2 = parseInt(form.successCount2.value);
        const n2 = parseInt(form.sampleSize2.value);

        if (x1 < 0 || x1 > n1) {
            throw new Error('Number of successes in sample 1 must be between 0 and sample size');
        }

        if (x2 < 0 || x2 > n2) {
            throw new Error('Number of successes in sample 2 must be between 0 and sample size');
        }

        if (n1 <= 0 || n2 <= 0) {
            throw new Error('Sample sizes must be positive');
        }

        // Prepare form data
        const formData = {
            hypothesisType: form.hypothesisType.value,
            alpha: parseFloat(form.alpha.value),
            sampleSize1: n1,
            successCount1: x1,
            sampleSize2: n2,
            successCount2: x2
        };

        // API Request - changed endpoint to p-value version
        const response = await fetch('/calculate_two_proportions_pvalue', {
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
            <p><strong>Sample 1 Proportion (p̂₁):</strong> ${result.sampleProportion1}</p>
            <p><strong>Sample 2 Proportion (p̂₂):</strong> ${result.sampleProportion2}</p>
            <p><strong>Difference (p̂₁ - p̂₂):</strong> ${result.difference}</p>
            <p><strong>Pooled Proportion:</strong> ${result.pooledProportion}</p>
            <p><strong>Test Statistic (Z):</strong> ${result.testStatistic}</p>
            <p><strong>P-Value:</strong> ${result.pValue}</p>
            <p><strong>Comparison:</strong> ${result.comparison}</p>
            <p><strong>Significance Level (α):</strong> ${formData.alpha}</p>
            <p><strong>Conclusion:</strong> ${result.conclusion}</p>
        `;

        // Display the visualization if available
        if (result.plot) {
            document.getElementById('distPlot').src = `data:image/png;base64,${result.plot}`;
            document.getElementById('visualization-container').style.display = 'block';
        } else {
            document.getElementById('visualization-container').style.display = 'none';
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

// Input validation for success counts (same as before)
function validateSuccessCount(input, sampleSizeInput) {
    const x = parseInt(input.value);
    const n = parseInt(sampleSizeInput.value);
    if (isNaN(x) || x < 0 || (n && x > n)) {
        input.setCustomValidity('Successes must be between 0 and sample size');
        input.reportValidity();
    } else {
        input.setCustomValidity('');
    }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('hypothesisForm');
    // Changed to use p-value version
    form.addEventListener('submit', submitTwoProportionPValueForm);

    // Add validation for success counts (same as before)
    const successInput1 = document.getElementById('successCount1');
    const sampleSizeInput1 = document.getElementById('sampleSize1');
    const successInput2 = document.getElementById('successCount2');
    const sampleSizeInput2 = document.getElementById('sampleSize2');

    if (successInput1 && sampleSizeInput1) {
        successInput1.addEventListener('input', function() {
            validateSuccessCount(this, sampleSizeInput1);
        });
        sampleSizeInput1.addEventListener('input', function() {
            validateSuccessCount(successInput1, this);
        });
    }

    if (successInput2 && sampleSizeInput2) {
        successInput2.addEventListener('input', function() {
            validateSuccessCount(this, sampleSizeInput2);
        });
        sampleSizeInput2.addEventListener('input', function() {
            validateSuccessCount(successInput2, this);
        });
    }

    // Add alpha value validation
    const alphaInput = document.getElementById('alpha');
    if (alphaInput) {
        alphaInput.addEventListener('input', function() {
            const alpha = parseFloat(this.value);
            if (isNaN(alpha)) {
                this.setCustomValidity('Please enter a valid number');
            } else if (alpha <= 0 || alpha >= 1) {
                this.setCustomValidity('Alpha must be between 0 and 1');
            } else {
                this.setCustomValidity('');
            }
            this.reportValidity();
        });
    }
});