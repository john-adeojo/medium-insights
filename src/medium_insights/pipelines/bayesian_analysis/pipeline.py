"""
This is a boilerplate pipeline 'bayesian_analysis'
generated using Kedro 0.18.4
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import bayesian_inference

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node
            (
                    func=bayesian_inference,
                    inputs= "full_analysis",
                    outputs=[
                        "prior_plot_sigma", 
                        "prior_plot_mu", 
                        "model_diagnostics_trace", 
                        "model_diagnostics_summary", 
                        "model_diagnostics_mcse", 
                        "model_diagnostics_ess", 
                        "model_diagnostics_rank", 
                        "ppc_plot_loo_pit", 
                        "df_final_analysis"
                    ],
                    name="bayesian_inference"
            )
        ]
    )
