# BEACO2N-CO2-Correction

Group member info:

Qindan Zhu 3033020499

Hannah DeVyldere 

# What's included

This repository contains codes to preprocess the CO2 measurements from BEACO2N sensor network and reference site, emission and footprint data and three jupyter notebooks to conduct feature engineering, multi linear regression model and neutral network.

# How to set it up

The development of these codes are performed using Python version 3.8. The required packages are listed in requirement.txt. Setting up a virtual environment is highly recommended. You can either set it up using conda or virtualenv.

The full datasets can be downloaded from https://berkeley.box.com/s/1t5aabwofk9ab20g5ijcky6mq95l9t5b. Given the large data size, the finalized datasets for machine learning model is under https://berkeley.box.com/s/k424ap689z75h2azmewsyg0oj92mluwg.

# Overview of the codes

co2correction packages are intended to process all data collected from observations, existing emissions inventories and footprint model simulations.

collection-observations.py handles all steps including: 

1) collect data from BEACO2N network in csv files and match each observations to emission and footprints (both in ncdf files).

2) read in emission and footprints and trim the map covering the study region.

3) match each observations to corresponding co2 measurements from reference site.

collection-observations-on-cluster.py is a copy version of collection-observations.py and is adapted to run on the berkeley savio supercluster.

collect-emission-footprints.py and utils.py include utility functions.


EECS189_proj_data_separate_feature_engineering.ipynb reads in datasets prepared by co2correction package, make features that are needed for our model, normalize them, and conduct a train test split on our datasets. 

EECS189_proj_linear_regression.ipynb runs a ridge linear regression model and analyzes the model outputs.

EECS189_proj_nn.ipynb runs a neural network model.

