from flask import Flask, request, jsonify, render_template, url_for
import math
from scipy.stats import norm, t, chi2, f
import matplotlib
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from io import BytesIO
import base64
import numpy as np

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('/index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/Statistical_Calculations.html')
def Statistical_Calculations():
    return render_template('Statistical_Calculations.html')

@app.route('/CIS_Diff_Means.html')
def CIS_Diff_Means():
    return render_template('CIS_Diff_Means.html')

@app.route('/CIS_Mean.html')
def CIS_Mean():
    return render_template('CIS_Mean.html')

@app.route('/CIS_Proportion.html')
def CIS_Proportion():
    return render_template('CIS_Proportion.html')

@app.route('/CIS_Diff_Proportions.html')
def CIS_Diff_Proportions():
    return render_template('CIS_Diff_Proportions.html')

@app.route('/CIS_Variance.html')
def CIS_Variance():
    return render_template('CIS_Variance.html')

@app.route('/CIS_Diff_Variances.html')
def CIS_Diff_Variances():
    return render_template('CIS_Diff_Variances.html')

@app.route('/Confidence_Interval.html')
def Confidence_Interval():
    return render_template('Confidence_Interval.html')

@app.route('/Cookie_Policy.html')
def Cookie_Policy():
    return render_template('Cookie_Policy.html')

@app.route('/P_Value.html')
def P_Value():
    return render_template('P_Value.html')

@app.route('/Privacy_Policy.html')
def Privacy_Policy():
    return render_template('Privacy_Policy.html')

@app.route('/PVS_Diff_Means.html')
def PVS_Diff_Means():
    return render_template('PVS_Diff_Means.html')

@app.route('/PVS_Diff_Proportions.html')
def PVS_Diff_Proportions():
    return render_template('PVS_Diff_Proportions.html')

@app.route('/PVS_Diff_Variances.html')
def PVS_Diff_Variances():
    return render_template('PVS_Diff_Variances.html')

@app.route('/PVS_Mean.html')
def PVS_Mean():
    return render_template('PVS_Mean.html')

@app.route('/PVS_Proportion.html')
def PVS_Proportion():
    return render_template('PVS_Proportion.html')

@app.route('/PVS_Variance.html')
def PVS_Variance():
    return render_template('PVS_Variance.html')

@app.route('/Terms_Of_Use.html')
def Terms_Of_Use():
    return render_template('Terms_Of_Use.html')

@app.route('/TMS_Diff_Means.html')
def TMS_Diff_Means():
    return render_template('TMS_Diff_Means.html')

@app.route('/TMS_Mean.html')
def TMS_Mean():
    return render_template('TMS_Mean.html')

@app.route('/TMS_Proportion.html')
def TMS_Proportion():
    return render_template('TMS_proportion.html')

@app.route('/TMS_Diff_Proportions.html')
def TMS_Diff_Proportions():
    return render_template('TMS_Diff_Proportions.html')

@app.route('/TMS_Variance.html')
def TMS_Variance():
    return render_template('TMS_Variance.html')

@app.route('/TMS_Diff_Variances.html')
def TMS_Diff_Variances():
    return render_template('TMS_Diff_Variances.html')

@app.route('/Traditional.html')
def Traditional():
    return render_template('Traditional.html')

@app.context_processor
def inject_url():
    return dict(url_for=url_for)

# ---------------  Traditional Method For Mean --------------- #

@app.route('/calculate', methods=['POST'])
def calculate():
    print("Received request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        # Validate required fields
        required_fields = ['hypothesisType', 'mu0', 'alpha', 'sampleSize', 'sampleMean']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        mu0 = float(data['mu0'])
        alpha = float(data['alpha'])
        n = int(data['sampleSize'])
        x_bar = float(data['sampleMean'])
        sigma = float(data['sigma']) if data.get('sigma') else None
        s = float(data['sampleStdDev']) if data.get('sampleStdDev') else None

        if not sigma and not s:
            return jsonify({'error': 'Sample standard deviation required when population σ is unknown'}), 400
        
        # Perform calculations
        if sigma:  # Z-test (σ known)
            z_score = (x_bar - mu0) / (sigma / math.sqrt(n))
            if hypothesis_type == 'two-tailed':
                critical_value = norm.ppf(1 - alpha/2)
                critical_value_display = f"±{round(abs(critical_value), 4)}"
            elif hypothesis_type == 'right-tailed':
                critical_value = norm.ppf(1 - alpha)
                critical_value_display = round(critical_value, 4)
            else:  # left-tailed
                critical_value = norm.ppf(alpha)
                critical_value_display = round(critical_value, 4)
            test_statistic = z_score
            distribution = 'z-distribution'
        else:  # Always use t-test when σ is unknown
            if not s:
                return jsonify({'error': 'Sample standard deviation required when population σ is unknown'}), 400
            s = float(s)
            standard_error = s / math.sqrt(n)
            t_score = (x_bar - mu0) / standard_error
            
            if hypothesis_type == 'two-tailed':
                critical_value = t.ppf(1 - alpha/2, df=n-1)
                critical_value_display = f"±{round(abs(critical_value), 4)}"
            elif hypothesis_type == 'right-tailed':
                critical_value = t.ppf(1 - alpha, df=n-1)
                critical_value_display = round(critical_value, 4)
            else:  # left-tailed
                critical_value = t.ppf(alpha, df=n-1)
                critical_value_display = round(critical_value, 4)
                
            test_statistic = t_score
            distribution = 't-distribution'

        # ===== Create visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))

        # Determine plot range dynamically
        plot_margin = 0.5
        x_min = min(-4, test_statistic - 3, -abs(critical_value) - plot_margin)
        x_max = max(4, test_statistic + 3, abs(critical_value) + plot_margin)
        x = np.linspace(x_min, x_max, 1000)
        y = norm.pdf(x)

        # Plot standard normal distribution
        ax.plot(x, y, 'b-', label='Standard Normal Distribution', linewidth=2)

        # Shade rejection region under the curve
        if hypothesis_type == 'two-tailed':
            x_left = x[x <= -abs(critical_value)]
            x_right = x[x >= abs(critical_value)]
            ax.fill_between(x_left, norm.pdf(x_left), color='red', alpha=0.3, label='Rejection Region')
            ax.fill_between(x_right, norm.pdf(x_right), color='red', alpha=0.3)
            ax.plot([-critical_value, -critical_value], [0, norm.pdf(-critical_value)], color='red', linestyle='--', linewidth=1.5)
            ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], color='red', linestyle='--', linewidth=1.5)
            
            # Position CV labels on opposite sides
            ax.text(-critical_value - 0.1, norm.pdf(-critical_value) + 0.01, f'CV: -{abs(critical_value):.2f}', ha='right', va='bottom', color='red')
            ax.text(critical_value + 0.1, norm.pdf(critical_value) + 0.01, f'CV: {critical_value:.2f}', ha='left', va='bottom', color='red')

        elif hypothesis_type == 'left-tailed':
            x_crit = x[x <= critical_value]
            ax.fill_between(x_crit, norm.pdf(x_crit), color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions for left-tailed test
            if test_statistic < critical_value:
                # Test stat is in rejection region - label on left
                ts_ha = 'right'
                ts_x_offset = -0.1
                cv_ha = 'left'
                cv_x_offset = 0.1
            else:
                # Test stat is not in rejection region - label on right
                ts_ha = 'left'
                ts_x_offset = 0.1
                cv_ha = 'right'
                cv_x_offset = -0.1
            
            ax.text(critical_value + cv_x_offset, norm.pdf(critical_value) + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        else:  # right-tailed
            x_crit = x[x >= critical_value]
            ax.fill_between(x_crit, norm.pdf(x_crit), color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions for right-tailed test
            if test_statistic > critical_value:
                # Test stat is in rejection region - label on right
                ts_ha = 'left'
                ts_x_offset = 0.1
                cv_ha = 'right'
                cv_x_offset = -0.1
            else:
                # Test stat is not in rejection region - label on left
                ts_ha = 'right'
                ts_x_offset = -0.1
                cv_ha = 'left'
                cv_x_offset = 0.1
            
            ax.text(critical_value + cv_x_offset, norm.pdf(critical_value) + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        # Plot test statistic with dynamic labeling
        ax.plot([test_statistic, test_statistic], [0, norm.pdf(test_statistic)], color='green', linestyle='-', linewidth=2)
        ts_y_pos = norm.pdf(test_statistic) + 0.02

        if hypothesis_type == 'two-tailed':
            # For two-tailed, keep original positioning
            ax.text(test_statistic - 0.1, ts_y_pos, f'Test Stat: {test_statistic:.2f}', ha='right', va='bottom', color='green')
        else:
            # For one-tailed tests, use the determined positions
            ax.text(test_statistic + ts_x_offset, ts_y_pos, 
                    f'Test Stat: {test_statistic:.2f}', 
                    ha=ts_ha, va='bottom', color='green')

        # Formatting
        ax.set_title('Hypothesis Test Visualization', fontsize=14, pad=20)
        ax.set_xlabel('Standard Deviations from Mean (Z)', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.arange(int(x_min), int(x_max)+1, 1))
        ax.set_yticks(np.linspace(0, max(y)+0.1, 10))
        ax.set_ylim(0, max(y) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label='Normal Distribution'),
            Patch(facecolor='red', alpha=0.3, label='Rejection Region'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value'),
            Line2D([0], [0], color='green', lw=2, label='Test Statistic')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()

        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): μ = {mu0}")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ ≠ {mu0} (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ > {mu0} (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): μ < {mu0} (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")

        # Perform calculations with explanations
        if sigma:  # Z-test
            steps.append("<strong>Step 2: Using Z-Test (σ known)</strong>")
            steps.append(f"• Population σ provided: {sigma}")
            standard_error = sigma / math.sqrt(n)
            z_score = (x_bar - mu0) / standard_error
            steps.append(f"• Standard Error (σ/√n): {round(standard_error, 4)}")
            steps.append(f"• Z-Score: (x̄ - μ₀)/SE = ({x_bar} - {mu0})/{round(standard_error, 4)} = {round(z_score, 4)}")
            
            if hypothesis_type == 'two-tailed':
                critical_value = norm.ppf(1 - alpha/2)
                steps.append(f"• Critical Value: ±{round(critical_value, 4)} (Two-tailed)")
            elif hypothesis_type == 'right-tailed':
                critical_value = norm.ppf(1 - alpha)
                steps.append(f"• Critical Value: {round(critical_value, 4)} (Right-tailed)")
            else:
                critical_value = norm.ppf(alpha)
                steps.append(f"• Critical Value: {round(critical_value, 4)} (Left-tailed)")
        else:  # t-test
            steps.append("<strong>Step 2: Standard Deviation</strong>")
            steps.append(f"• Using sample standard deviation (s): {s}")
            standard_error = s / math.sqrt(n)
            steps.append(f"• Standard Error (s/√n): {round(standard_error, 4)}")
            
            steps.append("<strong>Step 3: Using T-Test (σ unknown)</strong>")
            t_score = (x_bar - mu0) / standard_error
            steps.append(f"• T-Score: (x̄ - μ₀)/SE = ({x_bar} - {mu0})/{round(standard_error, 4)} = {round(t_score, 4)}")
            steps.append(f"• Degrees of Freedom: n-1 = {n-1}")
                
            if hypothesis_type == 'two-tailed':
                critical_value = t.ppf(1 - alpha/2, df=n-1)
                steps.append(f"• Critical Value: ±{round(critical_value, 4)}")
            elif hypothesis_type == 'right-tailed':
                critical_value = t.ppf(1 - alpha, df=n-1)
                steps.append(f"• Critical Value: {round(critical_value, 4)}")
            else:
                critical_value = t.ppf(alpha, df=n-1)
                steps.append(f"• Critical Value: {round(critical_value, 4)}")
        
        # Decision logic with explanation
        steps.append("<strong>Step 4: Decision Rule</strong>")
        if hypothesis_type == 'two-tailed':
            reject_condition = abs(test_statistic) > abs(critical_value)
            steps.append(f"• Reject H₀ if |Test Statistic| > |Critical Value|")
            
            if test_statistic == 0:
                steps.append(f"• Test Statistic is exactly 0 (sample mean equals hypothesized mean)")
                steps.append(f"• {abs(round(test_statistic, 4))} == 0")
            elif abs(test_statistic) == abs(critical_value):
                steps.append(f"• Test Statistic exactly equals Critical Value (borderline case)")
                steps.append(f"• {abs(round(test_statistic, 4))} == {abs(round(critical_value, 4))}")
            else:
                steps.append(f"• {abs(round(test_statistic, 4))} {'>' if reject_condition else '<'} {abs(round(critical_value, 4))}")
                
        else:
            if hypothesis_type == 'right-tailed':
                reject_condition = test_statistic > critical_value
                steps.append(f"• Reject H₀ if Test Statistic > Critical Value")
                
                if test_statistic == critical_value:
                    steps.append(f"• Test Statistic exactly equals Critical Value (borderline case)")
                    steps.append(f"• {round(test_statistic, 4)} == {round(critical_value, 4)}")
                else:
                    steps.append(f"• {round(test_statistic, 4)} {'>' if reject_condition else '<'} {round(critical_value, 4)}")
                    
            else:  # left-tailed
                reject_condition = test_statistic < critical_value
                steps.append(f"• Reject H₀ if Test Statistic < Critical Value")
                
                if test_statistic == critical_value:
                    steps.append(f"• Test Statistic exactly equals Critical Value (borderline case)")
                    steps.append(f"• {round(test_statistic, 4)} == {round(critical_value, 4)}")
                elif test_statistic == 0:
                    steps.append(f"• Test Statistic is exactly 0 (sample mean equals hypothesized mean)")
                    steps.append(f"• {round(test_statistic, 4)} == 0")
                else:
                    steps.append(f"• {round(test_statistic, 4)} {'<' if reject_condition else '>'} {round(critical_value, 4)}")
        
        # Conclusion with special case handling
        if (hypothesis_type == 'two-tailed' and abs(test_statistic) == abs(critical_value)) or \
           (hypothesis_type != 'two-tailed' and test_statistic == critical_value):
            conclusion = 'Borderline case: Test Statistic equals Critical Value'
        elif test_statistic == 0:
            conclusion = 'Test Statistic is 0 (sample mean equals hypothesized mean)'
        else:
            conclusion = 'Reject H₀' if reject_condition else 'Fail to reject H₀'
            
        steps.append(f"<strong>Conclusion:</strong> {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(test_statistic, 4),
            'criticalValue': critical_value_display,
            'distribution': distribution,
            'conclusion': conclusion,
            'steps': steps,
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        if 'fig' in locals():
            plt.close(fig)
        return jsonify({'error': str(e)}), 500

# ---------------  P-Value Method For Mean --------------- #

@app.route('/calculate_pvalue', methods=['POST'])
def calculate_pvalue():
    print("Received p-value request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        # Validate required fields
        required_fields = ['hypothesisType', 'mu0', 'alpha', 'sampleSize', 'sampleMean']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        mu0 = float(data['mu0'])
        alpha = float(data['alpha'])
        n = int(data['sampleSize'])
        x_bar = float(data['sampleMean'])
        sigma = float(data['sigma']) if data.get('sigma') else None
        s = float(data['sampleStdDev']) if data.get('sampleStdDev') else None

        if not sigma and not s:
            return jsonify({'error': 'Sample standard deviation required when population σ is unknown'}), 400
        
        # Perform calculations
        if sigma:  # Z-test (σ known)
            standard_error = sigma / math.sqrt(n)
            z_score = (x_bar - mu0) / standard_error
            
            if hypothesis_type == 'two-tailed':
                p_value = 2 * (1 - norm.cdf(abs(z_score)))
            elif hypothesis_type == 'right-tailed':
                p_value = 1 - norm.cdf(z_score)
            else:  # left-tailed
                p_value = norm.cdf(z_score)
                
            test_statistic = z_score
            distribution = 'z-distribution'
        else:  # Always use t-test when σ is unknown
            if not s:
                return jsonify({'error': 'Sample standard deviation required when population σ is unknown'}), 400
            
            s = float(s)
            standard_error = s / math.sqrt(n)
            t_score = (x_bar - mu0) / standard_error
            
            if hypothesis_type == 'two-tailed':
                p_value = 2 * (1 - t.cdf(abs(t_score), df=n-1))
            elif hypothesis_type == 'right-tailed':
                p_value = 1 - t.cdf(t_score, df=n-1)
            else:  # left-tailed
                p_value = t.cdf(t_score, df=n-1)
                
            test_statistic = t_score
            distribution = 't-distribution'

        # ===== Create visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))

        # Calculate critical value based on alpha
        if hypothesis_type == 'two-tailed':
            crit_val = norm.ppf(1 - alpha/2) if sigma else t.ppf(1 - alpha/2, df=n-1)
        elif hypothesis_type == 'right-tailed':
            crit_val = norm.ppf(1 - alpha) if sigma else t.ppf(1 - alpha, df=n-1)
        else:  # left-tailed
            crit_val = norm.ppf(alpha) if sigma else t.ppf(alpha, df=n-1)

        # Determine plot range dynamically
        plot_margin = 0.5
        x_min = min(-4, test_statistic - 3, -abs(crit_val) - plot_margin)
        x_max = max(4, test_statistic + 3, abs(crit_val) + plot_margin)
        x = np.linspace(x_min, x_max, 1000)

        # Choose distribution (normal or t)
        if sigma:
            y = norm.pdf(x)
            dist_label = 'Standard Normal Distribution'
        else:
            y = t.pdf(x, df=n-1)
            dist_label = f't-Distribution (df={n-1})'

        # Plot distribution
        ax.plot(x, y, 'b-', label=dist_label, linewidth=2)

        # Shade p-value region
        if hypothesis_type == 'two-tailed':
            left_tail = x[x <= -abs(test_statistic)]
            right_tail = x[x >= abs(test_statistic)]
            ax.fill_between(left_tail, norm.pdf(left_tail) if sigma else t.pdf(left_tail, df=n-1), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
            ax.fill_between(right_tail, norm.pdf(right_tail) if sigma else t.pdf(right_tail, df=n-1), 
                            color='green', alpha=0.3)
        elif hypothesis_type == 'right-tailed':
            p_value_area = x[x >= test_statistic]
            ax.fill_between(p_value_area, norm.pdf(p_value_area) if sigma else t.pdf(p_value_area, df=n-1), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
        else:  # left-tailed
            p_value_area = x[x <= test_statistic]
            ax.fill_between(p_value_area, norm.pdf(p_value_area) if sigma else t.pdf(p_value_area, df=n-1), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')

        # Shade alpha region (rejection region)
        if hypothesis_type == 'two-tailed':
            alpha_left = x[x <= -abs(crit_val)]
            alpha_right = x[x >= abs(crit_val)]
            ax.fill_between(alpha_left, norm.pdf(alpha_left) if sigma else t.pdf(alpha_left, df=n-1), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.fill_between(alpha_right, norm.pdf(alpha_right) if sigma else t.pdf(alpha_right, df=n-1), 
                            color='orange', alpha=0.2)
            # Draw CV lines only up to curve height
            ax.plot([-crit_val, -crit_val], [0, norm.pdf(-crit_val) if sigma else t.pdf(-crit_val, df=n-1)], 
                    color='red', linestyle='--', linewidth=1.5)
            ax.plot([crit_val, crit_val], [0, norm.pdf(crit_val) if sigma else t.pdf(crit_val, df=n-1)], 
                    color='red', linestyle='--', linewidth=1.5)
        else:
            alpha_area = x[x >= crit_val] if hypothesis_type == 'right-tailed' else x[x <= crit_val]
            ax.fill_between(alpha_area, norm.pdf(alpha_area) if sigma else t.pdf(alpha_area, df=n-1), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            # Draw CV line only up to curve height
            ax.plot([crit_val, crit_val], [0, norm.pdf(crit_val) if sigma else t.pdf(crit_val, df=n-1)], 
                    color='red', linestyle='--', linewidth=1.5)

        # Plot test statistic line only up to curve height
        ax.plot([test_statistic, test_statistic], [0, norm.pdf(test_statistic) if sigma else t.pdf(test_statistic, df=n-1)], 
                color='green', linestyle='-', linewidth=2)
        ts_y_pos = y[np.abs(x - test_statistic).argmin()] + 0.02

        if hypothesis_type == 'two-tailed':
            # For two-tailed tests, keep original positioning
            ax.text(test_statistic + 0.1, ts_y_pos,
                    f'Test Stat: {test_statistic:.2f}', 
                    ha='left',
                    va='bottom', 
                    color='green')
            
            ax.text(-crit_val + 0.1, y[np.abs(x - -crit_val).argmin()] + 0.01,
                    f'CV: -{abs(crit_val):.2f}', 
                    ha='left',
                    va='bottom', 
                    color='red')
            ax.text(crit_val - 0.1, y[np.abs(x - crit_val).argmin()] + 0.01,
                    f'CV: {crit_val:.2f}', 
                    ha='right',
                    va='bottom', 
                    color='red')
        else:
            # For one-tailed tests, determine label positions based on relative values
            if (hypothesis_type == 'right-tailed' and test_statistic > crit_val) or \
            (hypothesis_type == 'left-tailed' and test_statistic < crit_val):
                # Test stat is in rejection region
                ts_ha = 'left'
                ts_offset = 0.1
                cv_ha = 'right'
                cv_offset = -0.1
            else:
                # Test stat is not in rejection region
                ts_ha = 'right'
                ts_offset = -0.1
                cv_ha = 'left'
                cv_offset = 0.1
            
            # Position test statistic label
            ax.text(test_statistic + ts_offset, ts_y_pos,
                    f'Test Stat: {test_statistic:.2f}', 
                    ha=ts_ha,
                    va='bottom', 
                    color='green')
            
            # Position critical value label
            ax.text(crit_val + cv_offset,
                    y[np.abs(x - crit_val).argmin()] + 0.01, 
                    f'CV: {crit_val:.2f}', 
                    ha=cv_ha,
                    va='bottom', 
                    color='red')

        # Formatting
        ax.set_title(f'P-Value Hypothesis Test\n({dist_label})', fontsize=14, pad=20)
        ax.set_xlabel('Standard Deviations from Mean (Z)' if sigma else 't-values', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.arange(int(x_min), int(x_max)+1, 1))
        ax.set_yticks(np.linspace(0, max(y)+0.1, 10))
        ax.set_ylim(0, max(y) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label=dist_label),
            Patch(facecolor='green', alpha=0.3, label=f'p-value ({p_value:.4f})'),
            Patch(facecolor='orange', alpha=0.2, label=f'α region ({alpha})'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic ({test_statistic:.2f})'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value(s)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()

        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): μ = {mu0}")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ ≠ {mu0} (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ > {mu0} (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): μ < {mu0} (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")

        # Perform calculations with explanations
        if sigma:  # Z-test
            steps.append("<strong>Step 2: Using Z-Test (σ known)</strong>")
            steps.append(f"• Population σ provided: {sigma}")
            steps.append(f"• Standard Error (σ/√n): {round(standard_error, 4)}")
            steps.append(f"• Z-Score: (x̄ - μ₀)/SE = ({x_bar} - {mu0})/{round(standard_error, 4)} = {round(test_statistic, 4)}")
        else:  # T-test
            steps.append("<strong>Step 2: Using T-Test (σ unknown)</strong>")
            steps.append(f"• Sample standard deviation (s): {s}")
            steps.append(f"• Standard Error (s/√n): {round(standard_error, 4)}")
            steps.append(f"• T-Score: (x̄ - μ₀)/SE = ({x_bar} - {mu0})/{round(standard_error, 4)} = {round(test_statistic, 4)}")
            steps.append(f"• Degrees of Freedom: n-1 = {n-1}")
        
        # P-value calculation explanation
        steps.append("<strong>Step 3: P-Value Calculation</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Two-tailed p-value = 2 × P(X ≥ |{round(test_statistic, 4)}|)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Right-tailed p-value = P(X ≥ {round(test_statistic, 4)})")
        else:
            steps.append(f"• Left-tailed p-value = P(X ≤ {round(test_statistic, 4)})")
        steps.append(f"• Calculated p-value: {round(p_value, 6)}")
        
        # Decision rule
        steps.append("<strong>Step 4: Decision Rule</strong>")
        steps.append(f"• Reject H₀ if p-value ≤ α ({alpha})")
        steps.append(f"• {round(p_value, 6)} {'≤' if p_value <= alpha else '>'} {alpha}")
        
        # Conclusion
        conclusion = 'Reject H₀' if p_value <= alpha else 'Fail to reject H₀'
        steps.append(f"<strong>Conclusion:</strong> {conclusion} (p-value = {round(p_value, 6)})")
        
        # Prepare results
        result = {
            'testStatistic': round(test_statistic, 4),
            'pValue': round(p_value, 6),
            'distribution': distribution,
            'conclusion': conclusion,
            'steps': steps,
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        if 'fig' in locals():
            plt.close(fig)
        return jsonify({'error': str(e)}), 500
    
# ---------------  Confidence Interval Method For Mean --------------- #
    
@app.route('/calculate_ci', methods=['POST'])
def calculate_ci():
    print("Received CI request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['confidenceLevel', 'sampleSize', 'sampleMean']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        confidence_level = float(data['confidenceLevel'])
        n = int(data['sampleSize'])
        x_bar = float(data['sampleMean'])
        sigma = float(data['sigma']) if data.get('sigma') else None
        s = float(data['sampleStdDev']) if data.get('sampleStdDev') else None

        if not sigma and not s:
            return jsonify({'error': 'Sample standard deviation required when population σ is unknown'}), 400
        
        # Calculate critical value and standard error
        alpha = 1 - (confidence_level / 100)
        
        if sigma:  # Z-interval (σ known)
            standard_error = sigma / math.sqrt(n)
            critical_value = norm.ppf(1 - alpha/2)
            distribution = 'z-distribution'
        else:  # t-interval (σ unknown)
            standard_error = s / math.sqrt(n)
            critical_value = t.ppf(1 - alpha/2, df=n-1)
            distribution = 't-distribution'
        
        # Calculate margin of error and confidence interval
        margin_of_error = critical_value * standard_error
        lower_bound = x_bar - margin_of_error
        upper_bound = x_bar + margin_of_error
        
        # Initialize explanation steps
        steps = []
        
        # Add basic info
        steps.append(f"<strong>Step 1: Input Parameters</strong>")
        steps.append(f"• Confidence Level: {confidence_level}%")
        steps.append(f"• Sample Mean (x̄): {x_bar}")
        steps.append(f"• Sample Size (n): {n}")
        
        # Add distribution info
        steps.append("<strong>Step 2: Distribution Selection</strong>")
        if sigma:
            steps.append(f"• Using z-distribution (σ known: {sigma})")
            steps.append(f"• Standard Error (σ/√n): {round(standard_error, 4)}")
        else:
            steps.append(f"• Using t-distribution (σ unknown, using s: {s})")
            steps.append(f"• Degrees of Freedom: n-1 = {n-1}")
            steps.append(f"• Standard Error (s/√n): {round(standard_error, 4)}")
        
        # Add critical value calculation
        steps.append("<strong>Step 3: Critical Value</strong>")
        if sigma:
            steps.append(f"• z* for {confidence_level}% CI: {round(critical_value, 4)}")
        else:
            steps.append(f"• t* for {confidence_level}% CI: {round(critical_value, 4)}")
        
        # Add margin of error calculation
        steps.append("<strong>Step 4: Margin of Error</strong>")
        steps.append(f"• Margin of Error = Critical Value × Standard Error")
        steps.append(f"• {round(critical_value, 4)} × {round(standard_error, 4)} = {round(margin_of_error, 4)}")
        
        # Add confidence interval calculation
        steps.append("<strong>Step 5: Confidence Interval</strong>")
        steps.append(f"• Lower Bound = x̄ - Margin of Error")
        steps.append(f"• {round(x_bar, 4)} - {round(margin_of_error, 4)} = {round(lower_bound, 4)}")
        steps.append(f"• Upper Bound = x̄ + Margin of Error")
        steps.append(f"• {round(x_bar, 4)} + {round(margin_of_error, 4)} = {round(upper_bound, 4)}")
        
        # Prepare results
        result = {
            'confidenceLevel': confidence_level,
            'sampleMean': round(x_bar, 4),
            'criticalValue': round(critical_value, 4),
            'standardError': round(standard_error, 4),
            'marginOfError': round(margin_of_error, 4),
            'lowerBound': round(lower_bound, 4),
            'upperBound': round(upper_bound, 4),
            'distribution': distribution,
            'steps': steps
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------  Traditional Method For ProPortion --------------- #

@app.route('/calculate_proportion', methods=['POST'])
def calculate_proportion():
    print("Received proportion test request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'p0', 'alpha', 'sampleSize', 'successCount']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        p0 = float(data['p0'])
        alpha = float(data['alpha'])
        n = int(data['sampleSize'])
        x = int(data['successCount'])
        
        # Validate inputs
        if p0 < 0 or p0 > 1:
            return jsonify({'error': 'Hypothesized proportion must be between 0 and 1'}), 400
        if x < 0 or x > n:
            return jsonify({'error': 'Number of successes must be between 0 and sample size'}), 400
        
        # Calculate sample proportion
        p_hat = x / n
        
        # Calculate standard error
        standard_error = math.sqrt((p0 * (1 - p0)) / n)
        
        # Calculate z-score
        z_score = (p_hat - p0) / standard_error
        
        # Determine critical value based on test type
        if hypothesis_type == 'two-tailed':
            critical_value = norm.ppf(1 - alpha/2)
            critical_value_display = f"±{round(abs(critical_value), 4)}"
        elif hypothesis_type == 'right-tailed':
            critical_value = norm.ppf(1 - alpha)
            critical_value_display = round(critical_value, 4)
        else:  # left-tailed
            critical_value = norm.ppf(alpha)
            critical_value_display = round(critical_value, 4)

        # ===== Create visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))

        # Determine plot range dynamically
        plot_margin = 0.5
        axis_min = min(-4, z_score - 3, -abs(critical_value) - plot_margin)
        axis_max = max(4, z_score + 3, abs(critical_value) + plot_margin)
        x_vals = np.linspace(axis_min, axis_max, 1000)
        y_vals = norm.pdf(x_vals)

        # Plot standard normal distribution
        ax.plot(x_vals, y_vals, 'b-', label='Standard Normal Distribution', linewidth=2)

        # Shade rejection region (alpha region)
        if hypothesis_type == 'two-tailed':
            left_reject = x_vals[x_vals <= -abs(critical_value)]
            right_reject = x_vals[x_vals >= abs(critical_value)]
            ax.fill_between(left_reject, norm.pdf(left_reject), color='red', alpha=0.3, label='Rejection Region')
            ax.fill_between(right_reject, norm.pdf(right_reject), color='red', alpha=0.3)
            ax.plot([-critical_value, -critical_value], [0, norm.pdf(-critical_value)], color='red', linestyle='--', linewidth=1.5)
            ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], color='red', linestyle='--', linewidth=1.5)
            
            # Position CV labels on opposite sides
            ax.text(-critical_value - 0.1, norm.pdf(-critical_value) + 0.01, f'CV: -{abs(critical_value):.2f}', ha='right', va='bottom', color='red')
            ax.text(critical_value + 0.1, norm.pdf(critical_value) + 0.01, f'CV: {critical_value:.2f}', ha='left', va='bottom', color='red')

        elif hypothesis_type == 'left-tailed':
            reject_region = x_vals[x_vals <= critical_value]
            ax.fill_between(reject_region, norm.pdf(reject_region), color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions for left-tailed test
            if z_score < critical_value:
                # Test stat is in rejection region - label on left
                ts_ha = 'right'
                ts_x_offset = -0.1
                cv_ha = 'left'
                cv_x_offset = 0.1
            else:
                # Test stat is not in rejection region - label on right
                ts_ha = 'left'
                ts_x_offset = 0.1
                cv_ha = 'right'
                cv_x_offset = -0.1
            
            ax.text(critical_value + cv_x_offset, norm.pdf(critical_value) + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        else:  # right-tailed
            reject_region = x_vals[x_vals >= critical_value]
            ax.fill_between(reject_region, norm.pdf(reject_region), color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions for right-tailed test
            if z_score > critical_value:
                # Test stat is in rejection region - label on right
                ts_ha = 'left'
                ts_x_offset = 0.1
                cv_ha = 'right'
                cv_x_offset = -0.1
            else:
                # Test stat is not in rejection region - label on left
                ts_ha = 'right'
                ts_x_offset = -0.1
                cv_ha = 'left'
                cv_x_offset = 0.1
            
            ax.text(critical_value + cv_x_offset, norm.pdf(critical_value) + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        # Plot test statistic with dynamic labeling
        ax.plot([z_score, z_score], [0, norm.pdf(z_score)], color='green', linestyle='-', linewidth=2)
        ts_y_pos = norm.pdf(z_score) + 0.02

        if hypothesis_type == 'two-tailed':
            # For two-tailed, keep original positioning
            ax.text(z_score - 0.1, ts_y_pos, f'Test Stat: {z_score:.2f}', ha='right', va='bottom', color='green')
        else:
            # For one-tailed tests, use the determined positions
            ax.text(z_score + ts_x_offset, ts_y_pos, 
                    f'Test Stat: {z_score:.2f}', 
                    ha=ts_ha, va='bottom', color='green')

        # Formatting
        ax.set_title('Hypothesis Test Visualization (Proportion)', fontsize=14, pad=20)
        ax.set_xlabel('Standard Deviations from Mean (Z)', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.arange(int(axis_min), int(axis_max)+1, 1))
        ax.set_yticks(np.linspace(0, max(y_vals)+0.1, 10))
        ax.set_ylim(0, max(y_vals) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label='Normal Distribution'),
            Patch(facecolor='red', alpha=0.3, label='Rejection Region'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value'),
            Line2D([0], [0], color='green', lw=2, label='Test Statistic')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): p = {p0}")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p ≠ {p0} (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p > {p0} (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): p < {p0} (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Add calculation steps
        steps.append("<strong>Step 2: Sample Proportion</strong>")
        steps.append(f"• Number of successes (x): {x}")
        steps.append(f"• Sample size (n): {n}")
        steps.append(f"• Sample proportion (p̂ = x/n): {round(p_hat, 4)}")
        
        steps.append("<strong>Step 3: Standard Error Calculation</strong>")
        steps.append(f"• Standard Error = √(p₀(1-p₀)/n) = √({p0}×{round(1-p0, 4)}/{n})")
        steps.append(f"• Standard Error = {round(standard_error, 4)}")
        
        steps.append("<strong>Step 4: Z-Score Calculation</strong>")
        steps.append(f"• Z = (p̂ - p₀)/SE = ({round(p_hat, 4)} - {p0})/{round(standard_error, 4)}")
        steps.append(f"• Z-Score = {round(z_score, 4)}")
        
        steps.append("<strong>Step 5: Critical Value</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Critical Value: ±{round(critical_value, 4)} (Two-tailed)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Critical Value: {round(critical_value, 4)} (Right-tailed)")
        else:
            steps.append(f"• Critical Value: {round(critical_value, 4)} (Left-tailed)")
        
        # Decision logic
        steps.append("<strong>Step 6: Decision Rule</strong>")
        if hypothesis_type == 'two-tailed':
            reject_condition = abs(z_score) > abs(critical_value)
            steps.append(f"• Reject H₀ if |Z-Score| > |Critical Value|")
            steps.append(f"• {abs(round(z_score, 4))} {'>' if reject_condition else '<'} {abs(round(critical_value, 4))}")
        elif hypothesis_type == 'right-tailed':
            reject_condition = z_score > critical_value
            steps.append(f"• Reject H₀ if Z-Score > Critical Value")
            steps.append(f"• {round(z_score, 4)} {'>' if reject_condition else '<'} {round(critical_value, 4)}")
        else:  # left-tailed
            reject_condition = z_score < critical_value
            steps.append(f"• Reject H₀ if Z-Score < Critical Value")
            steps.append(f"• {round(z_score, 4)} {'<' if reject_condition else '>'} {round(critical_value, 4)}")
        
        # Conclusion
        conclusion = 'Reject H₀' if reject_condition else 'Fail to reject H₀'
        steps.append(f"<strong>Conclusion:</strong> {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(z_score, 4),
            'criticalValue': critical_value_display,
            'distribution': 'z-distribution',
            'conclusion': conclusion,
            'steps': steps,
            'sampleProportion': round(p_hat, 4),
            'standardError': round(standard_error, 4),
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ---------------  P-Value Method For ProPortion --------------- #

@app.route('/calculate_proportion_pvalue', methods=['POST'])
def calculate_proportion_pvalue():
    print("Received proportion p-value test request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'p0', 'alpha', 'sampleSize', 'successCount']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        p0 = float(data['p0'])
        alpha = float(data['alpha'])
        n = int(data['sampleSize'])
        x = int(data['successCount'])
        
        # Validate inputs
        if p0 < 0 or p0 > 1:
            return jsonify({'error': 'Hypothesized proportion must be between 0 and 1'}), 400
        if x < 0 or x > n:
            return jsonify({'error': 'Number of successes must be between 0 and sample size'}), 400
        
        # Calculate sample proportion and standard error
        p_hat = x / n
        standard_error = math.sqrt((p0 * (1 - p0)) / n)
        z_score = (p_hat - p0) / standard_error
        
        # Calculate p-value based on test type
        if hypothesis_type == 'two-tailed':
            p_value = 2 * (1 - norm.cdf(abs(z_score)))  # Two-tailed p-value
        elif hypothesis_type == 'right-tailed':
            p_value = 1 - norm.cdf(z_score)  # Right-tailed p-value
        else:  # left-tailed
            p_value = norm.cdf(z_score)  # Left-tailed p-value
        
        # Determine conclusion
        conclusion = 'Reject H₀' if p_value < alpha else 'Fail to reject H₀'

        # ====== Visualization Code for P-Value Method ======
        fig, ax = plt.subplots(figsize=(8, 4))

        # Calculate critical value based on alpha (for visualization only)
        if hypothesis_type == 'two-tailed':
            crit_val = norm.ppf(1 - alpha/2)
        elif hypothesis_type == 'right-tailed':
            crit_val = norm.ppf(1 - alpha)
        else:  # left-tailed
            crit_val = norm.ppf(alpha)

        # Determine plot range dynamically
        plot_margin = 0.5
        x_min = min(-4, z_score - 3, -abs(crit_val) - plot_margin)
        x_max = max(4, z_score + 3, abs(crit_val) + plot_margin)
        x_vals = np.linspace(x_min, x_max, 1000)
        y_vals = norm.pdf(x_vals)

        # Plot standard normal distribution
        ax.plot(x_vals, y_vals, 'b-', label='Standard Normal Distribution', linewidth=2)

        # Shade p-value region
        if hypothesis_type == 'two-tailed':
            left_tail = x_vals[x_vals <= -abs(z_score)]
            right_tail = x_vals[x_vals >= abs(z_score)]
            ax.fill_between(left_tail, norm.pdf(left_tail), color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
            ax.fill_between(right_tail, norm.pdf(right_tail), color='green', alpha=0.3)
        elif hypothesis_type == 'right-tailed':
            p_value_area = x_vals[x_vals >= z_score]
            ax.fill_between(p_value_area, norm.pdf(p_value_area), color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
        else:  # left-tailed
            p_value_area = x_vals[x_vals <= z_score]
            ax.fill_between(p_value_area, norm.pdf(p_value_area), color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')

        # Shade alpha region (rejection region)
        if hypothesis_type == 'two-tailed':
            alpha_left = x_vals[x_vals <= -abs(crit_val)]
            alpha_right = x_vals[x_vals >= abs(crit_val)]
            ax.fill_between(alpha_left, norm.pdf(alpha_left), color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.fill_between(alpha_right, norm.pdf(alpha_right), color='orange', alpha=0.2)
            # Draw CV lines
            ax.plot([-crit_val, -crit_val], [0, norm.pdf(-crit_val)], color='red', linestyle='--', linewidth=1.5)
            ax.plot([crit_val, crit_val], [0, norm.pdf(crit_val)], color='red', linestyle='--', linewidth=1.5)
        else:
            alpha_area = x_vals[x_vals >= crit_val] if hypothesis_type == 'right-tailed' else x_vals[x_vals <= crit_val]
            ax.fill_between(alpha_area, norm.pdf(alpha_area), color='orange', alpha=0.2, label=f'α region ({alpha})')
            # Draw CV line
            ax.plot([crit_val, crit_val], [0, norm.pdf(crit_val)], color='red', linestyle='--', linewidth=1.5)

        # Plot test statistic line
        ax.plot([z_score, z_score], [0, norm.pdf(z_score)], color='green', linestyle='-', linewidth=2)
        ts_y_pos = norm.pdf(z_score) + 0.02

        # Label positioning
        if hypothesis_type == 'two-tailed':
            # Test stat label
            ax.text(z_score - 0.1, ts_y_pos, f'Z-Score: {z_score:.2f}', ha='right', va='bottom', color='green')
            # Critical value labels
            ax.text(-crit_val + 0.1, norm.pdf(-crit_val) + 0.01, f'CV: -{abs(crit_val):.2f}', ha='left', va='bottom', color='red')
            ax.text(crit_val - 0.1, norm.pdf(crit_val) + 0.01, f'CV: {crit_val:.2f}', ha='right', va='bottom', color='red')
        else:
            # For one-tailed tests, determine label positions
            if (hypothesis_type == 'right-tailed' and z_score > crit_val) or \
            (hypothesis_type == 'left-tailed' and z_score < crit_val):
                # Test stat in rejection region
                ts_ha = 'left'
                ts_offset = 0.1
                cv_ha = 'right'
                cv_offset = -0.1
            else:
                # Test stat not in rejection region
                ts_ha = 'right'
                ts_offset = -0.1
                cv_ha = 'left'
                cv_offset = 0.1
            
            # Test stat label
            ax.text(z_score + ts_offset, ts_y_pos, f'Z-Score: {z_score:.2f}', ha=ts_ha, va='bottom', color='green')
            # Critical value label
            ax.text(crit_val + cv_offset, norm.pdf(crit_val) + 0.01, f'CV: {crit_val:.2f}', ha=cv_ha, va='bottom', color='red')

        # Formatting
        ax.set_title('P-Value Visualization (Proportion Test)', fontsize=14, pad=20)
        ax.set_xlabel('Z-Score', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.arange(int(x_min), int(x_max)+1, 1))
        ax.set_yticks(np.linspace(0, max(y_vals)+0.1, 10))
        ax.set_ylim(0, max(y_vals) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label='Standard Normal'),
            Patch(facecolor='green', alpha=0.3, label=f'p-value ({p_value:.4f})'),
            Patch(facecolor='orange', alpha=0.2, label=f'α region ({alpha})'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic ({z_score:.2f})'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value(s)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Hypothesis setup
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): p = {p0}")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p ≠ {p0} (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p > {p0} (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): p < {p0} (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Sample calculations
        steps.append("<strong>Step 2: Sample Statistics</strong>")
        steps.append(f"• Number of successes (x): {x}")
        steps.append(f"• Sample size (n): {n}")
        steps.append(f"• Sample proportion (p̂ = x/n): {round(p_hat, 4)}")
        
        # Standard error and Z-score
        steps.append("<strong>Step 3: Standard Error & Z-Score</strong>")
        steps.append(f"• Standard Error √(p₀(1-p₀)/n): {round(standard_error, 4)}")
        steps.append(f"• Z-Score: (p̂ - p₀)/SE = {round(z_score, 4)}")
        
        # P-value calculation
        steps.append("<strong>Step 4: P-Value Calculation</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Two-tailed p-value: 2 × P(Z ≥ |{round(z_score, 4)}|) = {round(p_value, 6)}")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Right-tailed p-value: P(Z ≥ {round(z_score, 4)}) = {round(p_value, 6)}")
        else:
            steps.append(f"• Left-tailed p-value: P(Z ≤ {round(z_score, 4)}) = {round(p_value, 6)}")
        
        # Decision rule
        steps.append("<strong>Step 5: Decision Rule</strong>")
        steps.append(f"• Compare p-value ({round(p_value, 6)}) with α ({alpha})")
        steps.append(f"• {'p-value ≤ α → Reject H₀' if p_value <= alpha else 'p-value > α → Fail to reject H₀'}")
        
        # Prepare results
        result = {
            'testStatistic': round(z_score, 4),
            'pValue': round(p_value, 6),
            'alpha': alpha,
            'conclusion': conclusion,
            'steps': steps,
            'sampleProportion': round(p_hat, 4),
            'standardError': round(standard_error, 4),
            'method': 'p-value',
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------  Confidence Interval Method For ProPortion --------------- #

@app.route('/calculate_proportion_ci', methods=['POST'])
def calculate_proportion_ci():
    print("Received proportion confidence interval request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['confidenceLevel', 'sampleSize', 'successCount']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        confidence_level = float(data['confidenceLevel']) / 100  # Convert from percentage to decimal
        n = int(data['sampleSize'])
        x = int(data['successCount'])
        
        # Validate inputs
        if confidence_level <= 0 or confidence_level >= 1:
            return jsonify({'error': 'Confidence level must be between 0 and 100'}), 400
        if x < 0 or x > n:
            return jsonify({'error': 'Number of successes must be between 0 and sample size'}), 400
        if n <= 0:
            return jsonify({'error': 'Sample size must be positive'}), 400
        
        # Calculate sample proportion
        p_hat = x / n
        
        # Calculate critical value (z*)
        alpha = 1 - confidence_level
        z_star = norm.ppf(1 - alpha/2)
        
        # Calculate standard error
        standard_error = math.sqrt((p_hat * (1 - p_hat)) / n)
        
        # Calculate margin of error
        margin_of_error = z_star * standard_error
        
        # Calculate confidence interval
        lower_bound = max(0, p_hat - margin_of_error)  # Bound at 0
        upper_bound = min(1, p_hat + margin_of_error)  # Bound at 1
        
        # Initialize explanation steps
        steps = []
        
        # Basic information
        steps.append(f"<strong>Step 1: Input Parameters</strong>")
        steps.append(f"• Confidence Level: {confidence_level*100}%")
        steps.append(f"• Sample Size (n): {n}")
        steps.append(f"• Number of Successes (x): {x}")
        
        # Sample proportion
        steps.append("<strong>Step 2: Sample Proportion</strong>")
        steps.append(f"• p̂ = x/n = {x}/{n} = {round(p_hat, 4)}")
        
        # Critical value
        steps.append("<strong>Step 3: Critical Value</strong>")
        steps.append(f"• For {confidence_level*100}% CI, α = {round(alpha, 4)}")
        steps.append(f"• z* (critical value) = {round(z_star, 4)}")
        
        # Standard error
        steps.append("<strong>Step 4: Standard Error</strong>")
        steps.append(f"• SE = √(p̂(1-p̂)/n) = √({round(p_hat,4)}×{round(1-p_hat,4)}/{n})")
        steps.append(f"• SE = {round(standard_error, 6)}")
        
        # Margin of error
        steps.append("<strong>Step 5: Margin of Error</strong>")
        steps.append(f"• ME = z* × SE = {round(z_star,4)} × {round(standard_error,6)}")
        steps.append(f"• ME = {round(margin_of_error, 6)}")
        
        # Confidence interval
        steps.append("<strong>Step 6: Confidence Interval</strong>")
        steps.append(f"• CI = p̂ ± ME = {round(p_hat,4)} ± {round(margin_of_error,4)}")
        steps.append(f"• Lower Bound = max(0, {round(p_hat,4)} - {round(margin_of_error,4)}) = {round(lower_bound, 4)}")
        steps.append(f"• Upper Bound = min(1, {round(p_hat,4)} + {round(margin_of_error,4)}) = {round(upper_bound, 4)}")
        
        # Interpretation
        steps.append("<strong>Step 7: Interpretation</strong>")
        steps.append(f"We are {confidence_level*100}% confident that the true population proportion falls between {round(lower_bound, 4)} and {round(upper_bound, 4)}")
        
        # Prepare results
        result = {
            'sampleProportion': round(p_hat, 4),
            'confidenceLevel': confidence_level,
            'criticalValue': round(z_star, 4),
            'standardError': round(standard_error, 6),
            'marginOfError': round(margin_of_error, 6),
            'lowerBound': round(lower_bound, 4),
            'upperBound': round(upper_bound, 4),
            'steps': steps,
            'method': 'confidence-interval'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ---------------  Teaditional Method For Variance --------------- #

@app.route('/calculate_variance_traditional', methods=['POST'])
def calculate_variance_traditional():
    print("Received variance test request (traditional method)!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'populationVariance', 'alpha', 'sampleSize', 'sampleVariance']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        sigma0_squared = float(data['populationVariance'])
        alpha = float(data['alpha'])
        n = int(data['sampleSize'])
        s_squared = float(data['sampleVariance'])
        
        # Validate inputs
        if sigma0_squared <= 0:
            return jsonify({'error': 'Population variance must be positive'}), 400
        if s_squared < 0:
            return jsonify({'error': 'Sample variance cannot be negative'}), 400
        if n < 2:
            return jsonify({'error': 'Sample size must be at least 2'}), 400
        if alpha <= 0 or alpha >= 1:
            return jsonify({'error': 'Significance level must be between 0 and 1'}), 400
        
        # Calculate chi-square test statistic
        chi_square = ((n - 1) * s_squared) / sigma0_squared
        df = n - 1  # degrees of freedom
        
        # Determine critical values based on test type
        if hypothesis_type == 'two-tailed':
            lower_critical = chi2.ppf(alpha/2, df)
            upper_critical = chi2.ppf(1 - alpha/2, df)
            critical_value_display = f"({round(lower_critical, 4)}, {round(upper_critical, 4)})"
        elif hypothesis_type == 'right-tailed':
            critical_value = chi2.ppf(1 - alpha, df)
            critical_value_display = round(critical_value, 4)
        else:  # left-tailed
            critical_value = chi2.ppf(alpha, df)
            critical_value_display = round(critical_value, 4)

        # ===== Create visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))

        # Determine plot range dynamically
        plot_margin = 10
        x_min = 0
        x_max = max(chi_square + 10, critical_value if hypothesis_type != 'two-tailed' else upper_critical) + plot_margin
        x = np.linspace(x_min, x_max, 1000)
        y = chi2.pdf(x, df)

        # Plot chi-square distribution
        ax.plot(x, y, 'b-', label=f'Chi-Square Distribution (df={df})', linewidth=2)

        # Shade rejection region under the curve
        if hypothesis_type == 'two-tailed':
            x_left = x[x <= lower_critical]
            x_right = x[x >= upper_critical]
            
            # Shade rejection regions
            ax.fill_between(x_left, chi2.pdf(x_left, df), color='red', alpha=0.3, label='Rejection Region')
            ax.fill_between(x_right, chi2.pdf(x_right, df), color='red', alpha=0.3)
            
            # Draw critical value lines
            ax.plot([lower_critical, lower_critical], [0, chi2.pdf(lower_critical, df)], 
                    color='red', linestyle='--', linewidth=1.5)
            ax.plot([upper_critical, upper_critical], [0, chi2.pdf(upper_critical, df)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Calculate positions for CV and TS labels
            y_cv_lower = chi2.pdf(lower_critical, df) + 0.005
            y_cv_upper = chi2.pdf(upper_critical, df) + 0.005
            y_ts = chi2.pdf(chi_square, df) + 0.005
            
            # Determine if TS is too close to CV (adjust label positions if needed)
            ts_near_lower_cv = abs(chi_square - lower_critical) < 2.0  # Threshold distance
            ts_near_upper_cv = abs(chi_square - upper_critical) < 2.0
            
            # Place CV labels (default positions)
            lower_cv_ha = 'right'
            lower_cv_x_offset = -0.5
            upper_cv_ha = 'left'
            upper_cv_x_offset = 0.5
            
            # Place TS label (default position)
            ts_ha = 'left'
            ts_x_offset = 0.5
            
            # Adjust if TS is near lower CV
            if ts_near_lower_cv:
                if chi_square < lower_critical:
                    ts_ha = 'right'
                    ts_x_offset = -0.5
                else:
                    lower_cv_ha = 'left'
                    lower_cv_x_offset = 0.5
            
            # Adjust if TS is near upper CV
            if ts_near_upper_cv:
                if chi_square > upper_critical:
                    ts_ha = 'left'
                    ts_x_offset = 0.5
                else:
                    upper_cv_ha = 'right'
                    upper_cv_x_offset = -0.5
            
            # Add CV labels (with dynamic positioning)
            ax.text(lower_critical + lower_cv_x_offset, y_cv_lower, 
                    f'CV: {lower_critical:.2f}', ha=lower_cv_ha, va='bottom', color='red')
            ax.text(upper_critical + upper_cv_x_offset, y_cv_upper, 
                    f'CV: {upper_critical:.2f}', ha=upper_cv_ha, va='bottom', color='red')
            
            # Add TS label (if not inside rejection regions)
            if not (chi_square <= lower_critical or chi_square >= upper_critical):
                ax.text(chi_square + ts_x_offset, y_ts, 
                        f'TS: {chi_square:.2f}', ha=ts_ha, va='bottom', color='blue')

        elif hypothesis_type == 'left-tailed':
            x_crit = x[x <= critical_value]
            ax.fill_between(x_crit, chi2.pdf(x_crit, df), color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, chi2.pdf(critical_value, df)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions
            if chi_square < critical_value:
                # Test stat is in rejection region
                ts_ha = 'right'
                ts_x_offset = -0.5
                cv_ha = 'left'
                cv_x_offset = 0.5
            else:
                # Test stat is not in rejection region
                ts_ha = 'left'
                ts_x_offset = 0.5
                cv_ha = 'right'
                cv_x_offset = -0.5
            
            ax.text(critical_value + cv_x_offset, chi2.pdf(critical_value, df) + 0.005, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        else:  # right-tailed
            x_crit = x[x >= critical_value]
            ax.fill_between(x_crit, chi2.pdf(x_crit, df), color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, chi2.pdf(critical_value, df)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions
            if chi_square > critical_value:
                # Test stat is in rejection region
                ts_ha = 'left'
                ts_x_offset = 0.5
                cv_ha = 'right'
                cv_x_offset = -0.5
            else:
                # Test stat is not in rejection region
                ts_ha = 'right'
                ts_x_offset = -0.5
                cv_ha = 'left'
                cv_x_offset = 0.5
            
            ax.text(critical_value + cv_x_offset, chi2.pdf(critical_value, df) + 0.005, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        # Plot test statistic with dynamic labeling
        ax.plot([chi_square, chi_square], [0, chi2.pdf(chi_square, df)], color='green', linestyle='-', linewidth=2)
        ts_y_pos = chi2.pdf(chi_square, df) + 0.01

        if hypothesis_type == 'two-tailed':
            ax.text(chi_square - 0.5, ts_y_pos, f'Test Stat: {chi_square:.2f}', ha='right', va='bottom', color='green')
        else:
            ax.text(chi_square + ts_x_offset, ts_y_pos, 
                    f'Test Stat: {chi_square:.2f}', 
                    ha=ts_ha, va='bottom', color='green')

        # Formatting
        ax.set_title('Variance Hypothesis Test', fontsize=14, pad=20)
        ax.set_xlabel('Chi-Square Value', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_ylim(0, max(y) + 0.05)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label=f'Chi-Square (df={df})'),
            Patch(facecolor='red', alpha=0.3, label='Rejection Region'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value'),
            Line2D([0], [0], color='green', lw=2, label='Test Statistic')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): σ² = {sigma0_squared}")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ² ≠ {sigma0_squared} (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ² > {sigma0_squared} (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): σ² < {sigma0_squared} (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Add calculation steps
        steps.append("<strong>Step 2: Sample Information</strong>")
        steps.append(f"• Sample size (n): {n}")
        steps.append(f"• Sample variance (s²): {round(s_squared, 4)}")
        steps.append(f"• Degrees of freedom (df = n-1): {df}")
        
        steps.append("<strong>Step 3: Chi-Square Test Statistic</strong>")
        steps.append(f"• χ² = (n-1)s²/σ₀² = ({n}-1)×{round(s_squared,4)}/{sigma0_squared}")
        steps.append(f"• Test Statistic = {round(chi_square, 4)}")
        
        steps.append("<strong>Step 4: Critical Value(s)</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Lower Critical Value (χ²{{{1-(alpha/2)}, {df}}}): {round(lower_critical, 4)}")
            steps.append(f"• Upper Critical Value (χ²{{{alpha/2}, {df}}}): {round(upper_critical, 4)}")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Critical Value (χ²{{{alpha}, {df}}}): {round(critical_value, 4)}")
        else:
            steps.append(f"• Critical Value (χ²{{{1-alpha}, {df}}}): {round(critical_value, 4)}")
        
        # Decision logic
        steps.append("<strong>Step 5: Decision Rule</strong>")
        if hypothesis_type == 'two-tailed':
            reject_condition = (chi_square < lower_critical) or (chi_square > upper_critical)
            steps.append(f"• Reject H₀ if χ² < {round(lower_critical, 4)} or χ² > {round(upper_critical, 4)}")
            steps.append(f"• {round(chi_square, 4)} is {'inside' if reject_condition else 'outside'} the critical region")
        elif hypothesis_type == 'right-tailed':
            reject_condition = chi_square > critical_value
            steps.append(f"• Reject H₀ if χ² > {round(critical_value, 4)}")
            steps.append(f"• {round(chi_square, 4)} {'>' if reject_condition else '<'} {round(critical_value, 4)}")
        else:  # left-tailed
            reject_condition = chi_square < critical_value
            steps.append(f"• Reject H₀ if χ² < {round(critical_value, 4)}")
            steps.append(f"• {round(chi_square, 4)} {'<' if reject_condition else '>'} {round(critical_value, 4)}")
        
        # Conclusion
        conclusion = 'Reject H₀' if reject_condition else 'Fail to reject H₀'
        steps.append(f"<strong>Conclusion:</strong> {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(chi_square, 4),
            'criticalValue': critical_value_display,
            'degreesOfFreedom': df,
            'distribution': 'chi-square',
            'conclusion': conclusion,
            'steps': steps,
            'sampleVariance': round(s_squared, 4),
            'populationVariance': sigma0_squared,
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------- P-Value Method For Variance --------------- #

@app.route('/calculate_variance_pvalue', methods=['POST'])
def calculate_variance_pvalue():
    print("Received variance test request (p-value method)!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'populationVariance', 'alpha', 'sampleSize', 'sampleVariance']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        sigma0_squared = float(data['populationVariance'])
        alpha = float(data['alpha'])
        n = int(data['sampleSize'])
        s_squared = float(data['sampleVariance'])
        
        # Validate inputs
        if sigma0_squared <= 0:
            return jsonify({'error': 'Population variance must be positive'}), 400
        if s_squared < 0:
            return jsonify({'error': 'Sample variance cannot be negative'}), 400
        if n < 2:
            return jsonify({'error': 'Sample size must be at least 2'}), 400
        if alpha <= 0 or alpha >= 1:
            return jsonify({'error': 'Significance level must be between 0 and 1'}), 400
        
        # Calculate chi-square test statistic
        chi_square = ((n - 1) * s_squared) / sigma0_squared
        df = n - 1  # degrees of freedom
        
        # Calculate p-value based on test type
        if hypothesis_type == 'two-tailed':
            p_value = 2 * min(chi2.cdf(chi_square, df), 1 - chi2.cdf(chi_square, df))
        elif hypothesis_type == 'right-tailed':
            p_value = 1 - chi2.cdf(chi_square, df)
        else:  # left-tailed
            p_value = chi2.cdf(chi_square, df)
        
        # Determine conclusion
        conclusion = 'Reject H₀' if p_value < alpha else 'Fail to reject H₀'

        # ====== Visualization Code ======
        fig, ax = plt.subplots(figsize=(8, 4))

        # Determine plot range dynamically
        x_min = max(0, chi2.ppf(0.001, df))  # Chi-square starts at 0
        x_max = max(4, chi_square + 3, chi2.ppf(0.999, df))  # Use 99.9th percentile as upper bound
        x_vals = np.linspace(x_min, x_max, 1000)
        y_vals = chi2.pdf(x_vals, df)

        # Plot chi-square distribution
        ax.plot(x_vals, y_vals, 'b-', label=f'χ²-Distribution (df={df})', linewidth=2)

        # Shade p-value region
        if hypothesis_type == 'two-tailed':
            # Always shade both tails that make up the p-value
            lower_p = chi2.ppf(p_value/2, df)  # Left tail critical value
            upper_p = chi2.ppf(1 - p_value/2, df)  # Right tail critical value
            
            # Shade left tail
            p_value_area_left = x_vals[x_vals <= lower_p]
            ax.fill_between(p_value_area_left, chi2.pdf(p_value_area_left, df), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
            
            # Shade right tail
            p_value_area_right = x_vals[x_vals >= upper_p]
            ax.fill_between(p_value_area_right, chi2.pdf(p_value_area_right, df), 
                            color='green', alpha=0.3)
            
        elif hypothesis_type == 'right-tailed':
            p_value_area = x_vals[x_vals >= chi_square]
            ax.fill_between(p_value_area, chi2.pdf(p_value_area, df), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
            
        else:  # left-tailed
            p_value_area = x_vals[x_vals <= chi_square]
            ax.fill_between(p_value_area, chi2.pdf(p_value_area, df), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')

        # Shade alpha region (rejection region)
        if hypothesis_type == 'two-tailed':
            lower_crit = chi2.ppf(alpha/2, df)
            upper_crit = chi2.ppf(1 - alpha/2, df)
            
            alpha_lower = x_vals[x_vals <= lower_crit]
            alpha_upper = x_vals[x_vals >= upper_crit]
            
            ax.fill_between(alpha_lower, chi2.pdf(alpha_lower, df), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.fill_between(alpha_upper, chi2.pdf(alpha_upper, df), 
                            color='orange', alpha=0.2)
            
            # Draw critical value lines
            ax.plot([lower_crit, lower_crit], [0, chi2.pdf(lower_crit, df)], 
                    color='red', linestyle='--', linewidth=1.5)
            ax.plot([upper_crit, upper_crit], [0, chi2.pdf(upper_crit, df)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Label critical values
            ax.text(lower_crit - 0.1, chi2.pdf(lower_crit, df) + 0.01, 
                    f'Lower CV: {lower_crit:.2f}', ha='right', va='bottom', color='red')
            ax.text(upper_crit + 0.1, chi2.pdf(upper_crit, df) + 0.01, 
                    f'Upper CV: {upper_crit:.2f}', ha='left', va='bottom', color='red')
            
        else:
            crit_val = chi2.ppf(1 - alpha, df) if hypothesis_type == 'right-tailed' else chi2.ppf(alpha, df)
            alpha_area = x_vals[x_vals >= crit_val] if hypothesis_type == 'right-tailed' else x_vals[x_vals <= crit_val]
            
            ax.fill_between(alpha_area, chi2.pdf(alpha_area, df), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.plot([crit_val, crit_val], [0, chi2.pdf(crit_val, df)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Label critical value
            cv_offset = 0.1 if hypothesis_type == 'right-tailed' else -0.1
            cv_ha = 'left' if hypothesis_type == 'right-tailed' else 'right'
            ax.text(crit_val + cv_offset, chi2.pdf(crit_val, df) + 0.01, 
                    f'CV: {crit_val:.2f}', ha=cv_ha, va='bottom', color='red')

        # Plot test statistic line
        ax.plot([chi_square, chi_square], [0, chi2.pdf(chi_square, df)], 
                color='green', linestyle='-', linewidth=2)
        ts_y_pos = chi2.pdf(chi_square, df) + 0.02

        # Label test statistic
        if hypothesis_type == 'two-tailed':
            chi_ha = 'left' if chi_square >= df else 'right'
            chi_offset = 0.1 if chi_square >= df else -0.1
        else:
            if (hypothesis_type == 'right-tailed' and chi_square > crit_val) or \
            (hypothesis_type == 'left-tailed' and chi_square < crit_val):
                # In rejection region
                chi_ha = 'left' if hypothesis_type == 'right-tailed' else 'right'
                chi_offset = 0.1 if hypothesis_type == 'right-tailed' else -0.1
            else:
                # Not in rejection region
                chi_ha = 'right' if hypothesis_type == 'right-tailed' else 'left'
                chi_offset = -0.1 if hypothesis_type == 'right-tailed' else 0.1

        ax.text(chi_square + chi_offset, ts_y_pos,
                f'χ²-Stat: {chi_square:.2f}', 
                ha=chi_ha, va='bottom', color='green')

        # Formatting
        ax.set_title('Chi-Square Test for Variance (P-Value Method)', fontsize=14, pad=20)
        ax.set_xlabel('Chi-Square Value', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.linspace(0, x_max, min(10, int(x_max)+1)))
        ax.set_yticks(np.linspace(0, max(y_vals)+0.1, 10))
        ax.set_ylim(0, max(y_vals) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label=f'χ²-Distribution (df={df})'),
            Patch(facecolor='green', alpha=0.3, label=f'p-value ({p_value:.4f})'),
            Patch(facecolor='orange', alpha=0.2, label=f'α region ({alpha})'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic ({chi_square:.2f})'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value(s)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): σ² = {sigma0_squared}")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ² ≠ {sigma0_squared} (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ² > {sigma0_squared} (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): σ² < {sigma0_squared} (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Add calculation steps
        steps.append("<strong>Step 2: Sample Information</strong>")
        steps.append(f"• Sample size (n): {n}")
        steps.append(f"• Sample variance (s²): {round(s_squared, 4)}")
        steps.append(f"• Degrees of freedom (df = n-1): {df}")
        
        steps.append("<strong>Step 3: Chi-Square Test Statistic</strong>")
        steps.append(f"• χ² = (n-1)s²/σ₀² = ({n}-1)×{round(s_squared,4)}/{sigma0_squared}")
        steps.append(f"• Test Statistic = {round(chi_square, 4)}")
        
        steps.append("<strong>Step 4: P-Value Calculation</strong>")
        if hypothesis_type == 'two-tailed':
            tail_prob = min(chi2.cdf(chi_square, df), 1 - chi2.cdf(chi_square, df))
            steps.append(f"• P-value = 2 × min(P(χ² ≤ {round(chi_square, 4)}), P(χ² ≥ {round(chi_square, 4)}))")
            steps.append(f"• P-value = 2 × {round(tail_prob, 4)} = {round(p_value, 4)}")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• P-value = P(χ² ≥ {round(chi_square, 4)})")
            steps.append(f"• P-value = {round(p_value, 4)}")
        else:
            steps.append(f"• P-value = P(χ² ≤ {round(chi_square, 4)})")
            steps.append(f"• P-value = {round(p_value, 4)}")
        
        # Decision logic
        steps.append("<strong>Step 5: Decision Rule</strong>")
        steps.append(f"• Reject H₀ if p-value < α ({alpha})")
        steps.append(f"• {round(p_value, 4)} {'<' if p_value < alpha else '>'} {alpha}")
        
        steps.append(f"<strong>Conclusion:</strong> {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(chi_square, 4),
            'pValue': round(p_value, 6),
            'degreesOfFreedom': df,
            'alpha': alpha,
            'distribution': 'chi-square',
            'conclusion': conclusion,
            'steps': steps,
            'sampleVariance': round(s_squared, 4),
            'populationVariance': sigma0_squared,
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------- Confidence Interval Method For Variance --------------- #

@app.route('/calculate_variance_ci', methods=['POST'])
def calculate_variance_ci():
    print("Received variance confidence interval request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['confidenceLevel', 'sampleSize', 'sampleVariance']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        confidence_level = float(data['confidenceLevel']) / 100  # Convert from percentage to decimal
        n = int(data['sampleSize'])
        s_squared = float(data['sampleVariance'])
        
        # Validate inputs
        if confidence_level <= 0 or confidence_level >= 1:
            return jsonify({'error': 'Confidence level must be between 0 and 100'}), 400
        if s_squared < 0:
            return jsonify({'error': 'Sample variance cannot be negative'}), 400
        if n < 2:
            return jsonify({'error': 'Sample size must be at least 2'}), 400
        
        # Calculate degrees of freedom
        df = n - 1
        
        # Calculate critical values (chi-square)
        alpha = 1 - confidence_level
        chi2_lower = chi2.ppf(alpha/2, df)
        print(chi2_lower)
        chi2_upper = chi2.ppf(1 - alpha/2, df)
        print(chi2_upper)
        
        # Calculate confidence interval bounds
        lower_bound = (df * s_squared) / chi2_upper
        upper_bound = (df * s_squared) / chi2_lower
        
        # Initialize explanation steps
        steps = []
        
        # Basic information
        steps.append(f"<strong>Step 1: Input Parameters</strong>")
        steps.append(f"• Confidence Level: {confidence_level*100}%")
        steps.append(f"• Sample Size (n): {n}")
        steps.append(f"• Sample Variance (s²): {round(s_squared, 4)}")
        
        # Degrees of freedom
        steps.append("<strong>Step 2: Degrees of Freedom</strong>")
        steps.append(f"• df = n - 1 = {n} - 1 = {df}")
        
        # Critical values
        steps.append("<strong>Step 3: Critical Values</strong>")
        steps.append(f"• For {confidence_level*100}% CI, α = {round(alpha, 4)}")
        steps.append(f"• χ² lower (χ²{{{1-(alpha/2)}, {df}}}) = {round(chi2_lower, 4)}")
        steps.append(f"• χ² upper (χ²{{{round(alpha/2, 4)}, {df}}}) = {round(chi2_upper, 4)}")
    
        # Confidence interval calculation
        steps.append("<strong>Step 4: Confidence Interval Calculation</strong>")
        steps.append(f"• Lower Bound = (df × s²)/(χ² upper) = ({df}×{round(s_squared,4)})/{round(chi2_upper,4)}")
        steps.append(f"• Upper Bound = (df × s²)/(χ² lower) = ({df}×{round(s_squared,4)})/{round(chi2_lower,4)}")
        
        # Confidence interval results
        steps.append("<strong>Step 5: Confidence Interval</strong>")
        steps.append(f"• Variance CI: ({round(lower_bound, 4)}, {round(upper_bound, 4)})")
        
        # Interpretation
        steps.append("<strong>Step 6: Interpretation</strong>")
        steps.append(f"We are {confidence_level*100}% confident that the true population variance falls between {round(lower_bound, 4)} and {round(upper_bound, 4)}")
        
        # Prepare results
        result = {
            'sampleVariance': round(s_squared, 4),
            'confidenceLevel': confidence_level,
            'degreesOfFreedom': df,
            'chi2Lower': round(chi2_lower, 4),
            'chi2Upper': round(chi2_upper, 4),
            'lowerBound': round(lower_bound, 4),
            'upperBound': round(upper_bound, 4),
            'steps': steps,
            'method': 'confidence-interval'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------  Traditional Method For Difference Between Means --------------- #

@app.route('/calculate_diff_means', methods=['POST'])
def calculate_diff_means():
    print("Received request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        # Validate required fields
        required_fields = ['hypothesisType', 'x1', 'x2', 'alpha', 'n1', 'n2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        x_bar1 = float(data['x1'])
        x_bar2 = float(data['x2'])
        alpha = float(data['alpha'])
        n1 = int(data['n1'])
        n2 = int(data['n2'])
        sigma1 = float(data['sigma1']) if data.get('sigma1') else None
        sigma2 = float(data['sigma2']) if data.get('sigma2') else None
        s1 = float(data['s1']) if data.get('s1') else None
        s2 = float(data['s2']) if data.get('s2') else None

        if not sigma1 and not s1:
            return jsonify({'error': 'First sample standard deviation required when population σ₁ is unknown'}), 400
        
        if not sigma2 and not s2:
            return jsonify({'error': 'Second sample standard deviation required when population σ₂ is unknown'}), 400
        
        # Perform calculations
        if sigma1 and sigma2:  # Z-test (σ₁ and σ₂ are known)
            standard_error = math.sqrt((sigma1**2/n1) + (sigma2**2/n2))
            z_score = (x_bar1 - x_bar2) / standard_error
            if hypothesis_type == 'two-tailed':
                critical_value = norm.ppf(1 - alpha/2)
                critical_value_display = f"±{round(abs(critical_value), 4)}"
            elif hypothesis_type == 'right-tailed':
                critical_value = norm.ppf(1 - alpha)
                critical_value_display = round(critical_value, 4)
            else:  # left-tailed
                critical_value = norm.ppf(alpha)
                critical_value_display = round(critical_value, 4)
            test_statistic = z_score
            distribution = 'z-distribution'
        elif (not sigma1 and not sigma2) and 0.5 <= s1/s2 <= 2:  # Pooled t-test
            sp = math.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
            standard_error = sp * math.sqrt((1/n1) + (1/n2))
            t_score = (x_bar1 - x_bar2) / standard_error
            
            if hypothesis_type == 'two-tailed':
                critical_value = t.ppf(1 - alpha/2, df=n1+n2-2)
                critical_value_display = f"±{round(abs(critical_value), 4)}"
            elif hypothesis_type == 'right-tailed':
                critical_value = t.ppf(1 - alpha, df=n1+n2-2)
                critical_value_display = round(critical_value, 4)
            else:  # left-tailed
                critical_value = t.ppf(alpha, df=n1+n2-2)
                critical_value_display = round(critical_value, 4)
                
            test_statistic = t_score
            distribution = 't-distribution'
        elif (not sigma1 and not sigma2):  # Welch's t-test
            standard_error = math.sqrt((s1**2/n1) + (s2**2/n2))
            t_score = (x_bar1 - x_bar2) / standard_error
            df = ((s1**2/n1) + (s2**2/n2))**2 / (((s1**2/n1)**2/(n1-1)) + ((s2**2/n2)**2/(n2-1)))
            
            if hypothesis_type == 'two-tailed':
                critical_value = t.ppf(1 - alpha/2, df=df)
                critical_value_display = f"±{round(abs(critical_value), 4)}"
            elif hypothesis_type == 'right-tailed':
                critical_value = t.ppf(1 - alpha, df=df)
                critical_value_display = round(critical_value, 4)
            else:  # left-tailed
                critical_value = t.ppf(alpha, df=df)
                critical_value_display = round(critical_value, 4)
                
            test_statistic = t_score
            distribution = 't-distribution'

        # ===== Create visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))

        # Determine distribution parameters
        if distribution == 'z-distribution':
            # For Z-test
            x_min = min(-4, test_statistic - 3, -abs(critical_value) - 0.5)
            x_max = max(4, test_statistic + 3, abs(critical_value) + 0.5)
            x_vals = np.linspace(x_min, x_max, 1000)
            y_vals = norm.pdf(x_vals)
            dist_label = 'Standard Normal (Z) Distribution'
        else:
            # For T-tests
            if 'df' in locals():  # Welch's t-test
                df_value = df
            else:  # Pooled t-test
                df_value = n1 + n2 - 2
            
            x_min = min(-4, test_statistic - 3, -abs(critical_value) - 0.5)
            x_max = max(4, test_statistic + 3, abs(critical_value) + 0.5)
            x_vals = np.linspace(x_min, x_max, 1000)
            y_vals = t.pdf(x_vals, df=df_value)
            dist_label = f"t-Distribution (df={df_value:.2f})"

        # Plot the distribution
        ax.plot(x_vals, y_vals, 'b-', label=dist_label, linewidth=2)

        # Shade rejection region based on test type
        if hypothesis_type == 'two-tailed':
            # Two-tailed test shading
            x_left = x_vals[x_vals <= -abs(critical_value)]
            x_right = x_vals[x_vals >= abs(critical_value)]
            
            if distribution == 'z-distribution':
                ax.fill_between(x_left, norm.pdf(x_left), color='red', alpha=0.3, label='Rejection Region')
                ax.fill_between(x_right, norm.pdf(x_right), color='red', alpha=0.3)
                ax.plot([-critical_value, -critical_value], [0, norm.pdf(-critical_value)], 
                        color='red', linestyle='--', linewidth=1.5)
                ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], 
                        color='red', linestyle='--', linewidth=1.5)
            else:
                ax.fill_between(x_left, t.pdf(x_left, df=df_value), color='red', alpha=0.3, label='Rejection Region')
                ax.fill_between(x_right, t.pdf(x_right, df=df_value), color='red', alpha=0.3)
                ax.plot([-critical_value, -critical_value], [0, t.pdf(-critical_value, df=df_value)], 
                        color='red', linestyle='--', linewidth=1.5)
                ax.plot([critical_value, critical_value], [0, t.pdf(critical_value, df=df_value)], 
                        color='red', linestyle='--', linewidth=1.5)
            
            # Label critical values
            if distribution == 'z-distribution':
                left_height = norm.pdf(-critical_value)
                right_height = norm.pdf(critical_value)
            else:
                left_height = t.pdf(-critical_value, df=df_value)
                right_height = t.pdf(critical_value, df=df_value)
            
            ax.text(-critical_value - 0.1, left_height + 0.01, 
                    f'CV: -{abs(critical_value):.2f}', ha='right', va='bottom', color='red')
            ax.text(critical_value + 0.1, right_height + 0.01, 
                    f'CV: {critical_value:.2f}', ha='left', va='bottom', color='red')

        elif hypothesis_type == 'left-tailed':
            # Left-tailed test shading
            x_crit = x_vals[x_vals <= critical_value]
            
            if distribution == 'z-distribution':
                ax.fill_between(x_crit, norm.pdf(x_crit), color='red', alpha=0.3, label='Rejection Region')
                ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], 
                        color='red', linestyle='--', linewidth=1.5)
                crit_height = norm.pdf(critical_value)
            else:
                ax.fill_between(x_crit, t.pdf(x_crit, df=df_value), color='red', alpha=0.3, label='Rejection Region')
                ax.plot([critical_value, critical_value], [0, t.pdf(critical_value, df=df_value)], 
                        color='red', linestyle='--', linewidth=1.5)
                crit_height = t.pdf(critical_value, df=df_value)
            
            # Position labels
            if test_statistic < critical_value:
                ts_ha = 'right'
                ts_x_offset = -0.1
                cv_ha = 'left'
                cv_x_offset = 0.1
            else:
                ts_ha = 'left'
                ts_x_offset = 0.1
                cv_ha = 'right'
                cv_x_offset = -0.1
            
            ax.text(critical_value + cv_x_offset, crit_height + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        else:  # right-tailed
            # Right-tailed test shading
            x_crit = x_vals[x_vals >= critical_value]
            
            if distribution == 'z-distribution':
                ax.fill_between(x_crit, norm.pdf(x_crit), color='red', alpha=0.3, label='Rejection Region')
                ax.plot([critical_value, critical_value], [0, norm.pdf(critical_value)], 
                        color='red', linestyle='--', linewidth=1.5)
                crit_height = norm.pdf(critical_value)
            else:
                ax.fill_between(x_crit, t.pdf(x_crit, df=df_value), color='red', alpha=0.3, label='Rejection Region')
                ax.plot([critical_value, critical_value], [0, t.pdf(critical_value, df=df_value)], 
                        color='red', linestyle='--', linewidth=1.5)
                crit_height = t.pdf(critical_value, df=df_value)
            
            # Position labels
            if test_statistic > critical_value:
                ts_ha = 'left'
                ts_x_offset = 0.1
                cv_ha = 'right'
                cv_x_offset = -0.1
            else:
                ts_ha = 'right'
                ts_x_offset = -0.1
                cv_ha = 'left'
                cv_x_offset = 0.1
            
            ax.text(critical_value + cv_x_offset, crit_height + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')

        # Plot test statistic
        if distribution == 'z-distribution':
            ts_height = norm.pdf(test_statistic)
        else:
            ts_height = t.pdf(test_statistic, df=df_value)

        ax.plot([test_statistic, test_statistic], [0, ts_height], 
                color='green', linestyle='-', linewidth=2)

        # Label test statistic
        ts_y_pos = ts_height + 0.02
        if hypothesis_type == 'two-tailed':
            ax.text(test_statistic - 0.1, ts_y_pos, 
                    f'Test Stat: {test_statistic:.2f}', ha='right', va='bottom', color='green')
        else:
            ax.text(test_statistic + ts_x_offset, ts_y_pos, 
                    f'Test Stat: {test_statistic:.2f}', ha=ts_ha, va='bottom', color='green')

        # Formatting
        test_type = "Z-Test" if distribution == 'z-distribution' else "T-Test"
        ax.set_title(f'Difference Between Means ({test_type}) - Traditional Method', fontsize=14, pad=20)
        ax.set_xlabel('Standardized Test Statistic', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.arange(int(x_min), int(x_max)+1, 1))
        ax.set_yticks(np.linspace(0, max(y_vals)+0.1, 10))
        ax.set_ylim(0, max(y_vals) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label=dist_label),
            Patch(facecolor='red', alpha=0.3, label='Rejection Region'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic ({test_statistic:.2f})')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()

        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): μ₁ = μ₂")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ₁ ≠ μ₂ (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ₁ > μ₂ (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): μ₁ < μ₂ (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")

        # Perform calculations with explanations
        if sigma1 and sigma2:  # Z-test
            steps.append("<strong>Step 2: Using Z-Test (σ₁ and σ₂ are known)</strong>")
            steps.append(f"• Population σ₁ provided: {sigma1}")
            steps.append(f"• Population σ₂ provided: {sigma2}")
            steps.append(f"• Standard Error: √((σ₁²/n₁)+(σ₂²/n₂)) = {round(standard_error, 4)}")
            steps.append(f"• Z-Score: (x̄₁ - x̄₂)/SE = ({x_bar1} - {x_bar2})/{round(standard_error, 4)} = {round(test_statistic, 4)}")
        elif 0.5 <= s1/s2 <= 2:  # Pooled t-test
            steps.append("<strong>Step 2: Using Pooled T-Test</strong>")
            steps.append(f"• Pooled Standard Deviation: √[((n₁-1)s₁² + (n₂-1)s₂²)/(n₁+n₂-2)] = {round(sp, 4)}")
            steps.append(f"• Standard Error: sp√(1/n₁ + 1/n₂) = {round(standard_error, 4)}")
            steps.append(f"• T-Score: (x̄₁ - x̄₂)/SE = ({x_bar1} - {x_bar2})/{round(standard_error, 4)} = {round(test_statistic, 4)}")
            steps.append(f"• Degrees of Freedom: n₁+n₂-2 = {n1+n2-2}")
        else:  # Welch's t-test
            steps.append("<strong>Step 2: Using Welch's T-Test</strong>")
            steps.append(f"• Standard Error: √(s₁²/n₁ + s₂²/n₂) = {round(standard_error, 4)}")
            steps.append(f"• T-Score: (x̄₁ - x̄₂)/SE = ({x_bar1} - {x_bar2})/{round(standard_error, 4)} = {round(test_statistic, 4)}")
            steps.append(f"• Degrees of Freedom: ≈{round(df, 2)} (Welch-Satterthwaite equation)")

        # Critical value explanation
        steps.append("<strong>Step 3: Critical Value</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• {critical_value_display} (α/2 = {alpha/2} in each tail)")
        else:
            tail = "right" if hypothesis_type == 'right-tailed' else "left"
            steps.append(f"• {critical_value_display} (α = {alpha} in the {tail} tail)")

        # Decision rule
        steps.append("<strong>Step 4: Decision Rule</strong>")
        if hypothesis_type == 'two-tailed':
            comparison = abs(test_statistic) > abs(critical_value)
            steps.append(f"• Reject H₀ if |Test Statistic| > |Critical Value|")
            steps.append(f"• {abs(round(test_statistic, 4))} {'>' if comparison else '<='} {abs(round(critical_value, 4))}")
        else:
            if hypothesis_type == 'right-tailed':
                comparison = test_statistic > critical_value
                steps.append(f"• Reject H₀ if Test Statistic > Critical Value")
            else:
                comparison = test_statistic < critical_value
                steps.append(f"• Reject H₀ if Test Statistic < Critical Value")
            steps.append(f"• {round(test_statistic, 4)} {'>' if comparison else '<='} {round(critical_value, 4)}")

        # Conclusion
        conclusion = 'Reject H₀' if comparison else 'Fail to reject H₀'
        steps.append(f"<strong>Conclusion:</strong> {conclusion}")

        # Prepare results
        result = {
            'testStatistic': round(test_statistic, 4),
            'criticalValue': critical_value_display,
            'distribution': distribution,
            'conclusion': conclusion,
            'steps': steps,
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        if 'fig' in locals():
            plt.close(fig)
        return jsonify({'error': str(e)}), 500
    
# ---------------  P-Value Method For Difference Between Means --------------- #

@app.route('/calculate_diff_means_pvalue', methods=['POST'])
def calculate_diff_means_pvalue():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['hypothesisType', 'x1', 'x2', 'alpha', 'n1', 'n2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        x_bar1 = float(data['x1'])
        x_bar2 = float(data['x2'])
        alpha = float(data['alpha'])
        n1 = int(data['n1'])
        n2 = int(data['n2'])
        sigma1 = float(data['sigma1']) if data.get('sigma1') else None
        sigma2 = float(data['sigma2']) if data.get('sigma2') else None
        s1 = float(data['s1']) if data.get('s1') else None
        s2 = float(data['s2']) if data.get('s2') else None

        if not sigma1 and not s1:
            return jsonify({'error': 'First sample standard deviation required when population σ₁ is unknown'}), 400
        if not sigma2 and not s2:
            return jsonify({'error': 'Second sample standard deviation required when population σ₂ is unknown'}), 400
        
        # Perform calculations
        if sigma1 and sigma2:  # Z-test
            standard_error = math.sqrt((sigma1**2/n1) + (sigma2**2/n2))
            test_statistic = (x_bar1 - x_bar2) / standard_error
            distribution = 'z-distribution'
            
            if hypothesis_type == 'two-tailed':
                p_value = 2 * (1 - norm.cdf(abs(test_statistic)))
            elif hypothesis_type == 'right-tailed':
                p_value = 1 - norm.cdf(test_statistic)
            else:  # left-tailed
                p_value = norm.cdf(test_statistic)
                
        else:  # t-test
            if not s1 or not s2:
                return jsonify({'error': 'Sample standard deviations required for both groups'}), 400
                
            variance_ratio = (s1**2)/(s2**2) if s2 != 0 else float('inf')
            
            if 0.5 <= variance_ratio <= 2:  # Pooled variance t-test
                sp = math.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2)/(n1+n2-2))
                standard_error = sp * math.sqrt(1/n1 + 1/n2)
                df = n1 + n2 - 2
                test_type = "Pooled Variance t-test"
            else:  # Welch's t-test
                standard_error = math.sqrt(s1**2/n1 + s2**2/n2)
                df = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
                test_type = "Welch's t-test"
            
            test_statistic = (x_bar1 - x_bar2) / standard_error
            distribution = f't-distribution (df={df:.2f}, {test_type})'
            
            if hypothesis_type == 'two-tailed':
                p_value = 2 * (1 - t.cdf(abs(test_statistic), df=df))
            elif hypothesis_type == 'right-tailed':
                p_value = 1 - t.cdf(test_statistic, df=df)
            else:  # left-tailed
                p_value = t.cdf(test_statistic, df=df)

        # ===== Create visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))

        # Calculate critical value based on alpha
        if hypothesis_type == 'two-tailed':
            crit_val = norm.ppf(1 - alpha/2) if distribution == 'z-distribution' else t.ppf(1 - alpha/2, df=df)
        elif hypothesis_type == 'right-tailed':
            crit_val = norm.ppf(1 - alpha) if distribution == 'z-distribution' else t.ppf(1 - alpha, df=df)
        else:  # left-tailed
            crit_val = norm.ppf(alpha) if distribution == 'z-distribution' else t.ppf(alpha, df=df)

        # Determine plot range dynamically
        plot_margin = 0.5
        x_min = min(-4, test_statistic - 3, -abs(crit_val) - plot_margin)
        x_max = max(4, test_statistic + 3, abs(crit_val) + plot_margin)
        x = np.linspace(x_min, x_max, 1000)

        # Choose distribution (normal or t)
        if distribution == 'z-distribution':
            y = norm.pdf(x)
        else:
            y = t.pdf(x, df=df)

        # Plot distribution
        ax.plot(x, y, 'b-', label=distribution, linewidth=2)

        # Shade p-value region
        if hypothesis_type == 'two-tailed':
            left_tail = x[x <= -abs(test_statistic)]
            right_tail = x[x >= abs(test_statistic)]
            ax.fill_between(left_tail, norm.pdf(left_tail) if distribution == 'z-distribution' else t.pdf(left_tail, df=df), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
            ax.fill_between(right_tail, norm.pdf(right_tail) if distribution == 'z-distribution' else t.pdf(right_tail, df=df), 
                            color='green', alpha=0.3)
        elif hypothesis_type == 'right-tailed':
            p_value_area = x[x >= test_statistic]
            ax.fill_between(p_value_area, norm.pdf(p_value_area) if distribution == 'z-distribution' else t.pdf(p_value_area, df=df), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
        else:  # left-tailed
            p_value_area = x[x <= test_statistic]
            ax.fill_between(p_value_area, norm.pdf(p_value_area) if distribution == 'z-distribution' else t.pdf(p_value_area, df=df), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')

        # Shade alpha region (rejection region)
        if hypothesis_type == 'two-tailed':
            alpha_left = x[x <= -abs(crit_val)]
            alpha_right = x[x >= abs(crit_val)]
            ax.fill_between(alpha_left, norm.pdf(alpha_left) if distribution == 'z-distribution' else t.pdf(alpha_left, df=df), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.fill_between(alpha_right, norm.pdf(alpha_right) if distribution == 'z-distribution' else t.pdf(alpha_right, df=df), 
                            color='orange', alpha=0.2)
            # Draw CV lines only up to curve height
            ax.plot([-crit_val, -crit_val], [0, norm.pdf(-crit_val) if distribution == 'z-distribution' else t.pdf(-crit_val, df=df)], 
                    color='red', linestyle='--', linewidth=1.5)
            ax.plot([crit_val, crit_val], [0, norm.pdf(crit_val) if distribution == 'z-distribution' else t.pdf(crit_val, df=df)], 
                    color='red', linestyle='--', linewidth=1.5)
        else:
            alpha_area = x[x >= crit_val] if hypothesis_type == 'right-tailed' else x[x <= crit_val]
            ax.fill_between(alpha_area, norm.pdf(alpha_area) if distribution == 'z-distribution' else t.pdf(alpha_area, df=df), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            # Draw CV line only up to curve height
            ax.plot([crit_val, crit_val], [0, norm.pdf(crit_val) if distribution == 'z-distribution' else t.pdf(crit_val, df=df)], 
                    color='red', linestyle='--', linewidth=1.5)

        # Plot test statistic line only up to curve height
        ax.plot([test_statistic, test_statistic], [0, norm.pdf(test_statistic) if distribution == 'z-distribution' else t.pdf(test_statistic, df=df)], 
                color='green', linestyle='-', linewidth=2)
        ts_y_pos = y[np.abs(x - test_statistic).argmin()] + 0.02

        if hypothesis_type == 'two-tailed':
            # For two-tailed tests, keep original positioning
            ax.text(test_statistic + 0.1, ts_y_pos,
                    f'Test Stat: {test_statistic:.2f}', 
                    ha='left',
                    va='bottom', 
                    color='green')
            
            ax.text(-crit_val + 0.1, y[np.abs(x - -crit_val).argmin()] + 0.01,
                    f'CV: -{abs(crit_val):.2f}', 
                    ha='left',
                    va='bottom', 
                    color='red')
            ax.text(crit_val - 0.1, y[np.abs(x - crit_val).argmin()] + 0.01,
                    f'CV: {crit_val:.2f}', 
                    ha='right',
                    va='bottom', 
                    color='red')
        else:
            # For one-tailed tests, determine label positions based on relative values
            if (hypothesis_type == 'right-tailed' and test_statistic > crit_val) or \
            (hypothesis_type == 'left-tailed' and test_statistic < crit_val):
                # Test stat is in rejection region
                ts_ha = 'left'
                ts_offset = 0.1
                cv_ha = 'right'
                cv_offset = -0.1
            else:
                # Test stat is not in rejection region
                ts_ha = 'right'
                ts_offset = -0.1
                cv_ha = 'left'
                cv_offset = 0.1
            
            # Position test statistic label
            ax.text(test_statistic + ts_offset, ts_y_pos,
                    f'Test Stat: {test_statistic:.2f}', 
                    ha=ts_ha,
                    va='bottom', 
                    color='green')
            
            # Position critical value label
            ax.text(crit_val + cv_offset,
                    y[np.abs(x - crit_val).argmin()] + 0.01, 
                    f'CV: {crit_val:.2f}', 
                    ha=cv_ha,
                    va='bottom', 
                    color='red')

        # Formatting
        ax.set_title(f'Difference Between Two Means Hypothesis Test\n({distribution})', fontsize=14, pad=20)
        ax.set_xlabel('Standard Deviations from Mean (Z)' if distribution == 'z' else 't-values', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.arange(int(x_min), int(x_max)+1, 1))
        ax.set_yticks(np.linspace(0, max(y)+0.1, 10))
        ax.set_ylim(0, max(y) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label=distribution),
            Patch(facecolor='green', alpha=0.3, label=f'p-value ({p_value:.4f})'),
            Patch(facecolor='orange', alpha=0.2, label=f'α region ({alpha})'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic ({test_statistic:.2f})'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value(s)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()

        # Initialize explanation steps
        steps = []
        
        # Step 1: Hypothesis Setup
        steps.append("<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): μ₁ = μ₂")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ₁ ≠ μ₂ (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): μ₁ > μ₂ (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): μ₁ < μ₂ (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")

        # Perform calculations
        if sigma1 and sigma2:  # Z-test (σ₁ and σ₂ are known)
            standard_error = math.sqrt((sigma1**2/n1) + (sigma2**2/n2))
            test_statistic = (x_bar1 - x_bar2) / standard_error
            distribution = 'z-distribution'
            
            # Step 2: Z-Test Calculation
            steps.append("<strong>Step 2: Z-Test Calculation</strong>")
            steps.append(f"• Population standard deviations: σ₁ = {sigma1}, σ₂ = {sigma2}")
            steps.append(f"• Standard Error = √(σ₁²/n₁ + σ₂²/n₂) = √({sigma1**2}/{n1} + {sigma2**2}/{n2}) = {standard_error:.4f}")
            steps.append(f"• Z-Score = (x̄₁ - x̄₂)/SE = ({x_bar1} - {x_bar2})/{standard_error:.4f} = {test_statistic:.4f}")
            
            # Step 3: P-Value Calculation
            if hypothesis_type == 'two-tailed':
                p_value = 2 * (1 - norm.cdf(abs(test_statistic)))
                steps.append("<strong>Step 3: Two-tailed P-value</strong>")
                steps.append(f"• p-value = 2 × P(Z ≥ |{test_statistic:.4f}|) = {p_value:.6f}")
            elif hypothesis_type == 'right-tailed':
                p_value = 1 - norm.cdf(test_statistic)
                steps.append("<strong>Step 3: Right-tailed P-value</strong>")
                steps.append(f"• p-value = P(Z ≥ {test_statistic:.4f}) = {p_value:.6f}")
            else:  # left-tailed
                p_value = norm.cdf(test_statistic)
                steps.append("<strong>Step 3: Left-tailed P-value</strong>")
                steps.append(f"• p-value = P(Z ≤ {test_statistic:.4f}) = {p_value:.6f}")
                
        else:  # t-test
            if not s1 or not s2:
                return jsonify({'error': 'Sample standard deviations required for both groups'}), 400
                
            variance_ratio = (s1**2)/(s2**2) if s2 != 0 else float('inf')
            
            if 0.5 <= variance_ratio <= 2:  # Pooled variance t-test
                sp = math.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2)/(n1+n2-2))
                standard_error = sp * math.sqrt(1/n1 + 1/n2)
                df = n1 + n2 - 2
                test_type = "Pooled Variance t-test"
                
                # Step 2: Pooled t-Test Calculation
                steps.append("<strong>Step 2: Pooled t-Test Calculation</strong>")
                steps.append(f"• Sample standard deviations: s₁ = {s1}, s₂ = {s2}")
                steps.append(f"• Variance ratio s₁²/s₂² = {variance_ratio:.2f} (using pooled variance)")
                steps.append(f"• Pooled SD = √[((n₁-1)s₁² + (n₂-1)s₂²)/(n₁+n₂-2)] = {sp:.4f}")
                steps.append(f"• Standard Error = sp × √(1/n₁ + 1/n₂) = {standard_error:.4f}")
                
            else:  # Welch's t-test
                standard_error = math.sqrt(s1**2/n1 + s2**2/n2)
                df = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
                test_type = "Welch's t-test"
                
                # Step 2: Welch's t-Test Calculation
                steps.append("<strong>Step 2: Welch's t-Test Calculation</strong>")
                steps.append(f"• Sample standard deviations: s₁ = {s1}, s₂ = {s2}")
                steps.append(f"• Variance ratio s₁²/s₂² = {variance_ratio:.2f} (using Welch's test)")
                steps.append(f"• Standard Error = √(s₁²/n₁ + s₂²/n₂) = {standard_error:.4f}")
                steps.append(f"• Degrees of freedom = {df:.2f} (Welch-Satterthwaite equation)")
            
            test_statistic = (x_bar1 - x_bar2) / standard_error
            distribution = f't-distribution (df={df:.2f}, {test_type})'
            
            steps.append(f"• t-Score = (x̄₁ - x̄₂)/SE = ({x_bar1} - {x_bar2})/{standard_error:.4f} = {test_statistic:.4f}")
            
            # Step 3: P-Value Calculation
            if hypothesis_type == 'two-tailed':
                p_value = 2 * (1 - t.cdf(abs(test_statistic), df=df))
                steps.append("<strong>Step 3: Two-tailed P-value</strong>")
                steps.append(f"• p-value = 2 × P(t ≥ |{test_statistic:.4f}|) = {p_value:.6f}")
            elif hypothesis_type == 'right-tailed':
                p_value = 1 - t.cdf(test_statistic, df=df)
                steps.append("<strong>Step 3: Right-tailed P-value</strong>")
                steps.append(f"• p-value = P(t ≥ {test_statistic:.4f}) = {p_value:.6f}")
            else:  # left-tailed
                p_value = t.cdf(test_statistic, df=df)
                steps.append("<strong>Step 3: Left-tailed P-value</strong>")
                steps.append(f"• p-value = P(t ≤ {test_statistic:.4f}) = {p_value:.6f}")

        # Step 4: Decision Rule
        steps.append("<strong>Step 4: Decision Rule</strong>")
        steps.append(f"• Compare p-value ({p_value:.6f}) to α ({alpha})")
        steps.append(f"• Decision: {'Reject H₀' if p_value <= alpha else 'Fail to reject H₀'} " + 
                    f"because {p_value:.6f} {'≤' if p_value <= alpha else '>'} {alpha}")

        conclusion = 'Reject H₀' if p_value <= alpha else 'Fail to reject H₀'
        
        return jsonify({
            'testStatistic': round(test_statistic, 4),
            'pValue': round(p_value, 6),
            'distribution': distribution,
            'conclusion': conclusion,
            'steps': steps,
            'plot': plot_data
        })
        
    except Exception as e:
        if 'fig' in locals():
            plt.close(fig)
        return jsonify({'error': str(e)}), 500

# ---------------  Confidence Interval Method For Difference between Means --------------- #
    
@app.route('/calculate_diff_means_ci', methods=['POST'])
def calculate_diff_means_ci():
    print("Received CI request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['confidenceLevel', 'x1', 'x2', 'n1', 'n2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Check if we have either population sigmas or sample std devs
        has_population_sigma = ('sigma1' in data and data['sigma1'] is not None and 
                               'sigma2' in data and data['sigma2'] is not None)
        
        has_sample_std_dev = ('s1' in data and data['s1'] is not None and 
                            's2' in data and data['s2'] is not None)
        
        if not has_population_sigma and not has_sample_std_dev:
            return jsonify({'error': 'Must provide either population σ or sample standard deviation'}), 400

        # Extract and convert data
        confidence_level = float(data['confidenceLevel'])
        n1 = int(data['n1'])
        n2 = int(data['n2'])
        x_bar1 = float(data['x1'])
        x_bar2 = float(data['x2'])
        
        # Initialize variables that will be used in steps
        sigma1 = None
        sigma2 = None
        s1 = None
        s2 = None
        
        # Determine which standard deviation to use
        if has_population_sigma:
            sigma1 = float(data['sigma1'])
            sigma2 = float(data['sigma2'])
            # Known population standard deviation - use z-distribution
            standard_error = math.sqrt((sigma1**2/n1) + (sigma2**2/n2))
            distribution = 'z-distribution'
            critical_value = norm.ppf(1 - (1 - confidence_level/100)/2)
        else:
            s1 = float(data['s1'])
            s2 = float(data['s2'])
            # Unknown population standard deviation - use t-distribution
            standard_error = math.sqrt((s1**2/n1) + (s2**2/n2))
            
            # Degrees of freedom (using Welch-Satterthwaite equation)
            df_numerator = ((s1**2/n1) + (s2**2/n2))**2
            df_denominator = ((s1**2/n1)**2)/(n1-1) + ((s2**2/n2)**2)/(n2-1)
            df = df_numerator / df_denominator
            
            distribution = f't-distribution (df≈{int(df)})'
            critical_value = t.ppf(1 - (1 - confidence_level/100)/2, df)
        
        # Calculate margin of error and confidence interval
        margin_of_error = critical_value * standard_error
        difference = x_bar1 - x_bar2
        lower_bound = difference - margin_of_error
        upper_bound = difference + margin_of_error
        
        # Create interpretation
        interpretation = (f"We are {confidence_level}% confident that the true difference in population means "
                         f"(μ₁ - μ₂) lies between {lower_bound:.4f} and {upper_bound:.4f}.")
        
        # Initialize explanation steps
        steps = []
        
        # Add basic info
        steps.append(f"<strong>Step 1: Input Parameters</strong>")
        steps.append(f"• Confidence Level: {confidence_level}%")
        steps.append(f"• Sample Mean (x̄₁): {x_bar1}")
        steps.append(f"• Sample Mean (x̄₂): {x_bar2}")
        steps.append(f"• Sample Size (n₁): {n1}")
        steps.append(f"• Sample Size (n₂): {n2}")
        
        # Add distribution info
        if has_population_sigma:
            steps.append("<strong>Step 2: Using z-distribution</strong>")
            steps.append(f"• Population Standard Deviation (σ₁) known: {sigma1}")
            steps.append(f"• Population Standard Deviation (σ₂) known: {sigma2}")
        else:
            steps.append("<strong>Step 2: Using t-distribution</strong>")
            steps.append(f"• Sample Standard Deviation (s₁): {s1}")
            steps.append(f"• Sample Standard Deviation (s₂): {s2}")
            steps.append(f"• Welch-Satterthwaite equation to calculate (df): [ (s1² / n1) + (s2² / n2) ]² / ( (s1² / n1)² / (n1 - 1) ) + ( (s2² / n2)² / (n2 - 1) )")
            steps.append(f"• Degrees of freedom (using Welch-Satterthwaite equation) (df): ≈{df:.2f}")
        
        steps.append(f"• Standard Error: {round(standard_error, 4)}")
        
        # Add critical value calculation
        steps.append("<strong>Step 3: Critical Value</strong>")
        steps.append(f"• Critical value for {confidence_level}% CI: {round(critical_value, 4)}")
        
        # Add margin of error calculation
        steps.append("<strong>Step 4: Margin of Error</strong>")
        steps.append(f"• Margin of Error = Critical Value × Standard Error")
        steps.append(f"• {round(critical_value, 4)} × {round(standard_error, 4)} = {round(margin_of_error, 4)}")
        
        # Add confidence interval calculation
        steps.append("<strong>Step 5: Confidence Interval</strong>")
        steps.append(f"• Lower Bound = (x̄₁-x̄₂) - Margin of Error")
        steps.append(f"• {round(difference, 4)} - {round(margin_of_error, 4)} = {round(lower_bound, 4)}")
        steps.append(f"• Upper Bound = (x̄₁-x̄₂) + Margin of Error")
        steps.append(f"• {round(difference, 4)} + {round(margin_of_error, 4)} = {round(upper_bound, 4)}")
        
        # Prepare results
        result = {
            'confidenceLevel': confidence_level,
            'sampleMean1': round(x_bar1, 4),
            'sampleMean2': round(x_bar2, 4),
            'difference': round(difference, 4),
            'criticalValue': round(critical_value, 4),
            'standardError': round(standard_error, 4),
            'marginOfError': round(margin_of_error, 4),
            'lowerBound': round(lower_bound, 4),
            'upperBound': round(upper_bound, 4),
            'distribution': distribution,
            'interpretation': interpretation,
            'steps': steps
        }

        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# ---------------  Traditional Method For Difference between Proportions --------------- #

@app.route('/calculate_two_proportions', methods=['POST'])
def calculate_two_proportions():
    print("Received two-proportion test request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'alpha', 'sampleSize1', 'successCount1', 'sampleSize2', 'successCount2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        alpha = float(data['alpha'])
        n1 = int(data['sampleSize1'])
        x1 = int(data['successCount1'])
        n2 = int(data['sampleSize2'])
        x2 = int(data['successCount2'])
        
        # Validate inputs
        if x1 < 0 or x1 > n1:
            return jsonify({'error': 'Number of successes in sample 1 must be between 0 and sample size'}), 400
        if x2 < 0 or x2 > n2:
            return jsonify({'error': 'Number of successes in sample 2 must be between 0 and sample size'}), 400
        
        # Calculate sample proportions
        p_hat1 = x1 / n1
        p_hat2 = x2 / n2
        p_hat_pooled = (x1 + x2) / (n1 + n2)
        
        # Calculate difference in proportions
        diff = p_hat1 - p_hat2
        
        # Calculate standard error
        standard_error = math.sqrt(p_hat_pooled * (1 - p_hat_pooled) * (1/n1 + 1/n2))
        
        # Calculate z-score
        z_score = diff / standard_error
        
        # Determine critical value based on test type
        if hypothesis_type == 'two-tailed':
            critical_value = norm.ppf(1 - alpha/2)
            critical_value_display = f"±{round(abs(critical_value), 4)}"
        elif hypothesis_type == 'right-tailed':
            critical_value = norm.ppf(1 - alpha)
            critical_value_display = round(critical_value, 4)
        else:  # left-tailed
            critical_value = norm.ppf(alpha)
            critical_value_display = round(critical_value, 4)

        # ===== Create visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Determine plot range
        plot_margin = 1.0
        x_min = min(-4, z_score - 3, -abs(critical_value) - plot_margin)
        x_max = max(4, z_score + 3, abs(critical_value) + plot_margin)
        x = np.linspace(x_min, x_max, 1000)
        y = norm.pdf(x)
        y_max = max(y) + 0.15

        # Plot distribution
        ax.plot(x, y, 'b-', label='Standard Normal Distribution', linewidth=2)

        # Shade rejection regions
        if hypothesis_type == 'two-tailed':
            left_tail = x[x <= -critical_value]
            right_tail = x[x >= critical_value]
            ax.fill_between(left_tail, norm.pdf(left_tail), color='orange', alpha=0.2, label=f'Rejection Region (α={alpha})')
            ax.fill_between(right_tail, norm.pdf(right_tail), color='orange', alpha=0.2)
        elif hypothesis_type == 'right-tailed':
            rejection_area = x[x >= critical_value]
            ax.fill_between(rejection_area, norm.pdf(rejection_area), color='orange', alpha=0.2, label=f'Rejection Region (α={alpha})')
        else:
            rejection_area = x[x <= critical_value]
            ax.fill_between(rejection_area, norm.pdf(rejection_area), color='orange', alpha=0.2, label=f'Rejection Region (α={alpha})')

        # Plot critical values (only up to curve height)
        cv_height = norm.pdf(critical_value)
        
        if hypothesis_type == 'two-tailed':
            # Left critical value
            ax.plot([-critical_value, -critical_value], [0, cv_height], 
                   color='red', linestyle='--', linewidth=1.5)
            ax.text(-critical_value, cv_height + 0.02, f'-CV: -{critical_value:.2f}', 
                   ha='center', color='red')
            
            # Right critical value
            ax.plot([critical_value, critical_value], [0, cv_height], 
                   color='red', linestyle='--', linewidth=1.5)
            ax.text(critical_value, cv_height + 0.02, f'CV: {critical_value:.2f}', 
                   ha='center', color='red')
        else:
            ax.plot([critical_value, critical_value], [0, cv_height], 
                   color='red', linestyle='--', linewidth=1.5)
            ax.text(critical_value, cv_height + 0.02, f'CV: {critical_value:.2f}', 
                   ha='center', color='red')

        # Plot test statistic (only up to curve height)
        ts_height = norm.pdf(z_score)
        ax.plot([z_score, z_score], [0, ts_height], 
               color='green', linestyle='-', linewidth=2)
        
        # Position test statistic label
        label_offset = 0.05 if abs(z_score - critical_value) > 0.5 else 0.1
        if z_score > 0:
            ha = 'left'
            xpos = z_score + label_offset
        else:
            ha = 'right'
            xpos = z_score - label_offset
            
        ax.text(xpos, ts_height + 0.02, f'Z = {z_score:.2f}', 
               color='green', ha=ha)

        # Final formatting
        ax.set_title('Two-Proportion Z-Test (Traditional Method)', fontsize=14, pad=20)
        ax.set_xlabel('Z-Score', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_ylim(0, y_max)
        ax.set_xlim(x_min, x_max)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create legend
        ax.legend(handles=[
            Line2D([0], [0], color='blue', lw=2, label='Standard Normal'),
            Patch(facecolor='orange', alpha=0.2, label=f'Rejection Region'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value'),
            Line2D([0], [0], color='green', lw=2, label='Test Statistic')
        ], loc='upper right')

        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): p₁ = p₂ (no difference between proportions)")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p₁ ≠ p₂ (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p₁ > p₂ (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): p₁ < p₂ (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Add sample information
        steps.append("<strong>Step 2: Sample Information</strong>")
        steps.append(f"<strong>Sample 1:</strong>")
        steps.append(f"• Successes (x₁): {x1}")
        steps.append(f"• Sample size (n₁): {n1}")
        steps.append(f"• Sample proportion (p̂₁ = x₁/n₁): {round(p_hat1, 4)}")
        
        steps.append(f"<strong>Sample 2:</strong>")
        steps.append(f"• Successes (x₂): {x2}")
        steps.append(f"• Sample size (n₂): {n2}")
        steps.append(f"• Sample proportion (p̂₂ = x₂/n₂): {round(p_hat2, 4)}")
        
        steps.append(f"• Difference in proportions (p̂₁ - p̂₂): {round(diff, 4)}")
        
        # Add calculation steps
        steps.append("<strong>Step 3: Pooled Proportion</strong>")
        steps.append(f"• Pooled proportion = (x₁ + x₂)/(n₁ + n₂) = ({x1} + {x2})/({n1} + {n2})")
        steps.append(f"• Pooled proportion = {round(p_hat_pooled, 4)}")
        
        steps.append("<strong>Step 4: Standard Error Calculation</strong>")
        steps.append(f"• SE = √[p̂(1-p̂)(1/n₁ + 1/n₂)] = √[{round(p_hat_pooled, 4)}×{round(1-p_hat_pooled, 4)}×(1/{n1} + 1/{n2})]")
        steps.append(f"• Standard Error = {round(standard_error, 4)}")
        
        steps.append("<strong>Step 5: Z-Score Calculation</strong>")
        steps.append(f"• Z = (p̂₁ - p̂₂)/SE = {round(diff, 4)}/{round(standard_error, 4)}")
        steps.append(f"• Z-Score = {round(z_score, 4)}")
        
        steps.append("<strong>Step 6: Critical Value</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Critical Value: ±{round(critical_value, 4)} (Two-tailed)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Critical Value: {round(critical_value, 4)} (Right-tailed)")
        else:
            steps.append(f"• Critical Value: {round(critical_value, 4)} (Left-tailed)")
        
        # Decision logic
        steps.append("<strong>Step 7: Decision Rule</strong>")
        if hypothesis_type == 'two-tailed':
            reject_condition = abs(z_score) > abs(critical_value)
            steps.append(f"• Reject H₀ if |Z-Score| > |Critical Value|")
            steps.append(f"• {abs(round(z_score, 4))} {'>' if reject_condition else '<'} {abs(round(critical_value, 4))}")
        elif hypothesis_type == 'right-tailed':
            reject_condition = z_score > critical_value
            steps.append(f"• Reject H₀ if Z-Score > Critical Value")
            steps.append(f"• {round(z_score, 4)} {'>' if reject_condition else '<'} {round(critical_value, 4)}")
        else:  # left-tailed
            reject_condition = z_score < critical_value
            steps.append(f"• Reject H₀ if Z-Score < Critical Value")
            steps.append(f"• {round(z_score, 4)} {'<' if reject_condition else '>'} {round(critical_value, 4)}")
        
        # Conclusion
        conclusion = 'Reject H₀' if reject_condition else 'Fail to reject H₀'
        steps.append(f"<strong>Conclusion:</strong> {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(z_score, 4),
            'criticalValue': critical_value_display,
            'distribution': 'z-distribution',
            'conclusion': conclusion,
            'steps': steps,
            'sampleProportion1': round(p_hat1, 4),
            'sampleProportion2': round(p_hat2, 4),
            'difference': round(diff, 4),
            'pooledProportion': round(p_hat_pooled, 4),
            'standardError': round(standard_error, 4),
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ---------------  P-Value Method For Difference Between Proportions --------------- #

@app.route('/calculate_two_proportions_pvalue', methods=['POST'])
def calculate_two_proportions_pvalue():
    print("Received two-proportion p-value request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'alpha', 'sampleSize1', 'successCount1', 'sampleSize2', 'successCount2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        alpha = float(data['alpha'])
        n1 = int(data['sampleSize1'])
        x1 = int(data['successCount1'])
        n2 = int(data['sampleSize2'])
        x2 = int(data['successCount2'])
        
        # Validate inputs
        if x1 < 0 or x1 > n1:
            return jsonify({'error': 'Number of successes in sample 1 must be between 0 and sample size'}), 400
        if x2 < 0 or x2 > n2:
            return jsonify({'error': 'Number of successes in sample 2 must be between 0 and sample size'}), 400
        
        # Calculate sample proportions
        p_hat1 = x1 / n1
        p_hat2 = x2 / n2
        p_hat_pooled = (x1 + x2) / (n1 + n2)
        
        # Calculate difference in proportions
        diff = p_hat1 - p_hat2
        
        # Calculate standard error
        standard_error = math.sqrt(p_hat_pooled * (1 - p_hat_pooled) * (1/n1 + 1/n2))
        
        # Calculate z-score
        z_score = diff / standard_error
        
        # Calculate p-value based on test type
        if hypothesis_type == 'two-tailed':
            p_value = 2 * (1 - norm.cdf(abs(z_score)))
            p_value_display = round(p_value, 6)
            comparison = f"p-value = {p_value_display} (Two-tailed)"
        elif hypothesis_type == 'right-tailed':
            p_value = 1 - norm.cdf(z_score)
            p_value_display = round(p_value, 6)
            comparison = f"p-value = {p_value_display} (Right-tailed)"
        else:  # left-tailed
            p_value = norm.cdf(z_score)
            p_value_display = round(p_value, 6)
            comparison = f"p-value = {p_value_display} (Left-tailed)"
        
        # Determine conclusion
        reject_condition = p_value < alpha
        conclusion = 'Reject H₀' if reject_condition else 'Fail to reject H₀'

        # ===== Visualization =====
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Calculate critical value for visualization
        if hypothesis_type == 'two-tailed':
            crit_val = norm.ppf(1 - alpha/2)
        elif hypothesis_type == 'right-tailed':
            crit_val = norm.ppf(1 - alpha)
        else:
            crit_val = norm.ppf(alpha)

        # Dynamic plot range
        plot_margin = 1.0
        x_min = min(-4, z_score - 2, -abs(crit_val) - plot_margin)
        x_max = max(4, z_score + 2, abs(crit_val) + plot_margin)
        x_vals = np.linspace(x_min, x_max, 1000)
        y_vals = norm.pdf(x_vals)
        y_max = max(y_vals) + 0.15

        # Plot distribution
        ax.plot(x_vals, y_vals, 'b-', label='Standard Normal Distribution', linewidth=2)

        # Shade p-value region (green as in original)
        if hypothesis_type == 'two-tailed':
            left_tail = x_vals[x_vals <= -abs(z_score)]
            right_tail = x_vals[x_vals >= abs(z_score)]
            ax.fill_between(left_tail, y_vals[:len(left_tail)], color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
            ax.fill_between(right_tail, y_vals[-len(right_tail):], color='green', alpha=0.3)
        elif hypothesis_type == 'right-tailed':
            p_value_area = x_vals[x_vals >= z_score]
            ax.fill_between(p_value_area, y_vals[-len(p_value_area):], color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
        else:
            p_value_area = x_vals[x_vals <= z_score]
            ax.fill_between(p_value_area, y_vals[:len(p_value_area)], color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')

        # Shade alpha region (orange as in original)
        if hypothesis_type == 'two-tailed':
            alpha_left = x_vals[x_vals <= -abs(crit_val)]
            alpha_right = x_vals[x_vals >= abs(crit_val)]
            ax.fill_between(alpha_left, y_vals[:len(alpha_left)], color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.fill_between(alpha_right, y_vals[-len(alpha_right):], color='orange', alpha=0.2)
        else:
            alpha_area = x_vals[x_vals >= crit_val] if hypothesis_type == 'right-tailed' else x_vals[x_vals <= crit_val]
            ax.fill_between(alpha_area, y_vals[:len(alpha_area)] if hypothesis_type == 'left-tailed' else y_vals[-len(alpha_area):], 
                           color='orange', alpha=0.2, label=f'α region ({alpha})')

        # Plot critical values (only up to curve)
        cv_height = norm.pdf(crit_val)
        if hypothesis_type == 'two-tailed':
            ax.plot([-crit_val, -crit_val], [0, cv_height], color='red', linestyle='--', linewidth=1.5)
            ax.plot([crit_val, crit_val], [0, cv_height], color='red', linestyle='--', linewidth=1.5)
        else:
            ax.plot([crit_val, crit_val], [0, cv_height], color='red', linestyle='--', linewidth=1.5)

        # Plot test statistic (only up to curve)
        ts_height = norm.pdf(z_score)
        ax.plot([z_score, z_score], [0, ts_height], color='green', linestyle='-', linewidth=2)

        # Label positioning without arrows
        label_y_offset = 0.02
        if hypothesis_type == 'two-tailed':
            # Critical values
            ax.text(-crit_val, cv_height + label_y_offset, f'-CV: -{crit_val:.2f}', ha='center', color='red')
            ax.text(crit_val, cv_height + label_y_offset, f'CV: {crit_val:.2f}', ha='center', color='red')
            # Test statistic
            ts_ha = 'left' if z_score > 0 else 'right'
            ts_x_offset = 0.1 if z_score > 0 else -0.1
            ax.text(z_score + ts_x_offset, ts_height + label_y_offset, f'Z = {z_score:.2f}', 
                   color='green', ha=ts_ha)
        else:
            # Critical value
            ax.text(crit_val, cv_height + label_y_offset, f'CV: {crit_val:.2f}', 
                   ha='left' if hypothesis_type == 'right-tailed' else 'right', color='red')
            # Test statistic
            ts_ha = 'left' if (hypothesis_type == 'right-tailed' and z_score > crit_val) or \
                              (hypothesis_type == 'left-tailed' and z_score > crit_val) else 'right'
            ts_x_offset = 0.1 if ts_ha == 'left' else -0.1
            ax.text(z_score + ts_x_offset, ts_height + label_y_offset, f'Z = {z_score:.2f}', 
                   color='green', ha=ts_ha)

        # Formatting
        ax.set_title('Two-Proportion Z-Test (P-Value Method)', fontsize=14, pad=20)
        ax.set_xlabel('Z-Score', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_ylim(0, y_max)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label='Standard Normal'),
            Patch(facecolor='green', alpha=0.3, label=f'p-value ({p_value:.4f})'),
            Patch(facecolor='orange', alpha=0.2, label=f'α region ({alpha})'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic (Z={z_score:.2f})'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value(s)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        # Save plot
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): p₁ = p₂ (no difference between proportions)")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p₁ ≠ p₂ (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): p₁ > p₂ (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): p₁ < p₂ (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Add sample information
        steps.append("<strong>Step 2: Sample Information</strong>")
        steps.append(f"<strong>Sample 1:</strong>")
        steps.append(f"• Successes (x₁): {x1}")
        steps.append(f"• Sample size (n₁): {n1}")
        steps.append(f"• Sample proportion (p̂₁ = x₁/n₁): {round(p_hat1, 4)}")
        
        steps.append(f"<strong>Sample 2:</strong>")
        steps.append(f"• Successes (x₂): {x2}")
        steps.append(f"• Sample size (n₂): {n2}")
        steps.append(f"• Sample proportion (p̂₂ = x₂/n₂): {round(p_hat2, 4)}")
        
        steps.append(f"• Difference in proportions (p̂₁ - p̂₂): {round(diff, 4)}")
        
        # Add calculation steps
        steps.append("<strong>Step 3: Pooled Proportion</strong>")
        steps.append(f"• Pooled proportion = (x₁ + x₂)/(n₁ + n₂) = ({x1} + {x2})/({n1} + {n2})")
        steps.append(f"• Pooled proportion = {round(p_hat_pooled, 4)}")
        
        steps.append("<strong>Step 4: Standard Error Calculation</strong>")
        steps.append(f"• SE = √[p̂(1-p̂)(1/n₁ + 1/n₂)] = √[{round(p_hat_pooled, 4)}×{round(1-p_hat_pooled, 4)}×(1/{n1} + 1/{n2})]")
        steps.append(f"• Standard Error = {round(standard_error, 4)}")
        
        steps.append("<strong>Step 5: Z-Score Calculation</strong>")
        steps.append(f"• Z = (p̂₁ - p̂₂)/SE = {round(diff, 4)}/{round(standard_error, 4)}")
        steps.append(f"• Z-Score = {round(z_score, 4)}")
        
        steps.append("<strong>Step 6: P-Value Calculation</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• p-value = 2 × P(Z ≥ |{round(z_score, 4)}|)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• p-value = P(Z ≥ {round(z_score, 4)})")
        else:
            steps.append(f"• p-value = P(Z ≤ {round(z_score, 4)})")
        steps.append(f"• Calculated p-value: {p_value_display}")
        
        steps.append("<strong>Step 7: Decision Rule</strong>")
        steps.append(f"• Reject H₀ if p-value < α ({alpha})")
        steps.append(f"• {p_value_display} {'<' if reject_condition else '>'} {alpha}")
        
        steps.append(f"<strong>Conclusion:</strong> {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(z_score, 4),
            'pValue': p_value_display,
            'comparison': comparison,
            'distribution': 'z-distribution',
            'conclusion': conclusion,
            'steps': steps,
            'sampleProportion1': round(p_hat1, 4),
            'sampleProportion2': round(p_hat2, 4),
            'difference': round(diff, 4),
            'pooledProportion': round(p_hat_pooled, 4),
            'standardError': round(standard_error, 4),
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
# ---------------  Confidence Interval Method For Difference between Proportions --------------- #

@app.route('/calculate_two_proportions_ci', methods=['POST'])
def calculate_two_proportions_ci():
    print("Received two-proportion confidence interval request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['confidenceLevel', 'sampleSize1', 'successCount1', 'sampleSize2', 'successCount2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        confidence_level = float(data['confidenceLevel'])
        n1 = int(data['sampleSize1'])
        x1 = int(data['successCount1'])
        n2 = int(data['sampleSize2'])
        x2 = int(data['successCount2'])
        
        # Validate inputs
        if confidence_level <= 0 or confidence_level >= 100:
            return jsonify({'error': 'Confidence level must be between 0 and 100'}), 400
        if x1 < 0 or x1 > n1:
            return jsonify({'error': 'Number of successes in sample 1 must be between 0 and sample size'}), 400
        if x2 < 0 or x2 > n2:
            return jsonify({'error': 'Number of successes in sample 2 must be between 0 and sample size'}), 400
        
        # Calculate sample proportions
        p_hat1 = x1 / n1
        p_hat2 = x2 / n2
        
        # Calculate difference in proportions
        diff = p_hat1 - p_hat2
        
        # Calculate standard error (not pooled for CI)
        standard_error = math.sqrt((p_hat1 * (1 - p_hat1) / n1) + (p_hat2 * (1 - p_hat2) / n2))
        
        # Calculate critical value (z*)
        alpha = 1 - (confidence_level / 100)
        critical_value = norm.ppf(1 - alpha/2)
        
        # Calculate margin of error
        margin_of_error = critical_value * standard_error
        
        # Calculate confidence interval
        lower_bound = diff - margin_of_error
        upper_bound = diff + margin_of_error
        
        # Initialize explanation steps
        steps = []
        
        # Add basic info
        steps.append(f"<strong>Step 1: Sample Information</strong>")
        steps.append(f"<strong>Sample 1:</strong>")
        steps.append(f"• Successes (x₁): {x1}")
        steps.append(f"• Sample size (n₁): {n1}")
        steps.append(f"• Sample proportion (p̂₁ = x₁/n₁): {round(p_hat1, 4)}")
        
        steps.append(f"<strong>Sample 2:</strong>")
        steps.append(f"• Successes (x₂): {x2}")
        steps.append(f"• Sample size (n₂): {n2}")
        steps.append(f"• Sample proportion (p̂₂ = x₂/n₂): {round(p_hat2, 4)}")
        
        steps.append(f"• Difference in proportions (p̂₁ - p̂₂): {round(diff, 4)}")
        
        # Add calculation steps
        steps.append("<strong>Step 2: Standard Error Calculation</strong>")
        steps.append(f"• SE = √[(p̂₁(1-p̂₁)/n₁ + p̂₂(1-p̂₂)/n₂]")
        steps.append(f"• SE = √[({round(p_hat1,4)}×{round(1-p_hat1,4)}/{n1} + {round(p_hat2,4)}×{round(1-p_hat2,4)}/{n2}]")
        steps.append(f"• Standard Error = {round(standard_error, 4)}")
        
        steps.append("<strong>Step 3: Critical Value</strong>")
        steps.append(f"• Confidence Level: {confidence_level}%")
        steps.append(f"• α = 1 - {confidence_level/100} = {round(alpha, 2)}")
        steps.append(f"• Critical Value (z) = {round(critical_value, 4)}")
        
        steps.append("<strong>Step 4: Margin of Error</strong>")
        steps.append(f"• Margin of Error = z × SE = {round(critical_value, 4)} × {round(standard_error, 4)}")
        steps.append(f"• Margin of Error = {round(margin_of_error, 4)}")
        
        steps.append("<strong>Step 5: Confidence Interval</strong>")
        steps.append(f"• CI = (p̂₁ - p̂₂) ± Margin of Error")
        steps.append(f"• CI = {round(diff, 4)} ± {round(margin_of_error, 4)}")
        steps.append(f"• Lower Bound = {round(diff, 4)} - {round(margin_of_error, 4)} = {round(lower_bound, 4)}")
        steps.append(f"• Upper Bound = {round(diff, 4)} + {round(margin_of_error, 4)} = {round(upper_bound, 4)}")
        
        # Interpretation
        steps.append("<strong>Interpretation:</strong>")
        steps.append(f"We are {confidence_level}% confident that the true difference in population proportions (p₁ - p₂) lies between {round(lower_bound, 4)} and {round(upper_bound, 4)}")
        
        # Prepare results
        result = {
            'sampleProportion1': round(p_hat1, 4),
            'sampleProportion2': round(p_hat2, 4),
            'difference': round(diff, 4),
            'confidenceLevel': confidence_level,
            'criticalValue': round(critical_value, 4),
            'standardError': round(standard_error, 4),
            'marginOfError': round(margin_of_error, 4),
            'confidenceInterval': {
                'lower': round(lower_bound, 4),
                'upper': round(upper_bound, 4)
            },
            'steps': steps,
            'interpretation': f"The {confidence_level}% confidence interval for the difference in proportions (p₁ - p₂) is ({round(lower_bound, 4)}, {round(upper_bound, 4)})"
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ---------------  Traditional Method For Difference between Variances --------------- #

@app.route('/calculate_two_variances', methods=['POST'])
def calculate_two_variances():
    print("Received two-variance test request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'alpha', 'sampleSize1', 'sampleVariance1', 
                          'sampleSize2', 'sampleVariance2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        alpha = float(data['alpha'])
        n1 = int(data['sampleSize1'])
        s1_squared = float(data['sampleVariance1'])
        n2 = int(data['sampleSize2'])
        s2_squared = float(data['sampleVariance2'])
        
        # Validate inputs
        if n1 < 2 or n2 < 2:
            return jsonify({'error': 'Sample sizes must be at least 2'}), 400
        if s1_squared <= 0 or s2_squared <= 0:
            return jsonify({'error': 'Sample variances must be positive'}), 400
        
        # Calculate F-statistic (always put larger variance in numerator)
        if s1_squared >= s2_squared:
            f_statistic = s1_squared / s2_squared
            df1 = n1 - 1  # degrees of freedom numerator
            df2 = n2 - 1  # degrees of freedom denominator
            larger_variance = "first sample"
        else:
            f_statistic = s2_squared / s1_squared
            df1 = n2 - 1
            df2 = n1 - 1
            larger_variance = "second sample"
        
        # Determine critical value based on test type
        if hypothesis_type == 'two-tailed':
            critical_value = f.ppf(1 - alpha/2, df1, df2)
            critical_value_display = f"F({alpha/2}, {df1}, {df2}) = {round(critical_value, 4)}"
        elif hypothesis_type == 'right-tailed':
            critical_value = f.ppf(1 - alpha, df1, df2)
            critical_value_display = f"F({alpha}, {df1}, {df2}) = {round(critical_value, 4)}"
        elif hypothesis_type == 'left-tailed':
            critical_value = f.ppf(alpha, df1, df2)
            critical_value_display = f"F({1-alpha}, {df1}, {df2}) = {round(critical_value, 4)}"
        else:
            return jsonify({'error': 'Invalid hypothesis type'}), 400
        
        # Determine conclusion
        conclusion = ""
        if hypothesis_type == 'two-tailed':
            if f_statistic > critical_value or f_statistic < (1/critical_value):
                conclusion = "Reject the null hypothesis (H₀)"
            else:
                conclusion = "Fail to reject the null hypothesis (H₀)"
        elif hypothesis_type == 'right-tailed':
            conclusion = "Reject H₀" if f_statistic > critical_value else "Fail to reject H₀"
        else:  # left-tailed
            conclusion = "Reject H₀" if f_statistic < critical_value else "Fail to reject H₀"

        # ===== Create F-Distribution Visualization =====
        fig, ax = plt.subplots(figsize=(10, 6))

        # Determine plot range dynamically
        plot_margin = 0.5
        x_min = 0  # F-distribution starts at 0
        x_max = max(4, f_statistic + 3, critical_value + plot_margin)
        x_vals = np.linspace(x_min, x_max, 1000)
        y_vals = f.pdf(x_vals, df1, df2)

        # Plot F-distribution
        ax.plot(x_vals, y_vals, 'b-', label=f'F-Distribution (df1={df1}, df2={df2})', linewidth=2)

        if hypothesis_type == 'two-tailed':
            # For two-tailed test
            upper_reject = x_vals[x_vals >= critical_value]
            lower_crit = 1/critical_value
            lower_reject = x_vals[x_vals <= lower_crit]
            
            # Shade rejection regions
            ax.fill_between(upper_reject, f.pdf(upper_reject, df1, df2), 
                            color='red', alpha=0.3, label='Rejection Region')
            ax.fill_between(lower_reject, f.pdf(lower_reject, df1, df2), 
                            color='red', alpha=0.3)
            
            # Plot critical value lines
            ax.plot([critical_value, critical_value], [0, f.pdf(critical_value, df1, df2)], 
                    color='red', linestyle='--', linewidth=1.5)
            ax.plot([lower_crit, lower_crit], [0, f.pdf(lower_crit, df1, df2)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions for upper critical value
            if f_statistic > critical_value:
                # F-stat in upper rejection region
                upper_cv_ha = 'right'
                upper_cv_offset = -0.1
                f_stat_ha_upper = 'left'
                f_stat_offset_upper = 0.1
            else:
                # F-stat not in upper rejection region
                upper_cv_ha = 'left'
                upper_cv_offset = 0.1
                f_stat_ha_upper = 'right'
                f_stat_offset_upper = -0.1
            
            # Determine label positions for lower critical value
            if f_statistic < lower_crit:
                # F-stat in lower rejection region
                lower_cv_ha = 'left'
                lower_cv_offset = 0.1
                f_stat_ha_lower = 'right'
                f_stat_offset_lower = -0.1
            else:
                # F-stat not in lower rejection region
                lower_cv_ha = 'right'
                lower_cv_offset = -0.1
                f_stat_ha_lower = 'left'
                f_stat_offset_lower = 0.1
            
            # Position upper CV label
            ax.text(critical_value + upper_cv_offset, f.pdf(critical_value, df1, df2) + 0.01, 
                    f'Upper CV: {critical_value:.2f}', ha=upper_cv_ha, va='bottom', color='red')
            
            # Position lower CV label
            ax.text(lower_crit + lower_cv_offset, f.pdf(lower_crit, df1, df2) + 0.01, 
                    f'Lower CV: {lower_crit:.2f}', ha=lower_cv_ha, va='bottom', color='red')
            
            # Position F-statistic label (choose position based on which tail is relevant)
            ts_y_pos = f.pdf(f_statistic, df1, df2) + 0.02
            if f_statistic > critical_value:
                ax.text(f_statistic + f_stat_offset_upper, ts_y_pos, 
                        f'F-Stat: {f_statistic:.2f}', 
                        ha=f_stat_ha_upper, va='bottom', color='green')
            elif f_statistic < lower_crit:
                ax.text(f_statistic + f_stat_offset_lower, ts_y_pos, 
                        f'F-Stat: {f_statistic:.2f}', 
                        ha=f_stat_ha_lower, va='bottom', color='green')
            else:
                # In the middle, default to right
                ax.text(f_statistic - 0.1, ts_y_pos, 
                        f'F-Stat: {f_statistic:.2f}', 
                        ha='right', va='bottom', color='green')

        elif hypothesis_type == 'right-tailed':
            # For right-tailed test
            reject_region = x_vals[x_vals >= critical_value]
            ax.fill_between(reject_region, f.pdf(reject_region, df1, df2), 
                            color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, f.pdf(critical_value, df1, df2)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions
            if f_statistic > critical_value:
                # F-stat in rejection region
                cv_ha = 'right'
                cv_offset = -0.1
                f_stat_ha = 'left'
                f_stat_offset = 0.1
            else:
                # F-stat not in rejection region
                cv_ha = 'left'
                cv_offset = 0.1
                f_stat_ha = 'right'
                f_stat_offset = -0.1
            
            # Position CV label
            ax.text(critical_value + cv_offset, f.pdf(critical_value, df1, df2) + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')
            
            # Position F-statistic label
            ts_y_pos = f.pdf(f_statistic, df1, df2) + 0.02
            ax.text(f_statistic + f_stat_offset, ts_y_pos, 
                    f'F-Stat: {f_statistic:.2f}', 
                    ha=f_stat_ha, va='bottom', color='green')

        else:  # left-tailed
            # For left-tailed test
            reject_region = x_vals[x_vals <= critical_value]
            ax.fill_between(reject_region, f.pdf(reject_region, df1, df2), 
                            color='red', alpha=0.3, label='Rejection Region')
            ax.plot([critical_value, critical_value], [0, f.pdf(critical_value, df1, df2)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Determine label positions
            if f_statistic < critical_value:
                # F-stat in rejection region
                cv_ha = 'left'
                cv_offset = 0.1
                f_stat_ha = 'right'
                f_stat_offset = -0.1
            else:
                # F-stat not in rejection region
                cv_ha = 'right'
                cv_offset = -0.1
                f_stat_ha = 'left'
                f_stat_offset = 0.1
            
            # Position CV label
            ax.text(critical_value + cv_offset, f.pdf(critical_value, df1, df2) + 0.01, 
                    f'CV: {critical_value:.2f}', ha=cv_ha, va='bottom', color='red')
            
            # Position F-statistic label
            ts_y_pos = f.pdf(f_statistic, df1, df2) + 0.02
            ax.text(f_statistic + f_stat_offset, ts_y_pos, 
                    f'F-Stat: {f_statistic:.2f}', 
                    ha=f_stat_ha, va='bottom', color='green')

        # Plot test statistic line
        ax.plot([f_statistic, f_statistic], [0, f.pdf(f_statistic, df1, df2)], 
                color='green', linestyle='-', linewidth=2)

        # Formatting
        ax.set_title('F-Test for Equality of Variances', fontsize=14, pad=20)
        ax.set_xlabel('F-Value', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.linspace(0, x_max, min(10, int(x_max)+1)))
        ax.set_yticks(np.linspace(0, max(y_vals)+0.1, 10))
        ax.set_ylim(0, max(y_vals) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label=f'F-Distribution (df1={df1}, df2={df2})'),
            Patch(facecolor='red', alpha=0.3, label='Rejection Region'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic ({f_statistic:.2f})')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): σ₁² = σ₂² (variances are equal)")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ₁² ≠ σ₂² (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ₁² > σ₂² (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): σ₁² < σ₂² (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Add sample information
        steps.append("<strong>Step 2: Sample Information</strong>")
        steps.append(f"<strong>Sample 1:</strong>")
        steps.append(f"• Sample size (n₁): {n1}")
        steps.append(f"• Sample variance (s₁²): {round(s1_squared, 4)}")
        
        steps.append(f"<strong>Sample 2:</strong>")
        steps.append(f"• Sample size (n₂): {n2}")
        steps.append(f"• Sample variance (s₂²): {round(s2_squared, 4)}")
        
        # Add F-statistic calculation
        steps.append("<strong>Step 3: Calculate F-Statistic</strong>")
        steps.append(f"• Larger variance is from the {larger_variance}")
        if s1_squared >= s2_squared:
            steps.append(f"• F = s₁² / s₂² = {round(s1_squared, 4)} / {round(s2_squared, 4)} = {round(f_statistic, 4)}")
        else:
            steps.append(f"• F = s₂² / s₁² = {round(s2_squared, 4)} / {round(s1_squared, 4)} = {round(f_statistic, 4)}")
        steps.append(f"• Degrees of Freedom (numerator): df₁ = n₁ - 1 = {df1}")
        steps.append(f"• Degrees of Freedom (denominator): df₂ = n₂ - 1 = {df2}")
        
        # Add critical value calculation
        steps.append("<strong>Step 4: Determine Critical Value</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Two-tailed test: F(α/2, df₁, df₂) = F({alpha/2}, {df1}, {df2})")
            steps.append(f"• Critical Value = {round(critical_value, 4)}")
            steps.append(f"• Rejection Region: F > {round(critical_value, 4)} or F < {round(1/critical_value, 4)}")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Right-tailed test: F(α, df₁, df₂) = F({alpha}, {df1}, {df2})")
            steps.append(f"• Critical Value = {round(critical_value, 4)}")
            steps.append(f"• Rejection Region: F > {round(critical_value, 4)}")
        else:
            steps.append(f"• Left-tailed test: F(1-α, df₁, df₂) = F({1-alpha}, {df1}, {df2})")
            steps.append(f"• Critical Value = {round(critical_value, 4)}")
            steps.append(f"• Rejection Region: F < {round(critical_value, 4)}")
        
        # Add decision
        steps.append("<strong>Step 5: Make Decision</strong>")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Compare F-statistic ({round(f_statistic, 4)}) with critical values")
            steps.append(f"• {round(f_statistic, 4)} > {round(critical_value, 4)} or {round(f_statistic, 4)} < {round(1/critical_value, 4)}?")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Compare F-statistic ({round(f_statistic, 4)}) with critical value ({round(critical_value, 4)})")
            steps.append(f"• {round(f_statistic, 4)} > {round(critical_value, 4)}?")
        else:
            steps.append(f"• Compare F-statistic ({round(f_statistic, 4)}) with critical value ({round(critical_value, 4)})")
            steps.append(f"• {round(f_statistic, 4)} < {round(critical_value, 4)}?")
        
        steps.append(f"• Conclusion: {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(f_statistic, 4),
            'criticalValue': critical_value_display,
            'df1': df1,
            'df2': df2,
            'distribution': 'F-distribution',
            'plot': plot_data,
            'conclusion': conclusion,
            'steps': steps,
            'sampleVariance1': round(s1_squared, 4),
            'sampleVariance2': round(s2_squared, 4),
            'largerVariance': larger_variance
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------  P-Value Method For Difference between Variances --------------- #

@app.route('/calculate_two_variances_pvalue', methods=['POST'])
def calculate_two_variances_pvalue():
    print("Received two-variance p-value test request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['hypothesisType', 'alpha', 'sampleSize1', 'sampleVariance1', 
                          'sampleSize2', 'sampleVariance2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        hypothesis_type = data['hypothesisType']
        alpha = float(data['alpha'])
        n1 = int(data['sampleSize1'])
        s1_squared = float(data['sampleVariance1'])
        n2 = int(data['sampleSize2'])
        s2_squared = float(data['sampleVariance2'])
        
        # Validate inputs
        if n1 < 2 or n2 < 2:
            return jsonify({'error': 'Sample sizes must be at least 2'}), 400
        if s1_squared <= 0 or s2_squared <= 0:
            return jsonify({'error': 'Sample variances must be positive'}), 400
        
        # Calculate F-statistic (always put larger variance in numerator)
        if s1_squared >= s2_squared:
            f_statistic = s1_squared / s2_squared
            df1 = n1 - 1  # degrees of freedom numerator
            df2 = n2 - 1  # degrees of freedom denominator
            larger_variance = "first sample"
        else:
            f_statistic = s2_squared / s1_squared
            df1 = n2 - 1
            df2 = n1 - 1
            larger_variance = "second sample"
        
        # Calculate p-value based on test type
        if hypothesis_type == 'two-tailed':
            p_value = 2 * min(f.cdf(f_statistic, df1, df2), 1 - f.cdf(f_statistic, df1, df2))
            p_value_direction = "two-tailed"
        elif hypothesis_type == 'right-tailed':
            p_value = 1 - f.cdf(f_statistic, df1, df2)
            p_value_direction = "right-tailed"
        elif hypothesis_type == 'left-tailed':
            p_value = f.cdf(f_statistic, df1, df2)
            p_value_direction = "left-tailed"
        else:
            return jsonify({'error': 'Invalid hypothesis type'}), 400
        
        # Determine conclusion
        if p_value <= alpha:
            conclusion = "Reject the null hypothesis (H₀)"
        else:
            conclusion = "Fail to reject the null hypothesis (H₀)"
        
        # ===== Create F-Distribution Visualization for P-Value Method =====
        fig, ax = plt.subplots(figsize=(10, 6))

        # Determine plot range dynamically
        plot_margin = 0.5
        x_min = 0  # F-distribution starts at 0
        x_max = max(4, f_statistic + 3, f.ppf(0.999, df1, df2))  # Use 99.9th percentile as upper bound
        x_vals = np.linspace(x_min, x_max, 1000)
        y_vals = f.pdf(x_vals, df1, df2)

        # Plot F-distribution
        ax.plot(x_vals, y_vals, 'b-', label=f'F-Distribution (df1={df1}, df2={df2})', linewidth=2)

        # Shade p-value region
        if hypothesis_type == 'two-tailed':
            # For two-tailed test, we need to consider both tails
            lower_crit = f.ppf(alpha/2, df1, df2)
            upper_crit = f.ppf(1 - alpha/2, df1, df2)
            
            # Shade the appropriate tails based on F-statistic position
            if f_statistic >= 1:  # In upper tail
                p_value_area = x_vals[x_vals >= f_statistic]
                ax.fill_between(p_value_area, f.pdf(p_value_area, df1, df2), 
                                color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
                # Also shade mirror image in lower tail
                mirror_f = 1/f_statistic
                mirror_area = x_vals[x_vals <= mirror_f]
                ax.fill_between(mirror_area, f.pdf(mirror_area, df1, df2), 
                                color='green', alpha=0.3)
            else:  # In lower tail
                p_value_area = x_vals[x_vals <= f_statistic]
                ax.fill_between(p_value_area, f.pdf(p_value_area, df1, df2), 
                                color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
                # Also shade mirror image in upper tail
                mirror_f = 1/f_statistic
                mirror_area = x_vals[x_vals >= mirror_f]
                ax.fill_between(mirror_area, f.pdf(mirror_area, df1, df2), 
                                color='green', alpha=0.3)
            
        elif hypothesis_type == 'right-tailed':
            p_value_area = x_vals[x_vals >= f_statistic]
            ax.fill_between(p_value_area, f.pdf(p_value_area, df1, df2), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')
            
        else:  # left-tailed
            p_value_area = x_vals[x_vals <= f_statistic]
            ax.fill_between(p_value_area, f.pdf(p_value_area, df1, df2), 
                            color='green', alpha=0.3, label=f'p-value ({p_value:.4f})')

        # Shade alpha region (rejection region)
        if hypothesis_type == 'two-tailed':
            lower_crit = f.ppf(alpha/2, df1, df2)
            upper_crit = f.ppf(1 - alpha/2, df1, df2)
            
            alpha_lower = x_vals[x_vals <= lower_crit]
            alpha_upper = x_vals[x_vals >= upper_crit]
            
            ax.fill_between(alpha_lower, f.pdf(alpha_lower, df1, df2), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.fill_between(alpha_upper, f.pdf(alpha_upper, df1, df2), 
                            color='orange', alpha=0.2)
            
            # Draw critical value lines
            ax.plot([lower_crit, lower_crit], [0, f.pdf(lower_crit, df1, df2)], 
                    color='red', linestyle='--', linewidth=1.5)
            ax.plot([upper_crit, upper_crit], [0, f.pdf(upper_crit, df1, df2)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Label critical values
            ax.text(lower_crit - 0.1, f.pdf(lower_crit, df1, df2) + 0.01, 
                    f'Lower CV: {lower_crit:.2f}', ha='right', va='bottom', color='red')
            ax.text(upper_crit + 0.1, f.pdf(upper_crit, df1, df2) + 0.01, 
                    f'Upper CV: {upper_crit:.2f}', ha='left', va='bottom', color='red')
            
        else:
            crit_val = f.ppf(1 - alpha, df1, df2) if hypothesis_type == 'right-tailed' else f.ppf(alpha, df1, df2)
            alpha_area = x_vals[x_vals >= crit_val] if hypothesis_type == 'right-tailed' else x_vals[x_vals <= crit_val]
            
            ax.fill_between(alpha_area, f.pdf(alpha_area, df1, df2), 
                            color='orange', alpha=0.2, label=f'α region ({alpha})')
            ax.plot([crit_val, crit_val], [0, f.pdf(crit_val, df1, df2)], 
                    color='red', linestyle='--', linewidth=1.5)
            
            # Label critical value
            cv_offset = 0.1 if hypothesis_type == 'right-tailed' else -0.1
            cv_ha = 'left' if hypothesis_type == 'right-tailed' else 'right'
            ax.text(crit_val + cv_offset, f.pdf(crit_val, df1, df2) + 0.01, 
                    f'CV: {crit_val:.2f}', ha=cv_ha, va='bottom', color='red')

        # Plot test statistic line
        ax.plot([f_statistic, f_statistic], [0, f.pdf(f_statistic, df1, df2)], 
                color='green', linestyle='-', linewidth=2)
        ts_y_pos = f.pdf(f_statistic, df1, df2) + 0.02

        # Label test statistic
        if hypothesis_type == 'two-tailed':
            f_stat_ha = 'left' if f_statistic >= 1 else 'right'
            f_stat_offset = 0.1 if f_statistic >= 1 else -0.1
        else:
            if (hypothesis_type == 'right-tailed' and f_statistic > crit_val) or \
            (hypothesis_type == 'left-tailed' and f_statistic < crit_val):
                # In rejection region
                f_stat_ha = 'left' if hypothesis_type == 'right-tailed' else 'right'
                f_stat_offset = 0.1 if hypothesis_type == 'right-tailed' else -0.1
            else:
                # Not in rejection region
                f_stat_ha = 'right' if hypothesis_type == 'right-tailed' else 'left'
                f_stat_offset = -0.1 if hypothesis_type == 'right-tailed' else 0.1

        ax.text(f_statistic + f_stat_offset, ts_y_pos,
                f'F-Stat: {f_statistic:.2f}', 
                ha=f_stat_ha, va='bottom', color='green')

        # Formatting
        ax.set_title('F-Test for Equality of Variances (P-Value Method)', fontsize=14, pad=20)
        ax.set_xlabel('F-Value', labelpad=10)
        ax.set_ylabel('Probability Density', labelpad=10)
        ax.set_xticks(np.linspace(0, x_max, min(10, int(x_max)+1)))
        ax.set_yticks(np.linspace(0, max(y_vals)+0.1, 10))
        ax.set_ylim(0, max(y_vals) + 0.15)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], color='blue', lw=2, label=f'F-Distribution (df1={df1}, df2={df2})'),
            Patch(facecolor='green', alpha=0.3, label=f'p-value ({p_value:.4f})'),
            Patch(facecolor='orange', alpha=0.2, label=f'α region ({alpha})'),
            Line2D([0], [0], color='green', lw=2, label=f'Test Statistic ({f_statistic:.2f})'),
            Line2D([0], [0], color='red', linestyle='--', lw=1.5, label='Critical Value(s)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', frameon=True)

        # Adjust layout to prevent clipping
        plt.tight_layout()

        # Save plot to base64
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')
        buf.close()
        
        # Initialize explanation steps
        steps = []
        
        # Add hypothesis info
        steps.append(f"<strong>Step 1: Hypothesis Setup</strong>")
        steps.append(f"• Null Hypothesis (H₀): σ₁² = σ₂² (variances are equal)")
        if hypothesis_type == 'two-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ₁² ≠ σ₂² (Two-tailed test)")
        elif hypothesis_type == 'right-tailed':
            steps.append(f"• Alternative Hypothesis (H₁): σ₁² > σ₂² (Right-tailed test)")
        else:
            steps.append(f"• Alternative Hypothesis (H₁): σ₁² < σ₂² (Left-tailed test)")
        steps.append(f"• Significance Level (α): {alpha}")
        
        # Add sample information
        steps.append("<strong>Step 2: Sample Information</strong>")
        steps.append(f"<strong>Sample 1:</strong>")
        steps.append(f"• Sample size (n₁): {n1}")
        steps.append(f"• Sample variance (s₁²): {round(s1_squared, 4)}")
        
        steps.append(f"<strong>Sample 2:</strong>")
        steps.append(f"• Sample size (n₂): {n2}")
        steps.append(f"• Sample variance (s₂²): {round(s2_squared, 4)}")
        
        # Add F-statistic calculation
        steps.append("<strong>Step 3: Calculate F-Statistic</strong>")
        steps.append(f"• Larger variance is from the {larger_variance}")
        if s1_squared >= s2_squared:
            steps.append(f"• F = s₁² / s₂² = {round(s1_squared, 4)} / {round(s2_squared, 4)} = {round(f_statistic, 4)}")
        else:
            steps.append(f"• F = s₂² / s₁² = {round(s2_squared, 4)} / {round(s1_squared, 4)} = {round(f_statistic, 4)}")
        steps.append(f"• Degrees of Freedom (numerator): df₁ = n₁ - 1 = {df1}")
        steps.append(f"• Degrees of Freedom (denominator): df₂ = n₂ - 1 = {df2}")
        
        # Add p-value calculation
        steps.append("<strong>Step 4: Calculate P-value</strong>")
        steps.append(f"• {p_value_direction} p-value calculation")
        steps.append(f"• P-value = {round(p_value, 6)}")
        steps.append(f"• Compare p-value ({round(p_value, 6)}) with α ({alpha})")
        
        # Add decision
        steps.append("<strong>Step 5: Make Decision</strong>")
        if p_value <= alpha:
            steps.append(f"• Since p-value ≤ α ({round(p_value, 6)} ≤ {alpha}), we reject H₀")
        else:
            steps.append(f"• Since p-value > α ({round(p_value, 6)} > {alpha}), we fail to reject H₀")
        steps.append(f"• Conclusion: {conclusion}")
        
        # Prepare results
        result = {
            'testStatistic': round(f_statistic, 4),
            'pValue': round(p_value, 6),
            'df1': df1,
            'df2': df2,
            'distribution': 'F-distribution',
            'conclusion': conclusion,
            'steps': steps,
            'sampleVariance1': round(s1_squared, 4),
            'sampleVariance2': round(s2_squared, 4),
            'largerVariance': larger_variance,
            'alpha': alpha,
            'plot': plot_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------- Confidence Interval Method For Difference between Variances --------------- #

@app.route('/calculate_two_variances_ci', methods=['POST'])
def calculate_two_variances_ci():
    print("Received two-variance confidence interval test request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        required_fields = ['confidenceLevel', 'sampleSize1', 'sampleVariance1', 
                          'sampleSize2', 'sampleVariance2']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Extract and convert data
        confidence_level = float(data['confidenceLevel'])
        alpha = 1 - confidence_level
        n1 = int(data['sampleSize1'])
        s1_squared = float(data['sampleVariance1'])
        n2 = int(data['sampleSize2'])
        s2_squared = float(data['sampleVariance2'])
        
        # Validate inputs
        if n1 < 2 or n2 < 2:
            return jsonify({'error': 'Sample sizes must be at least 2'}), 400
        if s1_squared <= 0 or s2_squared <= 0:
            return jsonify({'error': 'Sample variances must be positive'}), 400
        
        # Calculate variance ratio and degrees of freedom
        variance_ratio = s1_squared / s2_squared
        df1 = n1 - 1  # degrees of freedom numerator
        df2 = n2 - 1  # degrees of freedom denominator
        
        # Calculate critical F-values
        f_lower = f.ppf(alpha/2, df1, df2)
        f_upper = f.ppf(1 - alpha/2, df1, df2)
        
        # Calculate confidence interval bounds
        lower_bound = variance_ratio / f_upper
        upper_bound = variance_ratio / f_lower
        
        # Determine conclusion
        if 1 >= lower_bound and 1 <= upper_bound:
            conclusion = "The confidence interval contains 1 - no significant difference between variances"
        else:
            conclusion = "The confidence interval does not contain 1 - significant difference between variances"
        
        # Initialize explanation steps
        steps = []
        
        # Add basic info
        steps.append(f"<strong>Step 1: Setup</strong>")
        steps.append(f"• Confidence Level: {confidence_level*100}%")
        steps.append(f"• Variance Ratio (s₁²/s₂²): {round(variance_ratio, 4)}")
        
        # Add sample information
        steps.append("<strong>Step 2: Sample Information</strong>")
        steps.append(f"<strong>Sample 1:</strong>")
        steps.append(f"• Sample size (n₁): {n1}")
        steps.append(f"• Sample variance (s₁²): {round(s1_squared, 4)}")
        
        steps.append(f"<strong>Sample 2:</strong>")
        steps.append(f"• Sample size (n₂): {n2}")
        steps.append(f"• Sample variance (s₂²): {round(s2_squared, 4)}")
        
        # Add degrees of freedom
        steps.append("<strong>Step 3: Degrees of Freedom</strong>")
        steps.append(f"• df₁ (numerator) = n₁ - 1 = {df1}")
        steps.append(f"• df₂ (denominator) = n₂ - 1 = {df2}")
        
        # Add critical values
        steps.append("<strong>Step 4: Critical F-values</strong>")
        steps.append(f"• F(α/2, df₁, df₂) = F({1-(alpha/2)}, {df1}, {df2}) = {round(f_lower, 4)}")
        steps.append(f"• F(1-α/2, df₁, df₂) = F({round(alpha/2, 4)}, {df1}, {df2}) = {round(f_upper, 4)}")
        
        # Add confidence interval calculation
        steps.append("<strong>Step 5: Confidence Interval Calculation</strong>")
        steps.append(f"• Lower bound = (s₁²/s₂²)/F_upper = {round(variance_ratio,4)}/{round(f_upper,4)} = {round(lower_bound,4)}")
        steps.append(f"• Upper bound = (s₁²/s₂²)/F_lower = {round(variance_ratio,4)}/{round(f_lower,4)} = {round(upper_bound,4)}")
        steps.append(f"• {confidence_level*100}% Confidence Interval: [{round(lower_bound,4)}, {round(upper_bound,4)}]")
        
        # Add interpretation
        steps.append("<strong>Step 6: Interpretation</strong>")
        if 1 >= lower_bound and 1 <= upper_bound:
            steps.append(f"• The interval [{round(lower_bound,4)}, {round(upper_bound,4)}] contains 1")
            steps.append("• We cannot conclude there is a significant difference between the variances")
        else:
            steps.append(f"• The interval [{round(lower_bound,4)}, {round(upper_bound,4)}] does not contain 1")
            steps.append("• We conclude there is a significant difference between the variances")
        
        # Prepare results
        result = {
            'varianceRatio': round(variance_ratio, 4),
            'confidenceInterval': [round(lower_bound, 4), round(upper_bound, 4)],
            'confidenceLevel': confidence_level,
            'df1': df1,
            'df2': df2,
            'criticalFLower': round(f_lower, 4),
            'criticalFUpper': round(f_upper, 4),
            'conclusion': conclusion,
            'steps': steps,
            'sampleVariance1': round(s1_squared, 4),
            'sampleVariance2': round(s2_squared, 4)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ---------------  Statistical Calculations --------------- #

@app.route('/calculate_statistics', methods=['POST'])
def calculate_statistics():
    print("Received statistics calculation request!")
    try:
        data = request.get_json()
        print("Data received:", data)
        
        # Validate required fields
        if 'data' not in data or not data['data']:
            return jsonify({'error': 'Missing required field: data'}), 400
            
        # Extract and clean data
        data_str = data['data'].strip()
        
        # Parse input into numbers
        try:
            # Handle both comma and space separated values
            numbers = [float(item) for item in data_str.replace(',', ' ').split()]
        except ValueError as e:
            return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
        
        if len(numbers) < 2:
            return jsonify({'error': 'At least 2 data points are required'}), 400
        
        # Calculate statistics
        n = len(numbers)
        mean = sum(numbers) / n
        variance = sum((x - mean) ** 2 for x in numbers) / (n - 1)
        std_dev = math.sqrt(variance)
        sorted_data = sorted(numbers)
        
        # Initialize explanation steps
        steps = []
        
        # Add basic info
        steps.append(f"<strong>Step 1: Input Data</strong>")
        steps.append(f"• Raw data: {data_str}")
        steps.append(f"• Parsed numbers: {numbers}")
        steps.append(f"• Number of data points (n): {n}")
        
        # Mean calculation steps
        steps.append("<strong>Step 2: Mean Calculation</strong>")
        steps.append(f"• Formula: x̄ = (Σxᵢ) / n")
        steps.append(f"• Sum of values (Σxᵢ): {sum(numbers)}")
        steps.append(f"• Mean (x̄) = {sum(numbers)} / {n} = {round(mean, 4)}")
        
        # Variance calculation steps
        steps.append("<strong>Step 3: Variance Calculation</strong>")
        steps.append(f"• Formula: s² = Σ(xᵢ - x̄)² / (n - 1)")
        squared_diffs = [(x - mean) ** 2 for x in numbers]
        steps.append(f"• Squared differences: {[round(x, 4) for x in squared_diffs]}")
        steps.append(f"• Sum of squared differences: {round(sum(squared_diffs), 4)}")
        steps.append(f"• Variance (s²) = {round(sum(squared_diffs), 4)} / {n - 1} = {round(variance, 4)}")
        
        # Standard deviation calculation steps
        steps.append("<strong>Step 4: Standard Deviation Calculation</strong>")
        steps.append(f"• Formula: s = √(s²)")
        steps.append(f"• Standard Deviation (s) = √({round(variance, 4)}) = {round(std_dev, 4)}")
        
        # Sorted data
        steps.append("<strong>Step 5: Sorted Data</strong>")
        steps.append(f"• Sorted values (ascending order): {sorted_data}")
        
        # Interpretation
        steps.append("<strong>Interpretation:</strong>")
        steps.append(f"The mean value of your dataset is {round(mean, 4)}, indicating the central tendency.")
        steps.append(f"The variance of {round(variance, 4)} measures how spread out the data points are.")
        steps.append(f"The standard deviation of {round(std_dev, 4)} shows the typical distance from the mean.")
        
        # Prepare results
        result = {
            'dataCount': n,
            'mean': round(mean, 4),
            'variance': round(variance, 4),
            'stdDev': round(std_dev, 4),
            'sortedData': [round(x, 4) for x in sorted_data],
            'steps': steps,
            'interpretation': f"Dataset with {n} points has mean {round(mean, 4)}, variance {round(variance, 4)}, and standard deviation {round(std_dev, 4)}"
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)