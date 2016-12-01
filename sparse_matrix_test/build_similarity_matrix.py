from scipy.sparse import dok_matrix
from scipy.spatial.distance import jaccard, hamming
import numpy as np
import json
import cPickle
import time

json_file = open("inverted_subreddits.json", 'r')
users_file = open("users.txt", 'r')
user_json = open('users.json', 'r')
subs_list_file = open('sub_list.json', 'r')
defaults_file = open("../partial/defaults.json", 'r')

subs_dict = json.load(json_file)
defaults_list = json.load(defaults_file)
users_list = json.load(user_json)
subs_list = json.load(subs_list_file)

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
	result_file = open('occurrence_sparse_matrix.p', 'w')
	occurrences_matrix = dok_matrix((len(subs_dict),len(users_list)))
	
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


#build_users_list_json()
#build_sub_list_json()
#build_sparse_matrix()

start_time = time.time()
# 6.7 seconds to read matrix with 4000 subs and 16000 users
mat = cPickle.load(open('occurrence_sparse_matrix.p', 'r'))
print str(time.time()-start_time) + ' seconds to load occurrence matrix'

start_time = time.time()
print subs_list[4]
min_distance = float('inf')
candidate = ''
count = 0
for i in range(len(subs_list)):
	if i==4: continue
	distance = hamming(mat[4].toarray(), mat[i].toarray())
	if (distance) <= min_distance:
		min_distance = distance
		candidate = subs_list[i]
	count += 1
	if count % 10 == 0: print count

print str(time.time()-start_time) + ' seconds to find most similar sub for 1 element'
print subs_list[4], candidate
print min_distance