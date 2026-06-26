import os
import csv
import random
from datetime import datetime, timedelta

# Output path
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_data.csv")

# Baseline statistics configuration
# REST values based on real-world GitHub API response payloads
REST_STATS = {
    "repo": {"size_mean": 6480, "size_std": 150, "time_mean": 125.0, "time_std": 20.0},
    "commits": {"size_mean": 124500, "size_std": 800, "time_mean": 195.0, "time_std": 35.0},
    "issues": {"size_mean": 96200, "size_std": 500, "time_mean": 175.0, "time_std": 30.0},
    "pulls": {"size_mean": 118400, "size_std": 900, "time_mean": 185.0, "time_std": 35.0}
}

# GraphQL values reflecting schema-limited queries (only requested fields)
GRAPHQL_STATS = {
    "repo": {"size_mean": 315, "size_std": 5, "time_mean": 145.0, "time_std": 25.0},
    "commits": {"size_mean": 5420, "size_std": 100, "time_mean": 160.0, "time_std": 30.0},
    "issues": {"size_mean": 2880, "size_std": 80, "time_mean": 150.0, "time_std": 25.0},
    "pulls": {"size_mean": 2980, "size_std": 80, "time_mean": 155.0, "time_std": 25.0}
}

def generate_data(num_trials=30):
    print(f"Generating mock data for {num_trials} trials...")
    
    tasks = []
    for trial in range(1, num_trials + 1):
        for api_type in ["REST", "GraphQL"]:
            for endpoint in ["repo", "commits", "issues", "pulls"]:
                tasks.append({
                    "trial": trial,
                    "api_type": api_type,
                    "endpoint": endpoint
                })
                
    # Randomize the execution order to match the real collector behavior
    random.shuffle(tasks)
    
    start_time = datetime.utcnow() - timedelta(minutes=num_trials * 2)
    
    with open(RAW_DATA_PATH, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["timestamp", "trial", "api_type", "endpoint", "latency_ms", "size_bytes", "status_code"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, task in enumerate(tasks):
            trial = task["trial"]
            api_type = task["api_type"]
            endpoint = task["endpoint"]
            
            # Determine base stats
            stats = REST_STATS[endpoint] if api_type == "REST" else GRAPHQL_STATS[endpoint]
            
            # Simulate response size with small gaussian noise (always positive)
            size = max(10, int(random.gauss(stats["size_mean"], stats["size_std"])))
            
            # Simulate response time using a log-normal distribution or gaussian + jitter
            # This creates a realistic long-tail latency distribution (network spikes)
            base_time = random.gauss(stats["time_mean"], stats["time_std"])
            
            # Add a 5% chance of network jitter spike (500ms - 900ms delay)
            if random.random() < 0.05:
                jitter = random.uniform(300, 700)
                latency = base_time + jitter
            else:
                latency = base_time
                
            latency = max(20.0, round(latency, 2))
            
            # Increment timestamp by ~1.5 seconds (request delay)
            current_time = start_time + timedelta(seconds=idx * 1.6)
            timestamp = current_time.isoformat() + "Z"
            
            writer.writerow({
                "timestamp": timestamp,
                "trial": trial,
                "api_type": api_type,
                "endpoint": endpoint,
                "latency_ms": latency,
                "size_bytes": size,
                "status_code": 200
            })
            
    print(f"Successfully generated {len(tasks)} mock measurements in '{RAW_DATA_PATH}'")

if __name__ == "__main__":
    generate_data()
