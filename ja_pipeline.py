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
        
        '''
        Extracts data from kedro
        '''
        
        # Create kedro session
        path = os.getcwd()
        bootstrap_project(Path(path))
        session_start = KedroSession.create()

        # Load data
        with session_start:
            key = dataset
            context = session_start.load_context()
            kedro_connector = context.catalog.datasets.__dict__[key]
                        
        df = kedro_connector.load()
        
        return df
    
    
    
    def set_data_extraction_param(
        self, 
        start_date: str,
        end_date: str,
        n_components: int,
        min_cluster_size: int,
        n_neighbors: int,
        XRapidAPIKey: str
    ):
        
        directory = os.getcwd()
        path = directory + "/conf/local/parameters.yml"
        print("this is the path for the yaml file", path)
        with open(path, 'w') as f:
            yaml.dump(
            {
                "start_date": start_date,
                "end_date": end_date,
                "n_components": n_components,
                "min_cluster_size": min_cluster_size,
                "n_neighbors": n_neighbors,
                "XRapidAPIKey": XRapidAPIKey
                
            }, f
            )
        
        

if __name__ == "__main__":
    if os.getenv("MULTIPROCESSING_SPAWN_DISABLE"):
        import multiprocessing
        multiprocessing.set_start_method("forkserver", force=True)
#     #ja_pipeline = JAPipelineRun()
    
    import streamlit as st
    import plotly.express as px
    import yaml
    import pandas as pd
    import numpy as np
    import ja_pipeline
    import ast
    import matplotlib.pyplot as plt
    from datetime import date
    #from ydata_profiling import ProfileReport

    
    # Messaging for model refresh 
    def model_refresh_message():
        analysis_refresh_time = date.today()
        st.write("Analysis last refreshed")
        st.write(analysis_refresh_time)

    
    # Generate topic level summaries
    def topic_analysis(df):
        df = df
        df_summary = df[["topic", "Clap Score", "Generated Topics"]].groupby(["topic", "Generated Topics"]).agg({"Clap Score": "median"}).reset_index()
        df_summary["Clap Score"] = df_summary["Clap Score"].round(decimals=2)
        df_summary.sort_values(by="Clap Score", ascending=False, inplace=True)


        st.title("Medium Article Topic Analysis")
        #@st.cache
        def plot_pie_chart(row):
            topics = ast.literal_eval(row["Generated Topics"])
            fig = px.pie(
                values=[topic[1] for topic in topics],
                names=[topic[0] for topic in topics],
                title=f"Clap Score: {row['Clap Score']}",
                hole=.5
            )
            return fig

        df_plot = df_summary

        for i, row in df_plot.iterrows():
            st.plotly_chart(plot_pie_chart(row))


            
    # set parameters
    
    extract_params = ja_pipeline.JAPipelineRun()
    extract_params.set_data_extraction_param(
        start_date="2023-02-10", 
        end_date="2023-02-10",
        n_components=5,
        min_cluster_size=15,
        n_neighbors=15,
        XRapidAPIKey='XXXXXXXXXXXXXXXX'
    )

    
    # set data extraction dates    
    st.header("Pull data from medium API")
    start_date = st.text_input('Date Pull: Start YYYY-MM-DD', value='2023-02-10')
    end_date = st.text_input('Date Pull: End YYYY-MM-DD', value='2023-02-10')   
    XRapidAPIKey = st.text_input('Enter your Medium API secret key', value='XXXXXXXXXXXXXXXX')
    
    # Initiate data pull from medium API
    if st.button("Pull Data"):

        if start_date == "" or end_date == "" or XRapidAPIKey == 'XXXXXXXXXXXXXXXX' or XRapidAPIKey == "":
            st.text("Please enter some dates or a valid Medium API secret key")

        else:
            
            extract_params = ja_pipeline.JAPipelineRun()
            extract_params.set_data_extraction_param(
                start_date=start_date, 
                end_date=end_date,
                n_components=5,
                min_cluster_size=15,
                n_neighbors=15,
                XRapidAPIKey=XRapidAPIKey
            )
            
            extract_data = ja_pipeline.JAPipelineRun()
            extract_data.end2end_run("data_processing")

            st.text(''' Data extraction complete
                    ''')
      
            

    # set clustering parameters UMAP and HDBSCAN
    st.header("UMAP dimension reduction parameters")
    n_components = st.number_input(label='Number of Components', value=5)
    n_neighbors = st.number_input(label='Nearest Neighbours', value=15)
    
    # Set modeling
    st.header("HDBSCAN parameters")
    min_cluster_size = st.number_input(label='Minimum Cluster Size', value=15)
    
    # initiate model run after data pull
    if st.button("Run model"):

        if n_components <= 0 or min_cluster_size <= 0 or n_neighbors <= 0:
            st.text("Please make sure model parameters are integers >= 0")

        else:
            
            extract_params = ja_pipeline.JAPipelineRun()
            extract_params.set_data_extraction_param(
                start_date=start_date, 
                end_date=end_date,
                n_components=n_components,
                min_cluster_size=min_cluster_size,
                n_neighbors=n_neighbors,
                XRapidAPIKey=XRapidAPIKey
            )
            
            
            feature_eng = ja_pipeline.JAPipelineRun()
            feature_eng.end2end_run("feature_enginering_clustering")

            st.text(''' Feature engineering complete
                    ''')
     
    
        # display chart 
        cluster_chart = ja_pipeline.JAPipelineRun()
        HDSCAN_cluster_data = cluster_chart.get_data("HDSCAN_cluster_data")
        fig = px.scatter(HDSCAN_cluster_data, x='x', y='y', color='topic', color_continuous_scale='Viridis', width=800, height=800)
        st.plotly_chart(fig)
    
    
    
    # Initiate analytics 
    if st.button("Generate Topic Analysis"):

        # runs bayes analysis and saves new data set to data repo in kedro data\07_model_output
        run_bayes_analysis = ja_pipeline.JAPipelineRun()
        run_bayes_analysis.end2end_run("bayesian_analysis_pipeline")

        # Pull data from kedro data storage 
        getdata = ja_pipeline.JAPipelineRun()
        df_final_analysis = getdata.get_data("df_final_analysis")

        # Generates analysis from data 
        topic_analysis(df=df_final_analysis)
            
   