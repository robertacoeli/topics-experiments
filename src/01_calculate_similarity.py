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
import time
import networkx as nx

# internal modules
import similarity_calculations as sc

# global variables (change according to the studied dataset)
# if the period does not cover entire years, you must change the iteration functionality for the variables "years" and "months"
years = [2015, 2016] # years of the dataset
months = list(range(1,13)) # months in the range [1,12], i.e., it goes from january of 2015 to december of 2016
input_filename = "final_btm_model.twords"

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

# add edge between topics to the graph
def add_to_graph(graph, topic_matrix, p1, p2):
    for i in range(0, topic_matrix.shape[0]):
        for j in range(0, topic_matrix.shape[1]):
            graph.add_edge(p1 + "_topic_" + ("%02d" % (i + 1)),
                            p2 + "_topic_" + ("%02d" % (j + 1)),
                            weight=topic_matrix[i][j])
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
            for year2 in range(year1, max(years) + 1):
                for month2 in range(month1 if year2 == year1 else 1, max(months) + 1):
                    # format prefixes that indicate the month
                    p1 = str(year1) + "_" + ("%02d" % month1)
                    p2 = str(year2) + "_" + ("%02d" % (month2))

                    # obtain the topics from the final_btm_model.twords file.
                    # these files are under the subfolders inside the input folder (infolder -> parameter as the function)
                    # in our case, the subfolders were formatted as "deputados_<year_number>_<month_number>"
                    print("Comparing " + p1 + " AND " + p2)
                    with open(os.path.join(infolder, "deputados_" + str(year1) + "_" + ("%02d" % month1), input_filename), "r") as f1:
                        topics1 = [line.strip() for line in f1]

                    with open(os.path.join(infolder, "deputados_" + str(year2) + "_" + ("%02d" % month2), input_filename), "r") as f2:
                        topics2 = [line.strip() for line in f2]

                    # calculate word overlap measure
                    (wo_sim, wo_topics_out, wo_tpm) = sc.calculate_word_overlap_similarity(topics1, topics2, num_topics)

                    # calculate jaccard coefficient
                    (jc_sim, jc_topics_out, jc_tpm) = sc.calculate_jaccard_similarity(topics1, topics2, num_topics)

                    # appending values to arrays
                    period.append(p1 + " - " + p2)
                    wo_measure.append(wo_sim)
                    wo_tout.append(len(wo_topics_out))
                    jc_measure.append(jc_sim)
                    jc_tout.append(len(jc_topics_out))

                    # write matrices to files
                    wo_tpm_file = open(os.path.join(outfolder, "wo_topic_pairs_matrix_" + p1 + "_" + p2), "wb")
                    pickle.dump(wo_tpm, wo_tpm_file)
                    wo_tpm_file.close()
                    jc_tpm_file = open(os.path.join(outfolder, "jaccard_topic_pairs_matrix_" + p1 + "_" + p2), "wb")
                    pickle.dump(jc_tpm, jc_tpm_file)
                    jc_tpm_file.close()
                    output_file.write(p1 + ";" + p2 + ";" + str(wo_sim) + ";" + str(wo_topics_out) + ";" +
                                        str(len(wo_topics_out)) + ";" + str(jc_sim) + ";" +
                                        str(jc_topics_out) + ";" + str(len(jc_topics_out)) + "\n")
                    end = time.time()
                    print("Elapsed time: " + str(end - start))
                    start = end

                    # adding edges between topics to the similarity graph
                    print("Adding new edges to graph ... ", end="")
                    graph = add_to_graph(graph, jc_tpm, p1, p2)
                    end = time.time()
                    print("Elapsed time: " + str(end - start))
                    start = end

### MAIN
if __name__ == "__main__":
    infolder = "/home/robertacoeli/Documents/Mestrado/resultados/topicos"
    num_topics = 10
    outfolder = "/home/robertacoeli/Documents/Mestrado/resultados/agregacao_topicos"

    calculate_all_to_all_similarity(num_topics, infolder, outfolder)