function toggleStdDevInputs() {
    const sigmaInput = document.getElementById('populationSigma');
    const sampleStdDevInput = document.getElementById('sampleStdDev');
    const sigmaError = document.getElementById('sigmaError');
    const stdDevError = document.getElementById('stdDevError');

    // Clear errors when typing starts
    if (sigmaInput.value.trim() !== '' || sampleStdDevInput.value.trim() !== '') {
    sigmaError.style.display = 'none';
    stdDevError.style.display = 'none';
    }
    
    // Disable sampleStdDev if sigma has a value, and vice versa
    if (sigmaInput.value.trim() !== '') {
        sampleStdDevInput.disabled = true;
        sampleStdDevInput.placeholder = 'Disabled (σ is provided)';
        sampleStdDevInput.value = ''; // Clear the value
    } else if (sampleStdDevInput.value.trim() !== '') {
        sigmaInput.disabled = true;
        sigmaInput.placeholder = 'Disabled (s is provided)';
        sigmaInput.value = ''; // Clear the value
    } else {
        // Enable both if both are empty
        sigmaInput.disabled = false;
        sampleStdDevInput.disabled = false;
        sigmaInput.placeholder = 'Leave blank if unknown';
        sampleStdDevInput.placeholder = 'Required if σ unknown';
    }
}

// Add event listeners to both inputs
document.getElementById('populationSigma').addEventListener('input', toggleStdDevInputs);
document.getElementById('sampleStdDev').addEventListener('input', toggleStdDevInputs);

// Initialize on page load
document.addEventListener('DOMContentLoaded', toggleStdDevInputs);
/**/
async function submitForm(event) {
event.preventDefault();

const form = document.getElementById('hypothesisForm');
const submitBtn = form.querySelector('button[type="submit"]');
const resultsSection = document.querySelector('.results');
const sigmaInput = document.getElementById('populationSigma');
const sampleStdDevInput = document.getElementById('sampleStdDev');
const sigmaError = document.getElementById('sigmaError');
const stdDevError = document.getElementById('stdDevError');

// Clear previous errors
sigmaError.style.display = 'none';
stdDevError.style.display = 'none';

// Validate inputs
let isValid = true;

// Check if both sigma and sample std dev are empty
if (sigmaInput.value.trim() === '' && sampleStdDevInput.value.trim() === '') {
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
    // Get form values
    const sigmaInput = document.getElementById('populationSigma');
    const sampleStdDevInput = document.getElementById('sampleStdDev');

    // Prepare form data
    const formData = {
        hypothesisType: form.hypothesisType.value,
        mu0: parseFloat(form.populationMean.value),
        alpha: parseFloat(form.alpha.value),
        sampleSize: parseInt(form.sampleSize.value),
        sampleMean: parseFloat(form.sampleMean.value),
        sigma: form.populationSigma.value ? parseFloat(form.populationSigma.value) : null,
        sampleStdDev: form.sampleStdDev.value ? parseFloat(form.sampleStdDev.value) : null
    };

    // API Request
    const response = await fetch('/calculate', {
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
        <p><strong>Critical Value:</strong> ${result.criticalValue}</p>
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