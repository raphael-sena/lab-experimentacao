import os
import numpy as np
import pandas as pd
from scipy import stats

# Define paths
CODE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CODE_DIR, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_data.csv")
RESULTS_TXT_PATH = os.path.join(DATA_DIR, "statistical_results.txt")

def cohens_d(x, y):
    """Calculate Cohen's d effect size for two independent samples."""
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    var_x = np.var(x, ddof=1)
    var_y = np.var(y, ddof=1)
    
    # Handle zero variance case
    if var_x == 0 and var_y == 0:
        return 0.0
        
    pooled_std = np.sqrt(((nx - 1) * var_x + (ny - 1) * var_y) / dof)
    if pooled_std == 0:
        return 0.0
        
    return (np.mean(x) - np.mean(y)) / pooled_std

def cliffs_delta(x, y):
    """Calculate Cliff's Delta non-parametric effect size for two independent samples."""
    nx = len(x)
    ny = len(y)
    
    # Efficient calculation using numpy broadcasting
    x_arr = np.array(x)
    y_arr = np.array(y)
    
    diff = x_arr[:, None] - y_arr
    greater = np.sum(diff > 0)
    less = np.sum(diff < 0)
    
    delta = (greater - less) / (nx * ny)
    return delta

def interpret_cliffs_delta(delta):
    """Interpret Cliff's Delta magnitude based on Romano et al. (2006)."""
    abs_d = abs(delta)
    if abs_d < 0.147:
        return "Negligible"
    elif abs_d < 0.33:
        return "Small"
    elif abs_d < 0.474:
        return "Medium"
    else:
        return "Large"

def run_analysis():
    print("=" * 60)
    print("      GraphQL vs REST Statistical Hypothesis Analyzer")
    print("=" * 60)
    
    if not os.path.exists(RAW_DATA_PATH):
        print(f"[ERROR] Raw data file not found at: {RAW_DATA_PATH}")
        print("Please run collector.py or generate_samples.py first.")
        return
        
    df = pd.read_csv(RAW_DATA_PATH)
    df_clean = df[df["status_code"] == 200].copy()
    
    if df_clean.empty:
        print("[ERROR] No successful requests to analyze.")
        return
        
    endpoints = df_clean["endpoint"].unique()
    alpha = 0.05
    
    output_lines = []
    
    header = (
        "======================================================================\n"
        "                  STATISTICAL HYPOTHESIS TESTING REPORT\n"
        "                  GraphQL vs REST API Controlled Experiment\n"
        "======================================================================\n"
        f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Total successful trials: {len(df_clean)} (REST: {len(df_clean[df_clean['api_type'] == 'REST'])}, GraphQL: {len(df_clean[df_clean['api_type'] == 'GraphQL'])})\n"
        f"Significance level (alpha): {alpha}\n"
        "======================================================================\n\n"
    )
    output_lines.append(header)
    
    for endpoint in sorted(endpoints):
        rest_data = df_clean[(df_clean["endpoint"] == endpoint) & (df_clean["api_type"] == "REST")]
        gql_data = df_clean[(df_clean["endpoint"] == endpoint) & (df_clean["api_type"] == "GraphQL")]
        
        endpoint_header = f"RESOURCE ENDPOINT: '{endpoint.upper()}'\n" + "-" * 40 + "\n"
        output_lines.append(endpoint_header)
        
        # ----------------------------------------------------
        # ANALYSIS FOR RQ1: RESPONSE TIME (LATENCY)
        # ----------------------------------------------------
        rest_lat = rest_data["latency_ms"].values
        gql_lat = gql_data["latency_ms"].values
        
        # 1. Normality Test (Shapiro-Wilk)
        # S-W returns (statistic, p-value)
        _, shapiro_p_rest = stats.shapiro(rest_lat) if len(rest_lat) >= 3 else (0, 0)
        _, shapiro_p_gql = stats.shapiro(gql_lat) if len(gql_lat) >= 3 else (0, 0)
        
        rest_is_normal = shapiro_p_rest > alpha
        gql_is_normal = shapiro_p_gql > alpha
        
        output_lines.append("RQ1: Response Time (Latency) Analysis\n")
        output_lines.append(f"  - REST Latency (ms):    Mean={np.mean(rest_lat):.2f}, Median={np.median(rest_lat):.2f}, Std={np.std(rest_lat, ddof=1):.2f}\n")
        output_lines.append(f"  - GraphQL Latency (ms): Mean={np.mean(gql_lat):.2f}, Median={np.median(gql_lat):.2f}, Std={np.std(gql_lat, ddof=1):.2f}\n")
        output_lines.append(f"  - Normality Test (Shapiro-Wilk): REST p-value={shapiro_p_rest:.4f} ({'Normal' if rest_is_normal else 'Non-Normal'}), GraphQL p-value={shapiro_p_gql:.4f} ({'Normal' if gql_is_normal else 'Non-Normal'})\n")
        
        # Choose statistical test
        # Network latency is typically non-normal, so Mann-Whitney U is preferred unless both are normal.
        if rest_is_normal and gql_is_normal:
            # Independent Welch's T-Test (does not assume equal variance)
            t_stat, p_val = stats.ttest_ind(gql_lat, rest_lat, equal_var=False, alternative="less")
            test_used = "Welch's T-Test (One-Sided, GraphQL < REST)"
            eff_size = cohens_d(gql_lat, rest_lat)
            eff_desc = f"Cohen's d = {eff_size:.3f}"
        else:
            # Mann-Whitney U test (one-sided)
            # Alternative 'less': GQL distribution is stochastically smaller than REST (faster)
            u_stat, p_val = stats.mannwhitneyu(gql_lat, rest_lat, alternative="less")
            test_used = "Mann-Whitney U-Test (One-Sided, GraphQL < REST)"
            eff_size = cliffs_delta(gql_lat, rest_lat)
            eff_desc = f"Cliff's Delta = {eff_size:.3f} ({interpret_cliffs_delta(eff_size)})"
            
        reject_null_rq1 = p_val < alpha
        output_lines.append(f"  - Statistical Test:     {test_used}\n")
        output_lines.append(f"  - Test Statistic:       {u_stat if 'Mann-Whitney' in test_used else t_stat:.4f}\n")
        output_lines.append(f"  - p-value:              {p_val:.4g}\n")
        output_lines.append(f"  - Effect Size:          {eff_desc}\n")
        
        h0_time = "H0,1: GraphQL Latency >= REST Latency"
        h1_time = "H1,1: GraphQL Latency < REST Latency"
        
        if reject_null_rq1:
            decision_rq1 = f"REJECT NULL HYPOTHESIS ({h0_time}).\n    Conclusion: GraphQL responses are significantly FASTER than REST responses for this endpoint."
        else:
            decision_rq1 = f"FAIL TO REJECT NULL HYPOTHESIS ({h0_time}).\n    Conclusion: There is no statistically significant evidence that GraphQL is faster than REST."
            
        output_lines.append(f"  - Decision:             {decision_rq1}\n\n")
        
        # ----------------------------------------------------
        # ANALYSIS FOR RQ2: RESPONSE PAYLOAD SIZE
        # ----------------------------------------------------
        rest_size = rest_data["size_bytes"].values
        gql_size = gql_data["size_bytes"].values
        
        output_lines.append("RQ2: Response Payload Size (Bytes) Analysis\n")
        output_lines.append(f"  - REST Payload Size (Bytes):    Mean={np.mean(rest_size):.2f}, Median={np.median(rest_size):.2f}\n")
        output_lines.append(f"  - GraphQL Payload Size (Bytes): Mean={np.mean(gql_size):.2f}, Median={np.median(gql_size):.2f}\n")
        
        # Size variables in REST and GraphQL are often deterministic (fixed headers, fixed json structure).
        # Check if both distributions have zero variance.
        var_rest = np.var(rest_size)
        var_gql = np.var(gql_size)
        
        if var_rest == 0 and var_gql == 0:
            # Deterministic comparison
            output_lines.append("  - Statistical Test:     N/A (Deterministic - Zero Variance)\n")
            p_val_size = 0.0 if np.mean(gql_size) < np.mean(rest_size) else 1.0
            reject_null_rq2 = np.mean(gql_size) < np.mean(rest_size)
            eff_desc_size = "Cliff's Delta = -1.000 (Deterministic Absolute Difference)" if reject_null_rq2 else "Cliff's Delta = 0.000"
        else:
            # S-W test
            _, shapiro_p_rest_sz = stats.shapiro(rest_size) if len(rest_size) >= 3 else (0, 0)
            _, shapiro_p_gql_sz = stats.shapiro(gql_size) if len(gql_size) >= 3 else (0, 0)
            
            rest_sz_normal = shapiro_p_rest_sz > alpha
            gql_sz_normal = shapiro_p_gql_sz > alpha
            
            if rest_sz_normal and gql_sz_normal:
                t_stat_sz, p_val_size = stats.ttest_ind(gql_size, rest_size, equal_var=False, alternative="less")
                test_used_sz = "Welch's T-Test (One-Sided, GraphQL < REST)"
                eff_size_sz = cohens_d(gql_size, rest_size)
                eff_desc_size = f"Cohen's d = {eff_size_sz:.3f}"
            else:
                u_stat_sz, p_val_size = stats.mannwhitneyu(gql_size, rest_size, alternative="less")
                test_used_sz = "Mann-Whitney U-Test (One-Sided, GraphQL < REST)"
                eff_size_sz = cliffs_delta(gql_size, rest_size)
                eff_desc_size = f"Cliff's Delta = {eff_size_sz:.3f} ({interpret_cliffs_delta(eff_size_sz)})"
                
            reject_null_rq2 = p_val_size < alpha
            output_lines.append(f"  - Statistical Test:     {test_used_sz}\n")
            output_lines.append(f"  - p-value:              {p_val_size:.4g}\n")
            output_lines.append(f"  - Effect Size:          {eff_desc_size}\n")
            
        h0_size = "H0,2: GraphQL Payload Size >= REST Payload Size"
        h1_size = "H1,2: GraphQL Payload Size < REST Payload Size"
        
        if reject_null_rq2:
            reduction_pct = (1 - (np.mean(gql_size) / np.mean(rest_size))) * 100
            decision_rq2 = f"REJECT NULL HYPOTHESIS ({h0_size}).\n    Conclusion: GraphQL payload size is significantly SMALLER than REST payload size ({reduction_pct:.1f}% reduction)."
        else:
            decision_rq2 = f"FAIL TO REJECT NULL HYPOTHESIS ({h0_size}).\n    Conclusion: There is no statistically significant evidence that GraphQL payload size is smaller than REST."
            
        output_lines.append(f"  - Decision:             {decision_rq2}\n")
        output_lines.append("-" * 40 + "\n\n")
        
    # Write report to file
    report_content = "".join(output_lines)
    with open(RESULTS_TXT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Print the report to standard output
    print(report_content)
    print(f"Statistical analysis report saved to: {RESULTS_TXT_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    run_analysis()
