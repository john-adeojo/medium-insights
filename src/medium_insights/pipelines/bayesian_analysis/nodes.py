"""
This is a boilerplate pipeline 'bayesian_analysis'
generated using Kedro 0.18.4
"""
import pymc as pm
import matplotlib.pyplot as plt
import arviz as az
import pandas as pd
from scipy import special, stats
import numpy as np 
from scipy.stats import mstats

#import warnings
#import seaborn as sn
#from numpy.random import normal
#from datetime import datetime
#import theano
#import seaborn as snscd


def bayesian_inference(full_analysis):
        
    df = full_analysis.loc[full_analysis["topic"] != -1]
                           
    #df = df.sample(frac=0.05, weights='topic', random_state=12)
    
    print(df.shape)
    
    
    df["topic"] = df["topic"].astype("category")

    topic_idx = df.topic.cat.codes.values
    topic_codes = df.topic.cat.categories
    n_topics = topic_codes.size
    
    print("ran", topic_idx, topic_codes, n_topics )


    observed_follower_adjusted_claps_per_day = np.array(df["Follower Adjusted Claps per Day"])
  
    # Define model
    with pm.Model() as model:

        # Priors 
        sigma = pm.HalfNormal("sigma", sigma=10, shape=n_topics)
        mu = pm.Normal("mu", sigma=5, mu=0.004, shape=n_topics)

        clap_rating = pm.LogNormal('clap_rating', mu=mu[topic_idx], sigma=sigma[topic_idx], observed=observed_follower_adjusted_claps_per_day)

    #model_viz = pm.model_to_graphviz(model)    
    
    # Do MCMC sampling 
    print("1. start sampling")

    with model:
        trace = pm.sample(draws=10000, tune=3000, target_accept=0.95, cores=4, idata_kwargs={"log_likelihood": True}, return_inferencedata=False)
        
    with model:
        posterior_predictive  = pm.sample_posterior_predictive(trace=trace, 
                                         return_inferencedata=False)
    with model:
        prior_predictive = pm.sample_prior_predictive(samples=2000, 
                                                     return_inferencedata=False
                                                     )
    # Store inference data
    with model:
        idata = pm.to_inference_data(trace=trace, posterior_predictive=posterior_predictive, prior=prior_predictive, log_likelihood=True)
        
    
    # plot priors
    prior_plot_sigma = az.plot_dist(idata.prior["sigma"]).get_figure() 
    prior_plot_mu = az.plot_dist(idata.prior["mu"]).get_figure()
    
    # Plot Trace: 
    print("2. start trace diagnostics")
    model_diagnostics_trace = az.plot_trace(idata).ravel()[0].figure.get_figure()
    
    # Plot Summary
    print("3. start summary")
    model_diagnostics_summary = az.summary(idata)
    
    # Plot monte carlo squared error
    print("4. start mcse plots")
    model_diagnostics_mcse = az.plot_mcse(idata).ravel()[0].figure.get_figure()
    
    print("5. start ess plot")
    model_diagnostics_ess = az.plot_ess(idata).ravel()[0].figure.get_figure()
    
    print("6. start rank plots")
    model_diagnostics_rank = az.plot_rank(idata).ravel()[0].figure.get_figure()
    
    print("7. posterior predictive checks")
    ppc_plot_loo_pit = az.plot_loo_pit(idata=idata, y='clap_rating').get_figure()
    
    # Prep posterior prediction data
    observations = idata.posterior_predictive["clap_rating"].shape[2]
    posterior_pred = idata.posterior_predictive["clap_rating"].values.reshape(-1, observations).copy()

    # Define article clap metrics

    def expected_claps(posterior_pred, num_followers: int, time_days: int):
        adj_claps = posterior_pred * num_followers * time_days 
        expected_claps = np.median(adj_claps, axis=0)
        return expected_claps


    def hdi_of_columns(posterior_pred,num_followers=500, time_days=7, cred_mass=0.95):
        posterior_pred = posterior_pred * num_followers * time_days
        hdi = np.zeros(posterior_pred.shape[1])
        for i in range(posterior_pred.shape[1]):
            hdi[i] = mstats.mquantiles(posterior_pred[:, i], prob=[(1 - cred_mass) / 2, 1 - (1 - cred_mass) / 2])[1]
        return hdi

    expected_claps = expected_claps(posterior_pred=posterior_pred , num_followers=500, time_days=7)
    expected_claps_df = pd.DataFrame(expected_claps, columns=["Expected Claps"])

    hdi_claps = hdi_of_columns(posterior_pred=posterior_pred, num_followers=500, time_days=7, cred_mass=0.95)
    hdi_claps_df = pd.DataFrame(hdi_claps, columns=["HDI Claps"])

    clap_score = np.divide(expected_claps, hdi_claps)*1000
    clap_score_df = pd.DataFrame(clap_score, columns=["Clap Score"])

    df_final = df.merge(expected_claps_df, how="left", left_index=True, right_index=True)
    df_final = df_final.merge(hdi_claps_df, how="left", left_index=True, right_index=True)
    df_final_analysis = df_final.merge(clap_score_df, how="left", left_index=True, right_index=True)

        
    
    return prior_plot_sigma, prior_plot_mu, model_diagnostics_trace, model_diagnostics_summary, model_diagnostics_mcse, model_diagnostics_ess, model_diagnostics_rank, ppc_plot_loo_pit, df_final_analysis     
    