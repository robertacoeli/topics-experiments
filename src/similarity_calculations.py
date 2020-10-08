import numpy as np

# Jaccard topic matrix
def calculate_jaccard(topics1, topics2, num_topics):
    topic_pairs_matrix = np.zeros((num_topics, num_topics))
    for i in range(num_topics):
        for j in range(num_topics):
            t1 = set(topics1[i].split())
            t2 = set(topics2[j].split())
            topic_pairs_matrix[i][j] = len(t1.intersection(t2)) / len(t1.union(t2))
    return topic_pairs_matrix

# Word overlap topic matrix
def calculate_word_overlap(topics1, topics2, num_topics):
    topic_pairs_matrix = np.zeros((num_topics, num_topics), dtype=int)
    for i in range(num_topics):
        for j in range(num_topics):
            for tw in topics1[i].split():
                if tw in topics2[j].split():
                    topic_pairs_matrix[i][j] += 1
    return topic_pairs_matrix

# calculate model similarity
def calculate_similarity(topic_pairs_matrix, num_topics):
    topics_in = set()
    topics_max = []
    for ts in topic_pairs_matrix:
        topic_max_sim = np.amax(ts)
        argmax_topics = list(np.argwhere(ts == topic_max_sim).flatten())
        topics_in.update(argmax_topics)
        # tolerance of 5% for similarity values
        for i in range(len(ts)):
            if ts[i] > 0.95 * topic_max_sim:
                topics_in.add(i)
        topics_max.append(topic_max_sim)
    model_similarity = np.mean(topics_max)

    # adjust index according to "real" index (1 .. 10)
    new_topics = [(nt + 1) for nt in set(range(num_topics)) - topics_in]

    # return results
    return (model_similarity, sorted(new_topics), topic_pairs_matrix)

# WO similarity
def calculate_word_overlap_similarity(topics1, topics2, num_topics):
    topic_pairs_matrix = calculate_word_overlap(topics1, topics2, num_topics)
    return calculate_similarity(topic_pairs_matrix, num_topics)

# Jaccard similarity
def calculate_jaccard_similarity(topics1, topics2, num_topics):
    topic_pairs_matrix = calculate_jaccard(topics1, topics2, num_topics)
    return calculate_similarity(topic_pairs_matrix, num_topics)