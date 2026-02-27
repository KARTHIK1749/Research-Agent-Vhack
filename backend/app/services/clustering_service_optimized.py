"""
Optimized Clustering Service for Analytical Gap Engine - MARIS v2
Uses faster algorithms and optimized parameters for better performance.
"""
from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import pairwise_distances_argmin_min
import time

def cluster_embeddings_optimized(embeddings: List[List[float]], n_clusters: int = 5) -> Dict[str, Any]:
    """
    Perform optimized KMeans clustering on paper embeddings.
    
    Args:
        embeddings: List of embedding vectors
        n_clusters: Number of clusters to create (default: 5)
    
    Returns:
        Dictionary with cluster analysis results
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
    
    print(f"📈 Clustering Service: Processing {len(embeddings)} embeddings into {n_clusters} clusters...")
    start_time = time.time()
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    n_papers = len(embeddings_array)
    
    # Use MiniBatchKMeans for faster clustering on larger datasets
    if n_papers > 100:
        print("🔄 Clustering Service: Using MiniBatchKMeans for large dataset")
        kmeans = MiniBatchKMeans(
            n_clusters=min(n_clusters, n_papers), 
            random_state=42, 
            batch_size=32,
            max_iter=100,
            init='k-means++'
        )
    else:
        print("🔄 Clustering Service: Using standard KMeans")
        kmeans = MiniBatchKMeans(
            n_clusters=min(n_clusters, n_papers), 
            random_state=42,
            max_iter=100,
            init='k-means++'
        )
    
    labels = kmeans.fit_predict(embeddings_array)
    centroids = kmeans.cluster_centers_
    
    # Calculate cluster density efficiently
    unique_labels, counts = np.unique(labels, return_counts=True)
    density = {}
    for label, count in zip(unique_labels, counts):
        density[int(label)] = int(count)
    
    # Find sparsest cluster
    sparsest_cluster = None
    if density:
        sparsest_cluster = min(density.keys(), key=lambda k: density[k])
    
    # Calculate average distance to centroid for each cluster (quality metric)
    cluster_quality = {}
    for cluster_id in unique_labels:
        cluster_mask = labels == cluster_id
        cluster_embeddings = embeddings_array[cluster_mask]
        if len(cluster_embeddings) > 1:
            centroid = centroids[cluster_id]
            distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
            cluster_quality[int(cluster_id)] = float(np.mean(distances))
        else:
            cluster_quality[int(cluster_id)] = 0.0
    
    clustering_time = time.time() - start_time
    print(f"✅ Clustering Service: Completed in {clustering_time:.2f}s")
    print(f"📊 Clustering Service: Sparsest cluster: {sparsest_cluster} (density: {density.get(sparsest_cluster, 0)})")
    
    return {
        "labels": labels.tolist(),
        "centroids": centroids.tolist(),
        "density": density,
        "sparsest_cluster": sparsest_cluster,
        "cluster_quality": cluster_quality,
        "n_clusters": len(unique_labels),
        "total_papers": n_papers,
        "processing_time": clustering_time
    }

def cluster_embeddings(embeddings: List[List[float]], n_clusters: int = 5) -> Dict[str, Any]:
    """
    Backward compatibility wrapper.
    """
    result = cluster_embeddings_optimized(embeddings, n_clusters)
    # Remove new fields to maintain compatibility
    result.pop("cluster_quality", None)
    result.pop("processing_time", None)
    return result

def get_sparsest_cluster_papers(
    papers: List[Dict[str, Any]], 
    labels: List[int], 
    sparsest_cluster: int
) -> List[Dict[str, Any]]:
    """
    Get papers from the sparsest cluster with optimized filtering.
    
    Args:
        papers: List of paper dictionaries
        labels: Cluster labels for each paper
        sparsest_cluster: ID of the sparsest cluster
        
    Returns:
        List of papers from the sparsest cluster
    """
    if sparsest_cluster is None or not papers or not labels:
        return []
    
    # Use numpy for faster filtering
    labels_array = np.array(labels)
    sparsest_mask = labels_array == sparsest_cluster
    sparsest_indices = np.where(sparsest_mask)[0]
    
    # Get papers from sparsest cluster
    sparsest_papers = []
    for idx in sparsest_indices:
        if idx < len(papers):
            sparsest_papers.append(papers[idx])
    
    print(f"🎯 Clustering Service: Found {len(sparsest_papers)} papers in sparsest cluster {sparsest_cluster}")
    return sparsest_papers

def analyze_cluster_distribution(cluster_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the distribution of clusters for insights.
    
    Args:
        cluster_analysis: Output from cluster_embeddings
        
    Returns:
        Analysis of cluster distribution
    """
    density = cluster_analysis.get("density", {})
    total_papers = cluster_analysis.get("total_papers", 0)
    
    if not density or total_papers == 0:
        return {"analysis": "No clusters to analyze"}
    
    # Calculate statistics
    cluster_counts = list(density.values())
    avg_density = np.mean(cluster_counts)
    std_density = np.std(cluster_counts)
    
    # Find most and least dense clusters
    most_dense_cluster = max(density.keys(), key=lambda k: density[k])
    least_dense_cluster = min(density.keys(), key=lambda k: density[k])
    
    analysis = {
        "total_clusters": len(density),
        "total_papers": total_papers,
        "average_density": float(avg_density),
        "density_std": float(std_density),
        "most_dense_cluster": {
            "cluster_id": most_dense_cluster,
            "paper_count": density[most_dense_cluster],
            "percentage": (density[most_dense_cluster] / total_papers) * 100
        },
        "least_dense_cluster": {
            "cluster_id": least_dense_cluster,
            "paper_count": density[least_dense_cluster],
            "percentage": (density[least_dense_cluster] / total_papers) * 100
        },
        "distribution_balance": "balanced" if std_density < avg_density * 0.3 else "unbalanced"
    }
    
    return analysis
