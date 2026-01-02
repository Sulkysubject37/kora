import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VIS_DIR = Path("results/visualizations")
VIS_DIR.mkdir(parents=True, exist_ok=True)

TARGET_ACC = "GSE269316" # Parkinsons Representative

def generate_interactive_grn(accession):
    logger.info(f"Generating interactive GRN for {accession}...")
    
    edge_path = Path(f"results/{accession}/grn/edges.tsv")
    if not edge_path.exists():
        logger.error("Edge list not found.")
        return

    df = pd.read_csv(edge_path, sep='\t')
    # Filter top 200 edges for performance/readability
    df['abs_w'] = df['weight'].abs()
    top_edges = df.nlargest(200, 'abs_w')
    
    G = nx.from_pandas_edgelist(top_edges, 'source', 'target', edge_attr='weight')
    
    # Layout
    pos = nx.spring_layout(G, dim=3, seed=42)
    
    # Nodes
    Xn = [pos[k][0] for k in G.nodes()]
    Yn = [pos[k][1] for k in G.nodes()]
    Zn = [pos[k][2] for k in G.nodes()]
    
    trace_nodes = go.Scatter3d(
        x=Xn, y=Yn, z=Zn,
        mode='markers+text',
        marker=dict(symbol='circle', size=6, color='black'),
        text=list(G.nodes()),
        hoverinfo='text'
    )
    
    # Edges
    Xe = []
    Ye = []
    Ze = []
    colors = []
    
    for u, v, d in G.edges(data=True):
        Xe += [pos[u][0], pos[v][0], None]
        Ye += [pos[u][1], pos[v][1], None]
        Ze += [pos[u][2], pos[v][2], None]
        colors.append('red' if d['weight'] > 0 else 'blue')
        colors.append('red' if d['weight'] > 0 else 'blue') # Duplicate for line segment?
        colors.append('red') # Placeholder for None
    
    trace_edges = go.Scatter3d(
        x=Xe, y=Ye, z=Ze,
        mode='lines',
        line=dict(color='rgb(125,125,125)', width=1),
        hoverinfo='none'
    )
    
    layout = go.Layout(
        title=f"Interactive GRN: {accession} (Top 200 Interactions)",
        showlegend=False,
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
    )
    
    fig = go.Figure(data=[trace_edges, trace_nodes], layout=layout)
    out_path = VIS_DIR / f"grn_interactive_{accession}.html"
    fig.write_html(str(out_path))
    logger.info(f"Saved {out_path}")

def generate_weight_scan_animation(accession):
    logger.info(f"Generating weight scan animation for {accession}...")
    
    weights_path = Path(f"results/{accession}/weights/trained_weights.npy")
    if not weights_path.exists():
        return
        
    W = np.load(weights_path)
    W_flat = np.abs(W.flatten())
    # Subsample
    if len(W_flat) > 100000:
        W_flat = np.random.choice(W_flat, 100000, replace=False)
        
    fig, ax = plt.subplots(figsize=(8, 6))
    
    def update(frame):
        ax.clear()
        threshold = np.percentile(W_flat, 100 - frame) # Top 0% to Top 50%
        # Show histogram of weights above threshold
        
        # Actually, let's show the Cumulative Distribution Function (CDF) scan
        # Or better: "Network Density vs Threshold"
        
        sns.histplot(W_flat, bins=50, kde=True, ax=ax, color='blue', alpha=0.3)
        ax.axvline(threshold, color='red', linestyle='--', label=f'Threshold (Top {frame}%)')
        ax.set_title(f"Weight Distribution Scan: {accession}")
        ax.set_xlim(0, np.max(W_flat))
        ax.legend()
        
    import seaborn as sns
    ani = animation.FuncAnimation(fig, update, frames=np.linspace(0.1, 50, 50), interval=100)
    
    out_path = VIS_DIR / f"weight_scan_{accession}.gif"
    ani.save(out_path, writer='pillow')
    logger.info(f"Saved {out_path}")

if __name__ == "__main__":
    generate_interactive_grn(TARGET_ACC)
    generate_weight_scan_animation(TARGET_ACC)
