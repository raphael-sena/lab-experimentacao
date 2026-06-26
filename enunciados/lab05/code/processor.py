import os
import pandas as pd
import json

# Define paths
CODE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CODE_DIR, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_data.csv")
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed_data.csv")
SUMMARY_JSON_PATH = os.path.join(DATA_DIR, "processed_summary.json")

def process_results():
    print("=" * 60)
    print("      GraphQL vs REST Data Processor & Summarizer")
    print("=" * 60)
    
    if not os.path.exists(RAW_DATA_PATH):
        print(f"[ERROR] Raw data file not found at: {RAW_DATA_PATH}")
        print("Please run collector.py or generate_samples.py first.")
        return
        
    # Read raw data
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Loaded {len(df)} records from raw data.")
    
    # Clean data (keep only status code 200)
    df_clean = df[df["status_code"] == 200].copy()
    print(f"Filtered to {len(df_clean)} successful requests (status_code == 200).")
    
    if df_clean.empty:
        print("[ERROR] No successful requests to process.")
        return
        
    # Group by endpoint and api_type to compute descriptive stats for both metrics
    grouped = df_clean.groupby(["endpoint", "api_type"])
    
    # Calculate stats for Latency (response time)
    latency_stats = grouped["latency_ms"].agg(
        count_latency_ms="count",
        mean_latency_ms="mean",
        median_latency_ms="median",
        std_latency_ms="std",
        min_latency_ms="min",
        max_latency_ms="max"
    ).reset_index()
    
    # Calculate stats for Size (bytes)
    size_stats = grouped["size_bytes"].agg(
        mean_size_bytes="mean",
        median_size_bytes="median",
        std_size_bytes="std",
        min_size_bytes="min",
        max_size_bytes="max",
        total_size_bytes="sum"
    ).reset_index()
    
    # Merge statistics
    merged_stats = pd.merge(
        latency_stats, 
        size_stats, 
        on=["endpoint", "api_type"]
    )
    
    # Save the processed data to CSV (great for BI tool dashboards)
    merged_stats.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Processed summary saved to CSV at: {PROCESSED_DATA_PATH}")
    
    # Generate JSON summary file for programmatic dashboard usage
    summary_dict = {}
    for endpoint in df_clean["endpoint"].unique():
        summary_dict[endpoint] = {}
        for api_type in df_clean["api_type"].unique():
            subset = df_clean[(df_clean["endpoint"] == endpoint) & (df_clean["api_type"] == api_type)]
            if not subset.empty:
                summary_dict[endpoint][api_type] = {
                    "latency_ms": {
                        "count": int(subset["latency_ms"].count()),
                        "mean": float(subset["latency_ms"].mean()),
                        "median": float(subset["latency_ms"].median()),
                        "std": float(subset["latency_ms"].std()) if subset["latency_ms"].count() > 1 else 0.0,
                        "min": float(subset["latency_ms"].min()),
                        "max": float(subset["latency_ms"].max())
                    },
                    "size_bytes": {
                        "count": int(subset["size_bytes"].count()),
                        "mean": float(subset["size_bytes"].mean()),
                        "median": float(subset["size_bytes"].median()),
                        "std": float(subset["size_bytes"].std()) if subset["size_bytes"].count() > 1 else 0.0,
                        "min": float(subset["size_bytes"].min()),
                        "max": float(subset["size_bytes"].max()),
                        "total_transferred": float(subset["size_bytes"].sum())
                    }
                }
                
    with open(SUMMARY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_dict, f, indent=4)
    print(f"Processed summary saved to JSON at: {SUMMARY_JSON_PATH}")
    
    # Print a markdown table of the descriptive statistics to console
    print("\n" + "#" * 60)
    print("### EXPERIMENTAL RESULTS - DESCRIPTIVE STATISTICS")
    print("#" * 60)
    
    # Format size columns to look readable
    display_df = merged_stats.copy()
    display_df["mean_latency_ms"] = display_df["mean_latency_ms"].round(2)
    display_df["std_latency_ms"] = display_df["std_latency_ms"].round(2)
    display_df["mean_size_kb"] = (display_df["mean_size_bytes"] / 1024).round(2)
    display_df["total_size_mb"] = (display_df["total_size_bytes"] / (1024 * 1024)).round(2)
    
    # Select columns to display
    cols_to_show = [
        "endpoint", "api_type", "count_latency_ms", 
        "mean_latency_ms", "median_latency_ms", "std_latency_ms",
        "mean_size_kb", "total_size_mb"
    ]
    rename_dict = {
        "count_latency_ms": "Trials",
        "mean_latency_ms": "Avg Latency (ms)",
        "median_latency_ms": "Median Latency (ms)",
        "std_latency_ms": "Std Dev Latency (ms)",
        "mean_size_kb": "Avg Size (KB)",
        "total_size_mb": "Total Data (MB)"
    }
    
    markdown_df = display_df[cols_to_show].rename(columns=rename_dict)
    print(markdown_df.to_markdown(index=False))
    print("=" * 60)

if __name__ == "__main__":
    process_results()
