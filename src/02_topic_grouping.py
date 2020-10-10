''' 
    This script groups the topics according to the similarity values.

    inputs: 
    1) folder containing BTM top words for each month in the studied period. The folder of *each month* must contain the file "final_btm_model.twords" (example of the format of this file in https://drive.google.com/file/d/15F0G8bKNFQMBDYa2F7mAx8XDZc3fXypq/view?usp=sharing)
    2) name of the topic similarity graph file
    3) threshold for the weight of the edges of the similarity graph: this threshold defines the mininum weight that will be considered to indicate that the grouped topics are similar, i.e., edges that have a weight < threshold will be removed (meaning that the pair of grouped topics are not similar)

    output: output folder "similar_topics_criteria_<threshold>_threshold", which has the following files:
    1) "table.csv": this file has the "super" topic number and the months when it appears (marked by an X) 
    2) "table_words.txt": this file has the "super topic", its words and its subset of original topics 
    --> An example of this output folder and its files are in the Google Drive folder (https://drive.google.com/drive/folders/17HGKIUlRcRMq3BuHtazAllTiaohBozg9?usp=sharing)
'''
import os
import argparse
import time
import networkx as nx
import numpy as np
import sys
from sklearn.base import BaseEstimator, RegressorMixin

# global variables 
current_time = time.strftime("%Y%m%d_%H%M%S")

# the variables below might changed according to the studied dataset
# if the period does not cover entire years, you must change the iteration functionality for the variables "years" and "months"
years = [2015, 2016] # years of the dataset
months = list(range(1,13)) # months in the range [1,12], i.e., it goes from january of 2015 to december of 2016
input_filename = "final_btm_model.twords" # topic words file name
prefix_output_subfolder = "similar_topics_criteria_{0}_threshold" # name of the output folder

# period columns of the output file (each year/month is a column in the "table.csv" output file)
period_column = ""
for y in years:
    for m in months:
        period_column += ("%02d" % m) + "/" + str(y) + ";"

# CLASS FOR THE CALCULATIONS
class TopicsGrouping(BaseEstimator, RegressorMixin):

    # init function
    def __init__(self, inputfolder, graph_filename, num_topics):
        self.fname = inputfolder
        self.num_topics = int(num_topics)

        # Load the topics to a dict
        print("Loading topics... ", end="")
        self.topics_dict = self.load_topics()
        print("OK")

        # Load the topic similarity graph
        print("Loading graph... ", end="")
        self.graph = nx.read_gml(graph_filename)
        print("OK")

    # load topics for each month into a dict
    # each entry in the dict has the following key-value:
    # <period_identifier>_topic_<topic_number> -> [array of topic words]
    # example: 2015_01_topic_01 -> ["dinheiro", "corrupcao", "cpi", "milhoes", "brasil"]
    def load_topics(self):
        topics_dict = dict()

        for year in years:
            for month in months:
                period_identifier = str(year) + "_" + ("%02d" % month)

                # finds the whole path to the topics file (final_btm_model.twords for each month)
                # in our case, the file path to the file is structured as "<input_folder>/deputados_<year>_<month>/final_btm_model.twords"
                cfile = open(os.path.join(self.fname, "deputados_" + period_identifier, input_filename), "r")

                tnumber = 1
                for line in cfile:
                    indexer = period_identifier + "_topic_" + ("%02d" % tnumber) # key
                    topics_dict[indexer] = line.strip().split() # links the key to the value (array of words)
                    tnumber += 1
                cfile.close()

        return topics_dict

    # remove edges which weight is zero
    def remove_zero_weights(self):
        for (n1, n2, data) in self.graph.edges(data=True):
            if data['weight'] <= 0.0:
                self.graph.remove_edge(n1,n2)

    # remove edges which weight is below a threshold
    def remove_below_threshold(self, threshold):
        for (n1, n2, data) in self.graph.edges(data=True):
            if data['weight'] < threshold:
                self.graph.remove_edge(n1, n2)

    # sort each of the components of the graph in alphabetical order
    def sorting_ccomponents(self, ccomponents):
        new_ccomponents = []
        for item in ccomponents:
            new_ccomponents.append(" ".join(sorted([(i.split("_")[0] + "_" + i.split("_")[1]) for i in item])))
        alphab_order = np.argsort(new_ccomponents)
        return np.array([sorted(c) for c in ccomponents])[alphab_order]

    # get the set of distinct words within a graph component
    def find_component_words(self, item_component):
        words_set = set()
        for c in item_component:
            words_set.update(self.topics_dict[c])
        return words_set

    # find the column position to place the marker for the period of the topic occurrence in the output file
    def find_marker_position(self, topic_identifier):
        tid = topic_identifier.strip().split("_")
        if int(tid[0]) == min(years):
            return int(tid[1]) - 1
        else:
            return int(tid[1]) + 12 - 1

    # write results to csv file
    def write_to_csv(self, ccomponents, threshold):

        # creates the subfolder similar_topics_criteria_{0}_threshold
        filepath = os.path.join(self.fname, prefix_output_subfolder.format(threshold))
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        csvfile = open(os.path.join(filepath, "table.csv"), "w")
        wordsfile = open(os.path.join(filepath, "table_words.txt"), "w")

        # header of the csv file
        csvfile.write("Topic Number;" + period_column + "Size of Subset of Topics\n")

        # write to files
        topic_number = 1
        for array_component in ccomponents:
            words_set = set()
            period_list = [' ' for _ in range(0,24)]
            for c in array_component:
                position = self.find_marker_position(c)
                period_list[position] = 'X' # marks the period of topic occurrence with an 'X'
                words_set.update(self.topics_dict[c]) # set of words for the topic
            
            csvfile.write(("%03d" % topic_number) + ";" + (";".join(period_list)) + ";" + str(len(array_component)) + "\n")
            wordsfile.write("\n\n-------- TOPIC " + ("%03d" % topic_number) + " --------\n")
            wordsfile.write("Words: ")
            wordsfile.write(", ".join(words_set) + "\n")
            wordsfile.write("Subset of topics: ")
            wordsfile.write((", ".join(array_component)) + "\n")
            topic_number += 1

        # close files
        csvfile.close()
        wordsfile.close()

    # get the file containing the topics that were grouped according to the threshold
    def run(self, threshold):
        print("Analysing graph and getting topics spreadsheet...")

        # Remove weights that have no mean
        start = time.time()
        print("Removing edges which weight is zero... ", end="")
        self.remove_zero_weights()
        end = time.time()
        print("Elapsed time: %f seconds" % (end - start))

        # find the connected components of the graph after the removal of zero-weight edges
        start = end
        print("Finding connected components in the graph...", end="")
        ccomponents = self.sorting_ccomponents(list(nx.connected_components(self.graph.to_undirected())))
        print("connected components (step 1): " + str(len(list(ccomponents))))
        print(self.graph.number_of_edges() / 2)
        end = time.time()
        print("Elapsed time: %f seconds" % (end - start))

        # remove all the edges of the graph which weight is smaller than the threshold
        start = end
        print("Removing edges which weight is smaller than a threshold... ", end="")
        self.remove_below_threshold(13.0)
        end = time.time()
        print("Elapsed time: %f seconds" % (end - start))

        # find the connected components after the removal of the edges: each component (group of topics) are the final super topics for that threshold
        start = end
        ccomponents = self.sorting_ccomponents(list(nx.connected_components(self.graph.to_undirected())))
        print("connected components (step 2): " + str(len(list(ccomponents))))
        print(self.graph.number_of_edges() / 2)
        end = time.time()
        print("Elapsed time: %f seconds" % (end - start))

        # write the results to a csv file
        self.write_to_csv(ccomponents, threshold)

### MAIN
if __name__ == "__main__":
    infolder = "/home/robertacoeli/Documents/Mestrado/resultados/topicos" # input folder (folder containing the subfolders of the months, which each contains the "final_btm_model.twords" file)
    graph_filename = "/home/robertacoeli/Documents/Mestrado/resultados/agregacao_topicos/graph_all_to_all_similarities.gml" # name of the topic similarity graph file
    num_topics = 10  # number of topics that were used in the study
    threshold = 13 # the threshold for the similarity edges in the topic similarity graph

    tg = TopicsGrouping(infolder, graph_filename, num_topics)
    tg.run(threshold)