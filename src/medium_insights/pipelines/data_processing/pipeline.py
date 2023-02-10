"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.4
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import request_data


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func= request_data,
                inputs= "requested_date_range",
                outputs=["analysis_df", "article_content", "data_request_date"],
                name="request_data_node"
            )
        ]
    )
