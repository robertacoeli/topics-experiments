# TopicsExperiments

Scripts for calculating similarity between topics and building the topic similarity graph.

## Folders

* src
    * **similarity_calculations**: basic functions to calculate similarity (Jaccard and Word Overlap) and to build the topic pairs matrix (to build the similarity graph).
    * **01_calculate_similarity**: builds the topic similarity graph and saves auxiliary files to the output folder.
    * **01_successive_grouping**: executes the grouping algorithm and put the results into a csv file.

## Files

For the most part of the scripts, the "main" function is located at the end of the file, i.e., after the methods and class definitions. It contains the inputs and outputs, as well as it calls the function that executes the task for the script.

# Examples

If you may find it useful to check some input and output files to understand how the scripts operate, you can check some of them by this [Google Drive folder](https://drive.google.com/drive/folders/1LivGb9Nddbl2FByLqq6yPezBHxRzfBpT?usp=sharing).