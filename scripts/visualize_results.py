import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pathlib import Path
import glob
import json
import os

# Configuration
plt.style.use('ggplot')
VIS_DIR = Path("results/visualizations")
VIS_DIR.mkdir(parents=True, exist_ok=True)

COHORTS = [
    "GSE269316", "GSE290333", 
    "GSE307054", "GSE284339",
    "GSE79557",  "GSE215241",
    "GSE312139", "GSE309664",
    "GSE217469", "GSE273501"
]

def plot_benchmarks():
    print("Plotting benchmarks...")
    data = []
    benchmark_dir = Path("results/benchmarks")
    
    for csv_file in benchmark_dir.glob("benchmark_*.csv"):
        acc = csv_file.stem.replace("benchmark_", "")
        if acc not in COHORTS: continue
        
        try:
            df = pd.read_csv(csv_file)
            cpu_t = df[df['device'] == 'cpu']['throughput'].values[0]
            npu_t = df[df['device'] == 'npu']['throughput'].values[0]
            
            data.append({'Cohort': acc, 'Device': 'CPU', 'Throughput': cpu_t})
            data.append({'Cohort': acc, 'Device': 'NPU', 'Throughput': npu_t})
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

    if not data:
        print("No benchmark data found.")
        return

    df_plot = pd.DataFrame(data)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_plot, x='Cohort', y='Throughput', hue='Device', palette='viridis')
    plt.title('Swift Inference Performance: CPU vs NPU')
    plt.ylabel('Samples per Second')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(VIS_DIR / "benchmark_performance.png")
    print(f"Saved {VIS_DIR / 'benchmark_performance.png'}")

def plot_weight_distributions():
    print("Plotting weight distributions...")
    weights_data = {}
    
    for acc in COHORTS:
        path = Path(f"results/{acc}/weights/trained_weights.npy")
        if path.exists():
            w = np.load(path).flatten()
            # Downsample for speed/memory if needed
            if len(w) > 50000:
                w = np.random.choice(w, 50000, replace=False)
            weights_data[acc] = w
            
    if not weights_data:
        print("No weights found.")
        return

    # Create DataFrame for Seaborn
    plot_data = []
    for acc, w in weights_data.items():
        for val in w:
            plot_data.append({'Cohort': acc, 'Weight': val})
            
    df_weights = pd.DataFrame(plot_data)
    
    plt.figure(figsize=(14, 8))
    sns.violinplot(data=df_weights, x='Cohort', y='Weight', palette='magma', inner='quartile')
    plt.title('SNN Weight Distributions (Plasticity Profiles)')
    plt.xticks(rotation=45)
    plt.axhline(0, color='gray', linestyle='--')
    plt.tight_layout()
    plt.savefig(VIS_DIR / "weight_distributions.png")
    print(f"Saved {VIS_DIR / 'weight_distributions.png'}")

def plot_top_grns():
    print("Plotting GRN topology...")
    # Plot grid of 10 GRNs (Top 50 edges)
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    axes = axes.flatten()
    
    for i, acc in enumerate(COHORTS):
        ax = axes[i]
        edge_path = Path(f"results/{acc}/grn/edges.tsv")
        
        if not edge_path.exists():
            ax.text(0.5, 0.5, "No Data", ha='center')
            continue
            
        df = pd.read_csv(edge_path, sep='\t')
        # Top 50 absolute weights
        df['abs_w'] = df['weight'].abs()
        top_edges = df.nlargest(50, 'abs_w')
        
        G = nx.from_pandas_edgelist(top_edges, 'source', 'target', edge_attr='weight')
        pos = nx.spring_layout(G, seed=42)
        
        # Colors
        edges = G.edges(data=True)
        weights = [d['weight'] for u, v, d in edges]
        edge_colors = ['red' if w > 0 else 'blue' for w in weights]
        
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=20, node_color='black')
        nx.draw_networkx_edges(G, pos, ax=ax, width=0.5, edge_color=edge_colors, alpha=0.6)
        
        ax.set_title(acc, fontsize=10)
        ax.axis('off')
        
    plt.suptitle("Top 50 Regulatory Interactions per Cohort", fontsize=16)
    plt.tight_layout()
    plt.savefig(VIS_DIR / "grn_topology.png")
    print(f"Saved {VIS_DIR / 'grn_topology.png'}")

if __name__ == "__main__":
    plot_benchmarks()
    plot_weight_distributions()
    plot_top_grns()
