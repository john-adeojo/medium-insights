"""
This is a boilerplate pipeline 'feature_eng_clustering'
generated using Kedro 0.18.4
"""

import pandas as pd
#from ydata_profiling import ProfileReport
import numpy as np
import plotly.express as px
from sentence_transformers import SentenceTransformer
import umap.umap_ as umap
import hdbscan
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer


def feature_engineering(analysis_df, data_request_date):
    
    data_request_date = data_request_date.at[0, 'data_request_date']
  
    print("Data request date", data_request_date)
    
    
    analysis_df = analysis_df.loc[analysis_df.claps > 0]
    analysis_df['last_modified_at'] = pd.to_datetime(analysis_df['last_modified_at'], format='%Y-%m-%d %H:%M:%S')
    analysis_df['published_at'] = pd.to_datetime(analysis_df['published_at'], format='%Y-%m-%d %H:%M:%S')
    analysis_df['Data Pull Date'] = pd.to_datetime(data_request_date)
    analysis_df['No. of Days Published'] = (analysis_df['Data Pull Date'] - analysis_df['published_at']).dt.days + 2  # hack to remove 0 and -1 days.
    analysis_df['Follower Adjusted Claps per Day'] = analysis_df["Follower Adjusted Claps"] /  analysis_df["No. of Days Published"]

    # Adjusted claps are normalised to 1 week and 500 followers. The number of followers I have at the time of coding.
    analysis_df['Adjusted Claps'] = analysis_df['Follower Adjusted Claps per Day'] * 7 * 500

    analysis_df["log Follower Adjusted Claps"] = np.log(analysis_df["Follower Adjusted Claps"])
    analysis_df["log Follower Claps"] = np.log(analysis_df["claps"])
    analysis_df["log Follower Adjusted Claps per Day"] = np.log(analysis_df["Follower Adjusted Claps per Day"])
    analysis_df["log Adjusted Claps"] = np.log(analysis_df["Adjusted Claps"])
    analysis_df2 = analysis_df
    
    return analysis_df2

def create_embeddings (analysis_df2):
    from sentence_transformers import SentenceTransformer
    
    
    
    titles_df = list(analysis_df2.title)
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    embeddings = model.encode(titles_df, show_progress_bar=True)
    return embeddings 

def reduce_dimensions(embeddings, parameters: dict): 

    def generate_integer_list(n):
        return list(range(1, n+1))

    n_components = parameters["n_components"]
    n_neighbors = parameters["n_neighbors"]
    min_cluster_size = parameters["min_cluster_size"]

    umap_embeddings = umap.UMAP(n_neighbors=n_neighbors, 
                                n_components=n_components, 
                                random_state = 12,
                                transform_seed = 12,
                                metric='cosine').fit_transform(embeddings)

    components_list = generate_integer_list(n_components)
    umap_embeddings_df = pd.DataFrame(umap_embeddings, columns=components_list)
    
    return umap_embeddings
    
    
def cluster_HDBSCAN(umap_embeddings, analysis_df2, parameters: dict):
    
    min_cluster_size = parameters["min_cluster_size"]
    
    cluster = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size,
                          metric='euclidean',                      
                          cluster_selection_method='eom').fit(umap_embeddings)
    # bring in clusters
    analysis_df2["topic"] = cluster.labels_
    
    full_analysis_df = analysis_df2
    #full_analysis_df = analysis_df2.merge(umap_embeddings_df, how="left", right_index=True, left_index=True)

    return cluster, full_analysis_df


# node to visualise clusters
def visualise_clusters(embeddings, cluster, parameters: dict):
    
    n_neighbors = parameters["n_neighbors"]
    
    
    # Cluster into the 2D space for plotting using embeddings.
    umap_data = umap.UMAP(n_neighbors=n_neighbors, 
                          n_components=2, 
                          min_dist=0.0, 
                          random_state = 12,
                          transform_seed = 12,
                          metric='cosine').fit_transform(embeddings)

    # Assign UMAP dimensions to data frame 
    HDSCAN_cluster_data = pd.DataFrame(umap_data, columns=['x', 'y'])
    HDSCAN_cluster_data['topic'] = cluster.labels_

    # Visualise 2D clusters
    fig = px.scatter(HDSCAN_cluster_data, x='x', y='y', color='topic', color_continuous_scale='Viridis', width=800, height=800)
    
    return fig, HDSCAN_cluster_data
    
    

def extract_topics(full_analysis_df, cluster): 
    
    data = full_analysis_df.title.values.astype(str)
    docs_df = pd.DataFrame(data, columns=["Doc"])
    docs_df['topic'] = cluster.labels_
    docs_df['Doc_ID'] = range(len(docs_df))
    docs_per_topic = docs_df.groupby(['topic'], as_index = False).agg({'Doc': ' '.join})
    
    # function for tf_idf
    
    def c_tf_idf(documents, m, ngram_range=(1, 1)):
        count = CountVectorizer(ngram_range=ngram_range, stop_words="english").fit(documents)
        t = count.transform(documents).toarray()
        w = t.sum(axis=1)
        tf = np.divide(t.T, w)
        sum_t = t.sum(axis=0)
        idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
        tf_idf = np.multiply(tf, idf)

        return tf_idf, count

    tf_idf, count = c_tf_idf(docs_per_topic.Doc.values, m=len(data))
    
    def extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=20):
        words = count.get_feature_names_out()
        labels = list(docs_per_topic.topic)
        tf_idf_transposed = tf_idf.T
        indices = tf_idf_transposed.argsort()[:, -n:]
        top_n_words = {label: [(words[j], tf_idf_transposed[i][j]) for j in indices[i]][::-1] for i, label in enumerate(labels)}
        return top_n_words

    def extract_topic_sizes(df):
        topic_sizes = (df.groupby(['topic'])
                         .Doc
                         .count()
                         .reset_index()
                         .rename({"topic": "topic", "Doc": "Size"}, axis='columns')
                         .sort_values("Size", ascending=False))
        return topic_sizes

    top_n_words = extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=5)
    topic_sizes = extract_topic_sizes(docs_df); topic_sizes.head(10)
    
    full_analysis_df["Generated Topics"] = full_analysis_df["topic"].map(top_n_words)
    
    full_analysis = full_analysis_df
        
    return full_analysis

