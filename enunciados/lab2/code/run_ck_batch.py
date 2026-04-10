"""
run_ck_batch.py
Roda o CK em todos os repos de repo_measurements_1000.csv que ainda não estão
em ck_summary.csv. Resumível: se interrompido, continua de onde parou.
Após analisar cada repo, o clone é deletado para economizar disco.

Uso:
    python run_ck_batch.py
    python run_ck_batch.py --start 50   # pula os primeiros 50 da fila
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

import requests

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
OUTPUT_DIR  = BASE_DIR / "output"
PROCESS_CSV = OUTPUT_DIR / "repo_measurements_1000.csv"
SUMMARY_CSV = OUTPUT_DIR / "ck_summary.csv"
REPOS_DIR   = OUTPUT_DIR / "repos"
CK_DIR      = OUTPUT_DIR / "ck"
CK_JAR      = CK_DIR / "ck.jar"

SUMMARY_FIELDS = [
    "full_name", "stars", "releases", "created_at",
    "cbo_median", "cbo_mean", "cbo_std",
    "dit_median", "dit_mean", "dit_std",
    "lcom_median", "lcom_mean", "lcom_std",
    "loc_median", "loc_mean", "loc_std",
    "num_classes",
]

# ──────────────────────────────────────────────────────────────────────────────
# CK jar
# ──────────────────────────────────────────────────────────────────────────────
def ensure_ck_jar() -> Path:
    if CK_JAR.exists():
        print(f"[CK] jar ok: {CK_JAR}")
        return CK_JAR

    CK_JAR.parent.mkdir(parents=True, exist_ok=True)
    jar_url = (
        "https://repo1.maven.org/maven2/com/github/mauricioaniche/ck"
        "/0.7.0/ck-0.7.0-jar-with-dependencies.jar"
    )
    print(f"[CK] baixando jar: {jar_url}")
    with requests.get(jar_url, stream=True, timeout=(15, 180)) as r:
        r.raise_for_status()
        with CK_JAR.open("wb") as fh:
            shutil.copyfileobj(r.raw, fh)
    print("[CK] jar salvo.")
    return CK_JAR

# ──────────────────────────────────────────────────────────────────────────────
# Clone
# ──────────────────────────────────────────────────────────────────────────────
def clone_repo(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", "--quiet", url, str(dest)],
        capture_output=True,
        timeout=300,
    )
    return result.returncode == 0

# ──────────────────────────────────────────────────────────────────────────────
# CK analysis
# ──────────────────────────────────────────────────────────────────────────────
def run_ck(jar: Path, repo_path: Path, out_dir: Path) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["java", "-jar", str(jar), str(repo_path),
         "false", "0", "false", str(out_dir) + os.sep],
        capture_output=True,
        timeout=300,
    )
    if result.returncode != 0:
        return None
    for candidate in [
        out_dir / "class.csv",
        out_dir.parent / f"{out_dir.name}class.csv",
    ]:
        if candidate.exists():
            return candidate
    return None

# ──────────────────────────────────────────────────────────────────────────────
# Statistics
# ──────────────────────────────────────────────────────────────────────────────
def _stats(values: list[float]) -> tuple[float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0
    return (
        statistics.median(values),
        statistics.mean(values),
        statistics.pstdev(values),
    )


def parse_class_csv(class_csv: Path) -> dict:
    cbo_v, dit_v, lcom_v, loc_v = [], [], [], []
    with class_csv.open(newline="", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            try:
                cbo_v.append(float(row.get("cbo", 0) or 0))
                dit_v.append(float(row.get("dit", 0) or 0))
                lcom_v.append(float(row.get("lcom", 0) or 0))
                loc_v.append(float(row.get("loc", 0) or 0))
            except ValueError:
                pass

    cbo_m,  cbo_mn,  cbo_s  = _stats(cbo_v)
    dit_m,  dit_mn,  dit_s  = _stats(dit_v)
    lcom_m, lcom_mn, lcom_s = _stats(lcom_v)
    loc_m,  loc_mn,  loc_s  = _stats(loc_v)

    return {
        "cbo_median":  round(cbo_m,  4), "cbo_mean":  round(cbo_mn,  4), "cbo_std":  round(cbo_s,  4),
        "dit_median":  round(dit_m,  4), "dit_mean":  round(dit_mn,  4), "dit_std":  round(dit_s,  4),
        "lcom_median": round(lcom_m, 4), "lcom_mean": round(lcom_mn, 4), "lcom_std": round(lcom_s, 4),
        "loc_median":  round(loc_m,  4), "loc_mean":  round(loc_mn,  4), "loc_std":  round(loc_s,  4),
        "num_classes": len(cbo_v),
    }

# ──────────────────────────────────────────────────────────────────────────────
# CSV I/O
# ──────────────────────────────────────────────────────────────────────────────
def load_done() -> set[str]:
    if not SUMMARY_CSV.exists():
        return set()
    with SUMMARY_CSV.open(encoding="utf-8") as fh:
        return {row["full_name"] for row in csv.DictReader(fh)}


def append_summary(row: dict) -> None:
    write_header = not SUMMARY_CSV.exists() or SUMMARY_CSV.stat().st_size == 0
    with SUMMARY_CSV.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SUMMARY_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def load_process_repos() -> list[dict]:
    with PROCESS_CSV.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Batch CK analysis for all repos")
    parser.add_argument("--start", type=int, default=0,
                        help="Skip the first N pending repos (for manual sharding)")
    args = parser.parse_args()

    repos = load_process_repos()
    done  = load_done()
    jar   = ensure_ck_jar()

    pending = [r for r in repos if r["full_name"] not in done]
    pending = pending[args.start:]
    total   = len(pending)

    print(f"[info] {len(done)} repos já processados, {total} na fila.")

    ok = skip = fail = 0

    for idx, repo in enumerate(pending, 1):
        full_name = repo["full_name"]
        url       = repo["url"]
        safe      = full_name.replace("/", "__")
        repo_path = REPOS_DIR / safe
        ck_out    = CK_DIR / "metrics" / safe

        print(f"[{idx}/{total}] {full_name}", end=" ", flush=True)

        # Clone
        try:
            cloned = clone_repo(url, repo_path)
        except subprocess.TimeoutExpired:
            cloned = False

        if not cloned:
            print("→ clone falhou, pulando")
            skip += 1
            continue

        # CK
        try:
            class_csv = run_ck(jar, repo_path, ck_out)
        except subprocess.TimeoutExpired:
            class_csv = None

        if class_csv is None:
            print("→ CK falhou, pulando")
            shutil.rmtree(repo_path, ignore_errors=True)
            shutil.rmtree(ck_out,    ignore_errors=True)
            skip += 1
            continue

        ck_metrics = parse_class_csv(class_csv)
        append_summary({
            "full_name":  full_name,
            "stars":      repo["stars"],
            "releases":   repo["releases"],
            "created_at": repo["created_at"],
            **ck_metrics,
        })

        # Libera disco
        shutil.rmtree(repo_path, ignore_errors=True)
        shutil.rmtree(ck_out,    ignore_errors=True)

        print(f"→ ok  classes={ck_metrics['num_classes']:4d}  "
              f"CBO={ck_metrics['cbo_median']:.2f}  "
              f"DIT={ck_metrics['dit_median']:.2f}  "
              f"LCOM={ck_metrics['lcom_median']:.2f}")
        ok += 1

    print(f"\nConcluído: {ok} ok | {skip} pulados | {fail} falhas")
    total_done = len(load_done())
    print(f"ck_summary.csv agora tem {total_done} repositórios.")


if __name__ == "__main__":
    main()
