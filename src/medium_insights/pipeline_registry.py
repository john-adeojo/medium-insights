"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline
from medium_insights.pipelines import data_processing as dp
from medium_insights.pipelines import feature_eng_clustering as fe
from medium_insights.pipelines import bayesian_analysis as ba



def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    data_processing_pipeline = dp.create_pipeline()
    feature_eng_clustering_pipeline = fe.create_pipeline()
    bayesian_analysis_pipeline = ba.create_pipeline()

    return {
        "__default__": data_processing_pipeline + feature_eng_clustering_pipeline + bayesian_analysis_pipeline,
        "run_model_end_to_end": data_processing_pipeline + feature_eng_clustering_pipeline + bayesian_analysis_pipeline, 
        "data_processing": data_processing_pipeline,
        "feature_enginering_clustering": feature_eng_clustering_pipeline,
        "bayesian_analysis_pipeline": bayesian_analysis_pipeline
    }