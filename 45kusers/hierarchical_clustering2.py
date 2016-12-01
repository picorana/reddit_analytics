import json
import math
import pprint
import random
import numpy as np
from scipy.spatial.distance import jaccard, hamming
from collections import defaultdict

json_file = open("inverted_subreddits.json", 'r')
users_file = open("users.txt", 'r')
defaults_file = open("../partial/defaults.json", 'r')
subs_dict = json.load(json_file)
defaults_list = json.load(defaults_file)

num_of_users_in_sub_threshold = 50
num_of_posts_in_different_subs_threshold = 50

def build_occurrence_matrix():
	users = []
	for line in users_file:
		if len(line.split('\t')) < 2: continue
		user = line.split('\t')[0]
		num_of_different_subs = len(line.split('\t')[1].strip().split(' '))
		if num_of_different_subs < num_of_posts_in_different_subs_threshold: continue
		users.append(line.split("\t")[0])

	f = open('user_list.json', 'w')
	user_array = []
	for i in range(len(users)):
		user_array.append(users[i])
	print len(user_array)
	json.dump(user_array, f, indent=4)

	f = open('sub_user_matrix.txt', 'w')
	f_bool = open('sub_user_matrix_bool.txt', 'w')
	sub_list_file = open('sub_list.json', 'w')
	sub_list = []
	count = 0
	for sub in subs_dict:
		if len(subs_dict) < num_of_users_in_sub_threshold: continue
		sub_list.append(sub)
		this_array = []
		this_array_bool = []
		for user in users:
			if user in subs_dict[sub]:
				this_array.append(1)
				this_array_bool.append(True)
			else:
				this_array.append(0)
				this_array_bool.append(False)

		towrite = sub + "\t"
		for value in this_array:
			towrite += str(value) + " "
		f.write(towrite + '\n')

		towrite = sub + '\t'
		for value in this_array_bool:
			towrite += str(value) + " "
		f_bool.write(towrite + '\n')

		count += 1
		if count%10==0: print count
	json.dump(sub_list, sub_list_file, indent=4)

# keep in mind that 4000 x 4000 int = 64 mb
def build_distance_matrix():
	f = open('sub_user_matrix.txt', 'r')
	res_file = open('similarity_matrix.txt', 'w')
	
	count = 0
	line = f.readline()
	while line!='':
		sub = line.split('\t')[0]
		sub1_array = line.strip().split('\t')[1].split(' ')
		res_array = []
		print sub
		"""
		f.seek(0)
		line2 = f.readline()
		while line2 != '':
			sub2 = line.split('\t')[0]
			print sub, sub2
			sub2_array = line.strip().split('\t')[1].split(' ')
			res_array.append(hamming(sub1_array, sub2_array))
			line2 = f.readline()
		"""
		f.seek(count)
		
		towrite = sub + '\t'
		for value in res_array:
			towrite += str(value) + ' '
		#res_file.write(towrite)

		count+=1
		#if count%10==0: print count
		line = f.readline()


#build_occurrence_matrix()
build_distance_matrix()