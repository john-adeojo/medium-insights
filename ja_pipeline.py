import os
from pathlib import Path
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from kedro.framework.session import session
import ast
import yaml


class JAPipelineRun:
    """
    Runs slices of modeling pipeline
    """

    def __init__(self):
        """
        The constructor method that initializes the object's attributes.
        """

    def end2end_run(self, pipeline: str):
        """
        Runs end to end pipeline.
        """
        path = os.getcwd()
        bootstrap_project(Path(path))
        session_start = KedroSession.create()
    
        with session_start:
            session_start.run(pipeline_name=pipeline)
            
    
            
    def get_data(self, dataset: str):
        
        # Create kedro session
        path = os.getcwd()
        bootstrap_project(Path(path))
        session_start = KedroSession.create()

        # Load final analysis data
        with session_start:
            key = dataset
            context = session_start.load_context()
            kedro_connector = context.catalog.datasets.__dict__[key]
            
        df = kedro_connector.load()
        
        return df

if __name__ == "__main__":
    if os.getenv("MULTIPROCESSING_SPAWN_DISABLE"):
        import multiprocessing
        multiprocessing.set_start_method("forkserver", force=True)
    #ja_pipeline = JAPipelineRun()
    
    import streamlit as st
    import plotly.express as px
    import yaml
    import pandas as pd
    import numpy as np
    import ja_pipeline
    import ast

    # initialise model run with button
    if st.button("Run Model"):
        runmodel = ja_pipeline.JAPipelineRun()
        runmodel.end2end_run("run_model_end_to_end")


    # Generate topic level summaries
    def topic_analysis(df):
        df = df
        df_summary = df[["topic", "Clap Score", "Generated Topics"]].groupby(["topic", "Generated Topics"]).agg({"Clap Score": "median"}).reset_index()
        df_summary["Clap Score"] = df_summary["Clap Score"].round()


        st.title("Medium Article Topic Analysis")
        #@st.cache
        def plot_pie_chart(row):
            topics = ast.literal_eval(row["Generated Topics"])
            fig = px.pie(
                values=[topic[1] for topic in topics],
                names=[topic[0] for topic in topics],
                title=f"Clap Score: {row['Clap Score']}"
            )
            return fig

        df_plot = df_summary

        for i, row in df_plot.iterrows():
            st.plotly_chart(plot_pie_chart(row))

    # Run topic analysis
    getdata = ja_pipeline.JAPipelineRun()
    df_final_analysis = getdata.get_data("df_final_analysis")
    topic_analysis(df=df_final_analysis)


