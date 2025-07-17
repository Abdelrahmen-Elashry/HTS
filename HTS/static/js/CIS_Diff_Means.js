function toggleStdDevInputs() {
    const sigma1Input = document.getElementById('firstPopulationSigma');
    const sigma2Input = document.getElementById('secondPopulationSigma');
    const sample1StdDevInput = document.getElementById('firstSampleStdDev');
    const sample2StdDevInput = document.getElementById('secondSampleStdDev');
    
    // Disable sampleStdDev if sigma has a value, and vice versa
    if (sigma1Input.value.trim() !== '' || sigma2Input.value.trim() !== '') {
        sample1StdDevInput.disabled = true;
        sample1StdDevInput.placeholder = 'Disabled (σ provided)';
        sample1StdDevInput.value = '';
        sample2StdDevInput.disabled = true;
        sample2StdDevInput.placeholder = 'Disabled (σ provided)';
        sample2StdDevInput.value = '';
    } else if (sample1StdDevInput.value.trim() !== '' || sample2StdDevInput.value.trim() !== '') {
        sigma1Input.disabled = true;
        sigma1Input.placeholder = 'Disabled (s provided)';
        sigma1Input.value = '';
        sigma2Input.disabled = true;
        sigma2Input.placeholder = 'Disabled (s provided)';
        sigma2Input.value = '';
    } else {
        // Enable both if both are empty
        sigma1Input.disabled = false;
        sample1StdDevInput.disabled = false;
        sigma1Input.placeholder = 'Leave blank if unknown';
        sample1StdDevInput.placeholder = 'Required if σ₁ unknown';
        sigma2Input.disabled = false;
        sample2StdDevInput.disabled = false;
        sigma2Input.placeholder = 'Leave blank if unknown';
        sample2StdDevInput.placeholder = 'Required if σ₂ unknown';
    }
}

// Add event listeners to inputs
document.getElementById('firstPopulationSigma').addEventListener('input', toggleStdDevInputs);
document.getElementById('secondPopulationSigma').addEventListener('input', toggleStdDevInputs);
document.getElementById('firstSampleStdDev').addEventListener('input', toggleStdDevInputs);
document.getElementById('secondSampleStdDev').addEventListener('input', toggleStdDevInputs);

// Initialize on page load
document.addEventListener('DOMContentLoaded', toggleStdDevInputs);

async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById('hypothesisForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultsSection = document.querySelector('.results');
    const sigma1Input = document.getElementById('firstPopulationSigma');
    const sigma2Input = document.getElementById('secondPopulationSigma');
    const sample1StdDevInput = document.getElementById('firstSampleStdDev');
    const sample2StdDevInput = document.getElementById('secondSampleStdDev');

    // UI State
    submitBtn.disabled = true;
    submitBtn.textContent = 'Calculating...';

    try {
        // Prepare form data
        const formData = {
            confidenceLevel: parseFloat(form.confidenceLevel.value),
            n1: parseInt(form.firstSampleSize.value),
            n2: parseInt(form.secondSampleSize.value),
            x1: parseFloat(form.firstSampleMean.value),
            x2: parseFloat(form.secondSampleMean.value),
            sigma1: sigma1Input.value.trim() ? parseFloat(sigma1Input.value) : null,
            sigma2: sigma2Input.value.trim() ? parseFloat(sigma2Input.value) : null,
            s1: sample1StdDevInput.value.trim() ? parseFloat(sample1StdDevInput.value) : null,
            s2: sample2StdDevInput.value.trim() ? parseFloat(sample2StdDevInput.value) : null
        };

        // API Request
        const response = await fetch('/calculate_diff_means_ci', {
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
            <p><strong>Difference (x̄₁-x̄₂):</strong> ${result.difference}</p>
            <p><strong>Confidence Level:</strong> ${result.confidenceLevel}%</p>
            <p><strong>Critical Value:</strong> ${result.criticalValue} (${result.distribution})</p>
            <p><strong>Standard Error:</strong> ${result.standardError}</p>
            <p><strong>Margin of Error:</strong> ${result.marginOfError}</p>
            <p><strong>Confidence Interval:</strong> (${result.lowerBound}, ${result.upperBound})</p>
            <p><strong>Interpretation:</strong> ${result.interpretation}</p>
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

// Event listener
document.getElementById('hypothesisForm').addEventListener('submit', submitForm);