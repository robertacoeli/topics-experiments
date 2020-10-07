''' 
    This script generates the topic similarity graph and calculates the similarity between the BTM topics using the Jaccard and WDM coefficients. The similarity is calculated between each pair of months in the studied period.

    input: folder containing BTM top words for each month in the studied period. The folder of *each month* must contain the file "final_btm_model.twords" (example of the format of this file in https://drive.google.com/file/d/15F0G8bKNFQMBDYa2F7mAx8XDZc3fXypq/view?usp=sharing)

    output: text file containing the similarity between the topics. Example of output file: "general_measures.txt" in the Google Drive Folder (https://drive.google.com/drive/folders/17HGKIUlRcRMq3BuHtazAllTiaohBozg9?usp=sharing)
'''
# external modules
import argparse
import os
import numpy as np
import time
import itertools
from collections import Counter
import pickle
# import plotly
# import plotly.graph_objs as gobjs
import time
import networkx as nx

# internal modules
import writing_all_topics as wat

# global variables (change according to the studied dataset)
years = [2015, 2016] # years of the dataset
months = list(range(1,13)) # months in the range [1,12], i.e., it goes from january of 2015 and december of 2016

# initialize the graph, creating a node for each topic in the dataset
def init_graph(num_topics):
    graph = nx.Graph() 
    print("Initializing graph nodes ... ", end="")
    start = time.time()
    for year in years:
        for month in months:
            node_root_name = str(year) + "_" + ("%02d" % month)
            for t in range(1, num_topics + 1):
                graph.add_node(node_root_name + "_topic_" + ("%02d" % t))
    end = time.time()
    print("Elapsed time: " + str(end - start))
    start = end

    return graph

# calculates the similarity between each pair of topics of each month in the input folder 
# parameters:
# num_topics -> number of topics in each file (k = 10, if there are 10 topics that are calculated for each month of the studied period)
# infolder -> input folder (contains subfolders of the topics of each month, i.e, a file final_btm_model.twords for each month)
# outfolder -> name of the folder that will contain all the output files
def calculate_all_to_all_similarity(num_topics, infolder, outfolder):
    output_file = open(os.path.join(infolder, "general_measures.txt"), "w",
                            encoding="utf-8")
    output_file.write("Month1;Month2;WO Similarity;WO New Topics;WO Number of New Topics;Jaccard Similarity;Jaccard New Topics;Jaccard Number of New Topics\n")

    period = []
    wo_measure = []
    wo_tout = []
    jc_measure = []
    jc_tout = []

    graph = init_graph(num_topics)

    # calculations
    for year1 in years:
        for month1 in months:
            for year2 in range(year1)


### MAIN
if __name__ == "__main__":
    infolder = "/home/robertacoeli/Documents/Mestrado/resultados/topicos"
    num_topics = 10
    outfolder = "/home/robertacoeli/Documents/Mestrado/resultados/agregacao_topicos"

    calculate_all_to_all_similarity()