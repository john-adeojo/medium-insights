"""
This is a boilerplate pipeline 'feature_eng_clustering'
generated using Kedro 0.18.4
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import feature_engineering, create_embeddings, reduce_dimensions, cluster_HDBSCAN, visualise_clusters, extract_topics 

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func= feature_engineering,
                inputs= ["analysis_df", 'data_request_date'], 
                outputs="analysis_df2",
                name="feature_engineering"
            ), 
            node(
                func= create_embeddings,
                inputs= "analysis_df2",
                outputs="embeddings",
                name="create_embeddings"
            ), 
            node(
                func= reduce_dimensions,
                inputs= ["embeddings", "parameters"],
                outputs="umap_embeddings",
                name="reduce_dimensions"
            ),
            node(
                func= cluster_HDBSCAN,
                inputs= ["umap_embeddings", "analysis_df2", "parameters"],
                outputs=["cluster", "full_analysis_df"],
                name="cluster_HDBSCAN"
            ), 
            node(
                func= visualise_clusters,
                inputs= ["embeddings", "cluster", "parameters"],
                outputs= "clusters_plot",
                name="visualise_clusters"
            ),
            node(
                func= extract_topics,
                inputs= ["full_analysis_df", "cluster"],
                outputs= "full_analysis",
                name="extract_topics"
            )
        ]
    )
