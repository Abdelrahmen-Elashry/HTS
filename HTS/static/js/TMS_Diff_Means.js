function toggleStdDevInputs() {
    const sigma1Input = document.getElementById('firstPopulationSigma');
    const sigma2Input = document.getElementById('secondPopulationSigma');
    const sample1StdDevInput = document.getElementById('firstSampleStdDev');
    const sample2StdDevInput = document.getElementById('secondSampleStdDev');

    // Clear errors when typing starts
    if ((sigma1Input.value.trim() !== '' && sigma2Input.value.trim() !== '') || (sample1StdDevInput.value.trim() !== '' && sample2StdDevInput.value.trim() !== '')) {
    sigmaError.style.display = 'none';
    stdDevError.style.display = 'none';
    }
    
    // Disable sampleStdDev if sigma has a value, and vice versa
    if (sigma1Input.value.trim() !== '' || sigma2Input.value.trim() !== '') {
        sample1StdDevInput.disabled = true;
        sample1StdDevInput.placeholder = 'Disabled (σ₁ is provided)';
        sample1StdDevInput.value = ''; // Clear the value
        sample2StdDevInput.disabled = true;
        sample2StdDevInput.placeholder = 'Disabled (σ₂ is provided)';
        sample2StdDevInput.value = ''; // Clear the value
    } else if (sample1StdDevInput.value.trim() !== '' || sample2StdDevInput.value.trim() !== '') {
        sigma1Input.disabled = true;
        sigma1Input.placeholder = 'Disabled (s₁ is provided)';
        sigma1Input.value = ''; // Clear the value
        sigma2Input.disabled = true;
        sigma2Input.placeholder = 'Disabled (s₂ is provided)';
        sigma2Input.value = ''; // Clear the value
    } else {
        // Enable both if both are empty
        sigma1Input.disabled = false;
        sample1StdDevInput.disabled = false;
        sigma1Input.placeholder = 'Leave blank if unknown';
        sample1StdDevInput.placeholder = 'Required if σ₁ is unknown';
        sigma2Input.disabled = false;
        sample2StdDevInput.disabled = false;
        sigma2Input.placeholder = 'Leave blank if unknown';
        sample2StdDevInput.placeholder = 'Required if σ₂ is unknown';
    }
}

// Add event listeners to both inputs
document.getElementById('firstPopulationSigma').addEventListener('input', toggleStdDevInputs);
document.getElementById('secondPopulationSigma').addEventListener('input', toggleStdDevInputs);
document.getElementById('firstSampleStdDev').addEventListener('input', toggleStdDevInputs);
document.getElementById('secondSampleStdDev').addEventListener('input', toggleStdDevInputs);

// Initialize on page load
document.addEventListener('DOMContentLoaded', toggleStdDevInputs);
/**/
async function submitForm(event) {
event.preventDefault();

const form = document.getElementById('hypothesisForm');
const submitBtn = form.querySelector('button[type="submit"]');
const resultsSection = document.querySelector('.results');
const sigma1Input = document.getElementById('firstPopulationSigma');
const sigma2Input = document.getElementById('secondPopulationSigma');
const sample1StdDevInput = document.getElementById('firstSampleStdDev');
const sample2StdDevInput = document.getElementById('secondSampleStdDev');
const sigmaError = document.getElementById('sigmaError');
const stdDevError = document.getElementById('stdDevError');

// Validate inputs
let isValid = true;

// Check if both sigma and sample std dev are empty
if ((sigma1Input.value.trim() === '' && sigma2Input.value.trim() === '') && (sample1StdDevInput.value.trim() === '' && sample2StdDevInput.value.trim() === '')) {
    sigmaError.textContent = 'Please provide either population σ or sample standard deviation';
    sigmaError.style.display = 'block';
    stdDevError.textContent = 'Please provide either population σ or sample standard deviation';
    stdDevError.style.display = 'block';
    isValid = false;
}

if (!isValid) {
    return; // Stop submission if validation fails
}

// UI State
submitBtn.disabled = true;
submitBtn.textContent = 'Calculating...';

try {
    // Prepare form data
    const formData = {
        hypothesisType: form.hypothesisType.value,
        alpha: parseFloat(form.alpha.value),
        n1: parseInt(form.firstSampleSize.value),
        n2: parseInt(form.secondSampleSize.value),
        x1: parseFloat(form.firstSampleMean.value),
        x2: parseFloat(form.secondSampleMean.value),
        sigma1: form.firstPopulationSigma.value ? parseFloat(form.firstPopulationSigma.value) : null,
        sigma2: form.secondPopulationSigma.value ? parseFloat(form.secondPopulationSigma.value) : null,
        s1: form.firstSampleStdDev.value ? parseFloat(form.firstSampleStdDev.value) : null,
        s2: form.secondSampleStdDev.value ? parseFloat(form.secondSampleStdDev.value) : null
    };

    // API Request
    const response = await fetch('/calculate_diff_means', {
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
        <p><strong>P-Value:</strong> ${result.pValue}</p>
        <p><strong>Distribution:</strong> ${result.distribution}</p>
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
        document.getElementById('calculationSteps').style.display = 'block';
        
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