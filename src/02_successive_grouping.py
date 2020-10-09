''' 
    This script groups the topics according to the similarity values.

    inputs: 
    1) folder containing BTM top words for each month in the studied period. The folder of *each month* must contain the file "final_btm_model.twords" (example of the format of this file in https://drive.google.com/file/d/15F0G8bKNFQMBDYa2F7mAx8XDZc3fXypq/view?usp=sharing)
    2) name of the topic similarity graph file

    output: text file containing the similarity between the topics. Example of output file: "general_measures.txt" in the Google Drive Folder (https://drive.google.com/drive/folders/17HGKIUlRcRMq3BuHtazAllTiaohBozg9?usp=sharing)
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

    # 
    def find_marker_position(self, topic_identifier):
        tid = topic_identifier.strip().split("_")
        if int(tid[0]) == min(years):
            return int(tid[1]) - 1
        else:
            return int(tid[1]) + 12 - 1

    def find_component_words(self, item_component):
        words_set = set()
        for c in item_component:
            words_set.update(self.topics_dict[c])
        return words_set

    def is_in_grouping_pair(self, grouping_pairs, v1, v2):
        for i in range(0,len(grouping_pairs)):
            if (v1 in grouping_pairs[i]) or (v2 in grouping_pairs[i]):
                return i
        return -1

    def find_grouping_pairs(self, ccomponents, threshold):
        grouping_pairs = []
        tam_components = len(ccomponents)
        for i in range(0, tam_components):
            words_set_comp1 = self.find_component_words(ccomponents[i])
            for j in range(i + 1, tam_components):
                words_set_comp2 = self.find_component_words(ccomponents[j])
                min_setsize = min([len(words_set_comp1), len(words_set_comp2)])
                # print(len(words_set_comp1.intersection(words_set_comp2)))
                if len(words_set_comp1.intersection(words_set_comp2)) >= (threshold * min_setsize):
                    igp = self.is_in_grouping_pair(grouping_pairs, i, j)
                    # print("MIN SET SIZE: " + str(min_setsize))
                    if igp >= 0:
                        grouping_pairs[igp].update([i,j])
                    else:
                        grouping_pairs.append({i, j})
                    # print("analisando " + "i: " + str(i) + " j: " + str(j))
                    # print(words_set_comp1)
                    # print(words_set_comp2)
                    # print(words_set_comp1.intersection(words_set_comp2))

        return grouping_pairs

    # agrupamento sucessivo de componentes
    def successive_grouping(self, ccomponents, threshold):
        grouping_pairs = self.find_grouping_pairs(ccomponents, threshold)
        new_components = []
        print(grouping_pairs)
        # sys.exit(0)

        while len(grouping_pairs) > 0:
            new_components = []
            all_paired = []
            for gp in grouping_pairs:
                nc = []
                for item in gp:
                    all_paired.append(item)
                    nc += ccomponents[item]
                new_components.append(nc)

            for i in range(0, len(ccomponents)):
                if i not in all_paired:
                    new_components.append(ccomponents[i])
            ccomponents = new_components

            grouping_pairs = self.find_grouping_pairs(new_components, threshold)
            print(grouping_pairs)

        print(len(new_components))

        if len(new_components) == 0:
            return ccomponents
        else:
            return new_components

    # write results to csv file
    def write_to_csv(self, ccomponents, complement_name):
        filepath = os.path.join(self.fname, self.subfolder, "similar_topics_criteria_" +
                                complement_name)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        csvfile = open(os.path.join(filepath, "table.csv"), "w")
        wordsfile = open(os.path.join(filepath, "table_words.txt"), "w")
        wordsfile2 = open(os.path.join(filepath, "table_words_index.csv"), "w")
        period_column = ""
        for y in [2015,2016]:
            for m in range(1,13):
                period_column += ("%02d" % m) + "/" + str(y) + ";"
        csvfile.write("Topic Number;" + period_column +
                      "Size of Subset of Topics\n") # 27 columns
        wordsfile2.write("Topic Number;Topics Set;Words Set\n")
        topic_number = 1
        for array_component in ccomponents:
            words_set = set()
            period_list = [' ' for _ in range(0,24)]
            for c in array_component:
                position = self.find_marker_position(c)
                period_list[position] = 'X'
                words_set.update(self.topics_dict[c])
            csvfile.write(("%03d" % topic_number) + ";" +
                          (";".join(period_list)) + ";" +
                          str(len(array_component)) + "\n")
            wordsfile.write("\n\n-------- TOPIC " + ("%03d" % topic_number) + " --------\n")
            wordsfile.write("Words: ")
            wordsfile.write(", ".join(words_set) + "\n")
            wordsfile.write("Subset of topics: ")
            wordsfile.write((", ".join(array_component)) + "\n")
            wordsfile2.write(str(topic_number) + ";" + (", ".join(array_component)) + ";" +
                             (" ".join(words_set)) + "\n")
            topic_number += 1
        csvfile.close()
        wordsfile.close()

    # get topics spreadsheet
    def get_spreadsheet(self):
        print("Analysing graph and getting topics spreadsheet...")

        start = time.time()
        print("Removing edges which weight is zero... ", end="")
        self.remove_zero_weights()
        end = time.time()
        print("Elapsed time: %f seconds" % (end - start))
        start = end
        ccomponents = self.sorting_ccomponents(list(nx.connected_components(self.graph.to_undirected())))
        print("connected components (step 1): " + str(len(list(ccomponents))))
        print(self.graph.number_of_edges() / 2)

        # print("Removing edges which weight is smaller than the max one... ", end="")
        # self.keep_only_max()
        # end = time.time()
        # print("Elapsed time: %f seconds" % (end - start))
        # start = end
        # ccomponents = self.sorting_ccomponents(list(nx.connected_components(self.graph.to_undirected())))
        # print("connected components (step 2): " +
        #       str(len(list(ccomponents))))
        # print(self.graph.number_of_edges() / 2)

        print("Removing edges which weight is smaller than a threshold... ", end="")
        self.remove_below_threshold(13.0)
        end = time.time()
        print("Elapsed time: %f seconds" % (end - start))
        ccomponents = self.sorting_ccomponents(list(nx.connected_components(self.graph.to_undirected())))
        print("connected components (step 3): " +
              str(len(list(ccomponents))))
        print(self.graph.number_of_edges() / 2)

        self.write_to_csv(ccomponents, "simple_edge_removal")

        # tc = 0.8
        # ccomponents = self.successive_grouping(ccomponents, tc)

        # self.write_to_csv(ccomponents, "successive_grouping_" + str(int(tc * 100)) +
        #                   "_1-3_threshold_035")

### MAIN
if __name__ == "__main__":
    infolder = "/home/robertacoeli/Documents/Mestrado/resultados/topicos" # input folder (folder containing the subfolders of the months, which each contains the "final_btm_model.twords" file)
    graph_filename = "/home/robertacoeli/Documents/Mestrado/resultados/agregacao_topicos/graph_all_to_all_similarities.gml" # name of the topic similarity graph file
    num_topics = 10  # number of topics that were used in the study
    tsp = TopicsGrouping(infolder, graph_filename, num_topics)
    tsp.get_spreadsheet()