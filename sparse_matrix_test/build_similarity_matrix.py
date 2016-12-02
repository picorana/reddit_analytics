from scipy.sparse import dok_matrix
from scipy.spatial.distance import jaccard, hamming
from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN, Birch
from collections import defaultdict
import numpy as np
import random
import sys
import gc
import json
import cPickle
import time
import pprint

json_file = open("inverted_subreddits.json", 'r')
users_file = open("users.txt", 'r')
defaults_file = open("../partial/defaults.json", 'r')

subs_dict = json.load(json_file)
defaults_list = json.load(defaults_file)

num_of_posts_in_different_subs_threshold = 50
sub_threshold = 50

def build_users_list_json():
	result_file = open('users.json', 'w')

	users = []
	for line in users_file:
		if len(line.split('\t')) < 2: continue
		user = line.split('\t')[0]
		num_of_different_subs = len(line.split('\t')[1].strip().split(' '))
		if num_of_different_subs < num_of_posts_in_different_subs_threshold: continue
		users.append(line.split("\t")[0])
	json.dump(users, result_file, indent=4)

def build_sub_list_json():
	result_file = open('sub_list.json', 'w')

	subs = []
	for sub in subs_dict:
		if len(subs_dict[sub]) < sub_threshold: continue
		subs.append(sub)
	json.dump(subs, result_file, indent=4)

def build_sparse_matrix():
	user_json = open('users.json', 'r')
	subs_list_file = open('sub_list.json', 'r')
	result_file = open('occurrence_sparse_matrix.p', 'w')
	users_list = json.load(user_json)
	subs_list = json.load(subs_list_file)

	occurrences_matrix = dok_matrix((len(subs_dict),len(users_list)))
	
	print len(subs_list)

	sub_count = 0
	for sub in subs_list:
		usr_count = 0
		for user in users_list:
			if user in subs_dict[sub]:
				occurrences_matrix[sub_count, usr_count] = 1
			usr_count += 1
		sub_count += 1
		if sub_count % 10 == 0: print sub_count
	
	cPickle.dump(occurrences_matrix, result_file)

def build_distance_matrix():
	start_time = time.time()
	distance_matrix = np.empty([len(subs_list), len(subs_list)])
	result_file = open('similarity_matrix.p', 'w')

	# 6.7 seconds to read matrix with 4000 subs and 16000 users
	mat = cPickle.load(open('occurrence_sparse_matrix.p', 'r'))

	for i in range(len(subs_list)):
		sub = subs_list[i]

		min_distance = float('inf')
		candidate = ''

		for j in range(i, len(subs_list)):
			# 0.03 seconds to do a jaccard similarity
			distance = jaccard(mat[i].toarray(), mat[j].toarray())
			distance_matrix[i][j] = distance
			distance_matrix[j][i] = distance

			if j!=i and distance <= min_distance:
				min_distance = distance
				candidate = subs_list[j]


			if j % 10 == 0: print j,

		print '\nsimilarities for sub: ' + subs_list[i] + ' candidate: ' + candidate + ' number:' + str(i) + ' time: ' + str(time.time() - start_time)

	cPickle.dump(distance_matrix, result_file)

def kmeans():

	n_clusters = 10

	mat = cPickle.load(open('occurrence_sparse_matrix.p', 'r'))
	subs_list_file = open('sub_list.json', 'r')
	results_file = open('clusters.json', 'w')
	subs_list = json.load(subs_list_file)

	print 'starting clustering...'

	clusters = defaultdict(list)

	centroids = []
	for i in range(n_clusters):
		rand = random.randint(0, len(subs_list))
		centroids.append(subs_list[rand])

	count = 0
	for i in range(len(subs_list)):
		min_distance = float('inf')
		candidate = ''
		for centroid in centroids:
			centroid_index = subs_list.index(centroid)
			distance = jaccard(mat[i].toarray(), mat[centroid_index].toarray())
			if distance <= min_distance:
				min_distance = distance
				candidate = centroid
		clusters[candidate].append(subs_list[i])
		count += 1
		if count % 10 == 0: print count,

	json.dump(clusters, results_file, indent=4)




#build_users_list_json()
#build_sub_list_json()
#build_sparse_matrix()
#build_distance_matrix()
kmeans()
