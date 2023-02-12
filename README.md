# medium insights

## Project Overview 

Discover the most popular topics on the popular medium blog towards data science. The project leverages topic modelling to discover topics from the titles of articles and Bayesian analysis to estimate a "clap score" which is a measure of popularity fo those topics.

The project gives the user the ability to pull articles from medium over a specified time interval, set clustering parameters and generate the analysis through an interactive dashboard.

The aim is to help data scientists, technical writers and bloggers to find popular, trending topics to write about on medium.

## Pre-requisites

Follow the instructions carefully to set up your anaconda environment and install the relevant library. 

### Medium API key

You will need to have a medium API, you can grab one from [rapid API](https://rapidapi.com/nishujain199719-vgIfuFHZxVZ/api/medium2/).

### Installation

#### Instal Anaconda
You will need to have [anaconda](https://www.anaconda.com/) installed on your machine to get started.

#### Create a Conda environment (including pymc and python 3.8)
Once you have installed anaconda, open the anaconda powershell and enter the following command;

'''
conda create -c conda-forge -n <your_environment_name> "pymc>=4" "python=3.8"
'''

activate you python environment by entering the command;

'''
conda activate <your_environment_name>
'''

#### Installing Jax 
You should install Jax for faster sampling and inference. Grab the [jax wheel](https://whls.blob.core.windows.net/unstable/cpu/jaxlib-0.3.2-cp38-none-win_amd64.whl) file and save it in the root folder of your created environment.

run the following command;

'''
pip install jax[cpu]
'''

#### Install kedro 
Kedro is used to manage the ML pipeline behind the analysis.
Install kedro by entering the following command:

'''
pip install kedro
'''

Important! the kedro bersion this project is built on is Kedro 0.18.4

#### Clone github repo 
change the directory to the newly created conda environment with:

cd ..\anaconda3\envs\<your_encironment_name> 
note your filepath could be slightly different depending on your anaconda set up. 

clone the github repo to the environment with;

'''
git clone https://github.com/john-adeojo/medium-insights
'''

#### Installing python packages
change the directory to medium-insights with;

''' 
cd medium-insights
'''

run the following to install the required python libraries.

''' 
pip install -r src/requirements.txt
'''

#### Open the streamlit dashboard 
Once you are all set up, you can open the UI by entering the following command. Be sure you are in the medium-insights folder before running. 

'''
streamlit run ja_pipeline.py
'''

#### Open the ML pipeline view
Making sure that your conda environment is activated, navigate to medium-insights within your anaconda powershell instance. 

run the command 

'''
kedro viz
'''

The project is built on kedro, if you want to learn more about kedro please read the kedro documentation. 

Take a look at the [Kedro documentation](https://kedro.readthedocs.io) to get started.



