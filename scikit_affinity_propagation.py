import json
import pprint
import sklearn.cluster
import math
import numpy as np
import sys
from collections import defaultdict
import time

max_user_threshold = 2000
min_user_threshold = 1000

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
outfile = open('distance_matrix2.npy', 'w')
np.save(outfile, distance_matrix)
"""
outfile = open('distance_matrix2npy', 'r')
distance_matrix = np.load(outfile)
"""
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

availability_matrix = np.zeros([len(distance_matrix), len(distance_matrix)])
responsibility_matrix = np.zeros([len(distance_matrix), len(distance_matrix)])

start_time = time.time()
count = 0
for i in range(len(distance_matrix)):
	for j in range(len(distance_matrix[i])):
		max_val = 0
		for k in range(len(distance_matrix[i])):
			if k != j:
				if (availability_matrix[i][k] + distance_matrix[i][k]) >= max_val:
					max_val = availability_matrix[i][k] + distance_matrix[i][k]
		responsibility_matrix[i][j] = distance_matrix[i][j] - max_val
	count +=1
	if count%10==0: print count

pprint.pprint(responsibility_matrix)
print "time for 1 cicle of 133 subs: " + str(time.time()-start_time)

# 1090 x 1090 x 1090 = 