"""
Clustering Service for Analytical Gap Engine - MARIS v2
Performs KMeans clustering on paper embeddings to identify sparse research areas.
"""
from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances


def cluster_embeddings(embeddings: List[List[float]], n_clusters: int = 5) -> Dict[str, Any]:
    """
    Perform KMeans clustering on paper embeddings.
    
    Args:
        embeddings: List of embedding vectors
        n_clusters: Number of clusters to create (default: 5)
    
    Returns:
        Dictionary with cluster analysis results:
        {
            "labels": [...],
            "centroids": [...],
            "density": {cluster_id: count},
            "sparsest_cluster": cluster_id,
            "n_clusters": n_clusters,
            "total_papers": len(embeddings)
        }
    """
    if not embeddings:
        return {
            "labels": [],
            "centroids": [],
            "density": {},
            "sparsest_cluster": None,
            "n_clusters": 0,
            "total_papers": 0
        }
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings_array)
    centroids = kmeans.cluster_centers_
    
    # Calculate cluster density
    density = {}
    for i in range(n_clusters):
        cluster_count = np.sum(labels == i)
        density[i] = int(cluster_count)
    
    # Identify sparsest cluster
    sparsest_cluster = min(density.keys(), key=lambda x: density[x]) if density else None
    
    return {
        "labels": labels.tolist(),
        "centroids": centroids.tolist(),
        "density": density,
        "sparsest_cluster": sparsest_cluster,
        "n_clusters": n_clusters,
        "total_papers": len(embeddings)
    }


def get_sparsest_cluster_papers(papers: List[Dict], labels: List[int], sparsest_cluster: int) -> List[Dict]:
    """
    Get papers belonging to the sparsest cluster.
    
    Args:
        papers: List of paper dictionaries
        labels: Cluster labels for each paper
        sparsest_cluster: ID of the sparsest cluster
    
    Returns:
        List of papers in the sparsest cluster
    """
    if sparsest_cluster is None:
        return []
    
    sparsest_papers = []
    for i, paper in enumerate(papers):
        if i < len(labels) and labels[i] == sparsest_cluster:
            sparsest_papers.append(paper)
    
    return sparsest_papers


def compute_cluster_sparsity_score(density: Dict[int, int], total_papers: int) -> float:
    """
    Compute sparsity score for the cluster distribution.
    Lower values indicate more uneven distribution (good for gap finding).
    
    Args:
        density: Dictionary of cluster_id -> count
        total_papers: Total number of papers
    
    Returns:
        Sparsity score (0-1, lower is sparser)
    """
    if not density or total_papers == 0:
        return 1.0
    
    # Calculate coefficient of variation for cluster sizes
    cluster_sizes = list(density.values())
    if len(cluster_sizes) <= 1:
        return 0.0
    
    mean_size = np.mean(cluster_sizes)
    std_size = np.std(cluster_sizes)
    
    # Coefficient of variation normalized to 0-1
    cv = std_size / mean_size if mean_size > 0 else 0
    return min(cv / 2.0, 1.0)  # Normalize to roughly 0-1 range
