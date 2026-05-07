from __future__ import annotations

import math
from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
FIGS_DIR = OUTPUT_DIR / "figs"
FIGS_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';', parse_dates=['created_at', 'ended_at'], low_memory=False)
    return df


def summarize_medians(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        'changed_files', 'additions', 'deletions',
        'review_time_hours', 'description_char_count',
        'participants_count', 'comments_count', 'review_count'
    ]
    medians = {m: df[m].median() for m in metrics}
    return pd.Series(medians).to_frame('median')


def test_numeric_vs_status(df: pd.DataFrame, metric: str) -> dict:
    # Compare distribution between MERGED and CLOSED using Mann-Whitney U (non-parametric)
    a = df.loc[df['final_status'] == 'MERGED', metric].dropna()
    b = df.loc[df['final_status'] == 'CLOSED', metric].dropna()
    if len(a) < 5 or len(b) < 5:
        return {'stat': math.nan, 'pvalue': math.nan, 'n_merged': len(a), 'n_closed': len(b)}
    stat, p = stats.mannwhitneyu(a, b, alternative='two-sided')
    return {'stat': stat, 'pvalue': p, 'n_merged': len(a), 'n_closed': len(b)}


def corr_spearman(df: pd.DataFrame, x: str, y: str) -> dict:
    series_x = df[x].dropna()
    series_y = df[y].dropna()
    common = pd.concat([series_x, series_y], axis=1).dropna()
    if len(common) < 5:
        return {'rho': math.nan, 'pvalue': math.nan, 'n': len(common)}
    rho, p = stats.spearmanr(common[x], common[y])
    return {'rho': rho, 'pvalue': p, 'n': len(common)}


def plot_box_by_status(df: pd.DataFrame, metric: str, outdir: Path) -> Path:
    plt.figure(figsize=(6, 4))
    sns.boxplot(x='final_status', y=metric, data=df)
    plt.title(f'{metric} por status final')
    out = outdir / f'box_{metric}.png'
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def plot_scatter_with_reviews(df: pd.DataFrame, metric: str, outdir: Path) -> Path:
    plt.figure(figsize=(6, 4))
    sns.scatterplot(x=metric, y='review_count', data=df, alpha=0.6)
    plt.title(f'review_count vs {metric}')
    out = outdir / f'scatter_reviews_{metric}.png'
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def run_analysis(path: Path, outdir: Path) -> None:
    df = load_dataset(path)

    # Basic cleaning / type coercions
    numeric_cols = ['changed_files', 'additions', 'deletions', 'review_time_hours',
                    'description_char_count', 'participants_count', 'comments_count', 'review_count']
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # Summaries
    medians = summarize_medians(df)
    medians.to_csv(outdir / 'medians.csv')

    # RQ A: relations with final_status (MERGED vs CLOSED)
    rq_a_results = {}
    for metric in ['changed_files', 'additions', 'deletions', 'review_time_hours', 'description_char_count', 'participants_count', 'comments_count']:
        rq_a_results[metric] = test_numeric_vs_status(df, metric)
        plot_box_by_status(df, metric, outdir)

    rq_a_df = pd.DataFrame(rq_a_results).T
    rq_a_df.to_csv(outdir / 'rq_a_status_comparisons.csv')

    # RQ B: correlations with number of reviews
    rq_b_results = {}
    for metric in ['changed_files', 'additions', 'deletions', 'review_time_hours', 'description_char_count', 'participants_count', 'comments_count']:
        rq_b_results[metric] = corr_spearman(df, metric, 'review_count')
        plot_scatter_with_reviews(df, metric, outdir)

    rq_b_df = pd.DataFrame(rq_b_results).T
    rq_b_df.to_csv(outdir / 'rq_b_correlations_with_reviews.csv')

    print('Análise concluída. Arquivos escritos em:', outdir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Análise e visualizações para Lab03 Sprint1')
    parser.add_argument('--input', type=Path, default=OUTPUT_DIR / 'prs_sprint1.csv')
    parser.add_argument('--outdir', type=Path, default=FIGS_DIR)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run_analysis(args.input, args.outdir)
