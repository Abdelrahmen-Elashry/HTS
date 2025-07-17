// Form submission for Two-Proportion Confidence Interval
async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById('hypothesisForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultsSection = document.querySelector('.results');

    // UI State
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';

    try {
        // Extract input values
        const confidenceLevel = parseFloat(form.confidenceLevel.value);
        const x1 = parseInt(form.successCount1.value);
        const n1 = parseInt(form.sampleSize1.value);
        const x2 = parseInt(form.successCount2.value);
        const n2 = parseInt(form.sampleSize2.value);

        // Client-side validations
        if (isNaN(confidenceLevel) || confidenceLevel <= 0 || confidenceLevel >= 100) {
            throw new Error('Confidence level must be between 0 and 100');
        }

        if (n1 <= 0 || n2 <= 0) {
            throw new Error('Sample sizes must be positive');
        }

        if (x1 < 0 || x1 > n1) {
            throw new Error('Number of successes in sample 1 must be between 0 and sample size');
        }

        if (x2 < 0 || x2 > n2) {
            throw new Error('Number of successes in sample 2 must be between 0 and sample size');
        }

        // Prepare data
        const formData = {
            confidenceLevel,
            sampleSize1: n1,
            successCount1: x1,
            sampleSize2: n2,
            successCount2: x2
        };

        // API Request
        const response = await fetch('/calculate_two_proportions_ci', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Failed to calculate confidence interval');
        }

        const result = await response.json();

        // Display results
        document.getElementById('resultContent').innerHTML = `
            <p><strong>Sample 1 Proportion (p̂₁):</strong> ${result.sampleProportion1}</p>
            <p><strong>Sample 2 Proportion (p̂₂):</strong> ${result.sampleProportion2}</p>
            <p><strong>Difference (p̂₁ - p̂₂):</strong> ${result.difference}</p>
            <p><strong>Confidence Level:</strong> ${result.confidenceLevel}%</p>
            <p><strong>Critical Value (z):</strong> ${result.criticalValue}</p>
            <p><strong>Standard Error:</strong> ${result.standardError}</p>
            <p><strong>Margin of Error:</strong> ${result.marginOfError}</p>
            <p><strong>Confidence Interval:</strong> (${result.confidenceInterval.lower}, ${result.confidenceInterval.upper})</p>
            <p><strong>Interpretation:</strong> ${result.interpretation}</p>
        `;

        // Show calculation steps
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
        submitBtn.textContent = 'Calculate Confidence Interval';
    }
}

// Input validation for CI form
function validateCIInput(input, sampleSizeInput) {
    const x = parseInt(input.value);
    const n = parseInt(sampleSizeInput.value);
    if (isNaN(x) || x < 0 || (n && x > n)) {
        input.setCustomValidity('Successes must be between 0 and sample size');
        input.reportValidity();
    } else {
        input.setCustomValidity('');
    }
}

// Initialize listeners for CI form
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('confidenceIntervalForm');
    if (form) {
        form.addEventListener('submit', submitTwoProportionCIForm);

        // Input validations
        const successInput1 = document.getElementById('successCount1');
        const sampleSizeInput1 = document.getElementById('sampleSize1');
        const successInput2 = document.getElementById('successCount2');
        const sampleSizeInput2 = document.getElementById('sampleSize2');
        const confidenceLevelInput = document.getElementById('confidenceLevel');

        if (successInput1 && sampleSizeInput1) {
            successInput1.addEventListener('input', () => validateCIInput(successInput1, sampleSizeInput1));
            sampleSizeInput1.addEventListener('input', () => validateCIInput(successInput1, sampleSizeInput1));
        }

        if (successInput2 && sampleSizeInput2) {
            successInput2.addEventListener('input', () => validateCIInput(successInput2, sampleSizeInput2));
            sampleSizeInput2.addEventListener('input', () => validateCIInput(successInput2, sampleSizeInput2));
        }

        if (confidenceLevelInput) {
            confidenceLevelInput.addEventListener('input', function () {
                const value = parseFloat(this.value);
                if (isNaN(value) || value <= 0 || value >= 100) {
                    this.setCustomValidity('Confidence level must be between 0 and 100');
                } else {
                    this.setCustomValidity('');
                }
                this.reportValidity();
            });
        }
    }
});
