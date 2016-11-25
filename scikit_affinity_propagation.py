import json
import pprint
import sklearn.cluster
import math
import numpy as np
import sys
from collections import defaultdict

max_user_threshold = 2000
min_user_threshold = 200

def compute_this_subs_dict(min_user_threshold, max_user_threshold):
	f = open('./partial/inverted_subreddits.json', 'r')
	subs_dict = json.load(f)
	this_subs_dict = {}

	for sub in subs_dict:
		if len(subs_dict[sub]) >= min_user_threshold and len(subs_dict[sub])<=max_user_threshold:
			this_subs_dict[sub] = subs_dict[sub]
			sub_list.append(sub)

	print ("subs with more than " + str(min_user_threshold) + " and less than " + str(max_user_threshold) + " users: " + str(len(this_subs_dict)))

	return this_subs_dict

def compute_distance_matrix(this_subs_dict):
	distance_matrix = np.empty([len(this_subs_dict), len(this_subs_dict)])

	index = 0
	for sub in this_subs_dict:
		index2 = 0
		for sub2 in this_subs_dict:
			size_of_intersection = 0
			for user in this_subs_dict[sub]:
				if user in this_subs_dict[sub2]: size_of_intersection += 1
			similarity = size_of_intersection / math.sqrt(len(this_subs_dict[sub])*len(this_subs_dict[sub2]))
			distance_matrix[index][index2] = similarity
			index2 += 1
		index += 1
		if index%10==0: print index

	return distance_matrix

sub_list = []
this_subs_dict = compute_this_subs_dict(min_user_threshold, max_user_threshold)

"""
distance_matrix = compute_distance_matrix(this_subs_dict)
outfile = open('distance_matrix.npy', 'w')
np.save(outfile, distance_matrix)
"""
outfile = open('distance_matrix.npy', 'r')
distance_matrix = np.load(outfile)

print sub_list[1]
max_similarity = 0
candidate = ''
index = 0
for i in distance_matrix[1]:
	if i>=max_similarity and sub_list[index]!=sub_list[1]:
		candidate = sub_list[index]
		max_similarity = i
	index += 1

print candidate

"""
affinity_propagation = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.8)
affinity_propagation.fit(distance_matrix)

cluster_dict = defaultdict(set)

index = 0
for i in affinity_propagation.labels_:
	cluster_dict[i].add(sub_list[index])
	index += 1

for s in cluster_dict:
	print cluster_dict[s]
"""