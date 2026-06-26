import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define paths
CODE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(CODE_DIR, "data")
PLOTS_DIR = os.path.join(CODE_DIR, "plots")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_data.csv")

os.makedirs(PLOTS_DIR, exist_ok=True)

def generate_visualizations():
    print("=" * 60)
    print("      GraphQL vs REST Data Visualization Generator")
    print("=" * 60)
    
    if not os.path.exists(RAW_DATA_PATH):
        print(f"[ERROR] Raw data file not found at: {RAW_DATA_PATH}")
        print("Please run collector.py or generate_samples.py first.")
        return
        
    df = pd.read_csv(RAW_DATA_PATH)
    df_clean = df[df["status_code"] == 200].copy()
    df_clean["endpoint"] = df_clean["endpoint"].str.upper()
    
    if df_clean.empty:
        print("[ERROR] No successful requests to visualize.")
        return

    # Use seaborn's clean, modern visual style
    sns.set_theme(style="whitegrid")
    
    # Harmonious premium color palette
    # REST: Cool Blue, GraphQL: Modern Magenta
    palette = {"REST": "#1F77B4", "GraphQL": "#D62728"}
    
    # ----------------------------------------------------
    # PLOT 1: LATENCY BOXPLOT
    # ----------------------------------------------------
    print("Generating latency boxplot...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    
    # Create the boxplot
    sns.boxplot(
        data=df_clean,
        x="endpoint",
        y="latency_ms",
        hue="api_type",
        palette=palette,
        width=0.6,
        fliersize=4,
        linewidth=1.2,
        ax=ax
    )
    
    # Aesthetics
    ax.set_title("Response Time (Latency) Comparison\nGitHub REST vs. GraphQL (official-stockfish/Stockfish)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Resource Endpoint", fontsize=11, labelpad=10)
    ax.set_ylabel("Latency (milliseconds)", fontsize=11, labelpad=10)
    
    # Tick labels are already upper-case from the DataFrame
    
    # Legend improvements
    ax.legend(title="API Paradigm", title_fontsize="10", loc="upper right", frameon=True, shadow=False)
    
    # Tight layout to avoid text cuts
    plt.tight_layout()
    
    latency_plot_path = os.path.join(PLOTS_DIR, "latency_comparison.png")
    plt.savefig(latency_plot_path, dpi=300)
    plt.close()
    print(f"Latency plot saved to: {latency_plot_path}")
    
    # ----------------------------------------------------
    # PLOT 2: SIZE BAR CHART (KB)
    # ----------------------------------------------------
    print("Generating payload size comparison bar chart...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    
    # Calculate means for sizing
    # Size in KB
    df_clean["size_kb"] = df_clean["size_bytes"] / 1024.0
    df_means = df_clean.groupby(["endpoint", "api_type"])["size_kb"].mean().reset_index()
    
    # Create grouped bar plot
    bar_plot = sns.barplot(
        data=df_means,
        x="endpoint",
        y="size_kb",
        hue="api_type",
        palette=palette,
        width=0.6,
        edgecolor="black",
        linewidth=0.8,
        ax=ax
    )
    
    # Add labels on top of the bars
    for container in ax.containers:
        labels = [f"{v.get_height():.2f} KB" if v.get_height() >= 1.0 else f"{v.get_height() * 1024:.0f} B" for v in container]
        ax.bar_label(container, labels=labels, label_type="edge", padding=3, fontsize=9, fontweight="semibold")
        
    # Set y-axis limits with some headroom for labels
    max_height = df_means["size_kb"].max()
    ax.set_ylim(0, max_height * 1.15)
    
    # Aesthetics
    ax.set_title("Average Payload Size Comparison (Log-ish distribution visual)\nGitHub REST vs. GraphQL (official-stockfish/Stockfish)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Resource Endpoint", fontsize=11, labelpad=10)
    ax.set_ylabel("Payload Size (KB)", fontsize=11, labelpad=10)
    # Tick labels are already upper-case from the DataFrame
    ax.legend(title="API Paradigm", title_fontsize="10", loc="upper right")
    
    plt.tight_layout()
    
    size_plot_path = os.path.join(PLOTS_DIR, "size_comparison.png")
    plt.savefig(size_plot_path, dpi=300)
    plt.close()
    print(f"Size plot saved to: {size_plot_path}")
    
    # ----------------------------------------------------
    # PLOT 3: SIZE COMPARISON WITH LOG SCALE (For better side-by-side scale visualization)
    # ----------------------------------------------------
    print("Generating log-scaled payload size plot for high visual discrepancy...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    
    # Boxplot of size on log scale to show actual distribution and massive gap
    sns.boxplot(
        data=df_clean,
        x="endpoint",
        y="size_kb",
        hue="api_type",
        palette=palette,
        width=0.6,
        ax=ax
    )
    
    ax.set_yscale("log")
    ax.set_title("Payload Size Distribution (Logarithmic Scale)\nVisualizing the massive gap in data transfer sizes", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Resource Endpoint", fontsize=11, labelpad=10)
    ax.set_ylabel("Payload Size (KB) - Log Scale", fontsize=11, labelpad=10)
    # Tick labels are already upper-case from the DataFrame
    ax.legend(title="API Paradigm", loc="lower left")
    
    # Formatting Y labels for log scale (e.g. 0.1 KB, 1 KB, 10 KB, 100 KB)
    from matplotlib.ticker import LogFormatterMathtext
    ax.yaxis.set_major_formatter(LogFormatterMathtext())
    
    plt.tight_layout()
    log_size_plot_path = os.path.join(PLOTS_DIR, "size_comparison_log.png")
    plt.savefig(log_size_plot_path, dpi=300)
    plt.close()
    print(f"Log Size plot saved to: {log_size_plot_path}")
    
    print("All visualizations generated successfully!")
    print("=" * 60)

if __name__ == "__main__":
    generate_visualizations()
