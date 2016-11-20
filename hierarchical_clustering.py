import json
import math
import pprint
import random
from collections import defaultdict

json_file = open("./partial/inverted_subreddits.json", 'r')
users_file = open("./partial/users.txt", 'r')
defaults_file = open("./partial/defaults.json", 'r')
subs_dict = json.load(json_file)
defaults_list = json.load(defaults_file)

n_clusters_per_level = 5
users_threshold = 500

users = []
for line in users_file:
	users.append(line.split("\t")[0])

"""
max_similarity = 0
chosen1 = ""
chosen2 = ""
count = 0
for sub in subs_dict:
	if len(subs_dict[sub]) < 400: continue
	sub_set = set(subs_dict[sub])
	for sub2 in subs_dict:
		if len(subs_dict[sub2]) < 400: continue
		if (sub!=sub2):
			sub2_set = set(subs_dict[sub2])
			similarity = len(sub_set.intersection(sub2_set)) / math.sqrt(len(subs_dict[sub])*len(subs_dict[sub2]))
			if similarity > max_similarity:
				max_similarity = similarity
				chosen1 = sub
				chosen2 = sub2
	count+=1

print str(count) + " " + str(max_similarity) + " sub1: " + chosen1 + " sub2: " + chosen2
"""
"""
clusters = []
for sub in subs_dict:
	if len(subs_dict[sub]) < 500: continue
	clusters.append(sub)

while len(clusters) > 1:
	max_similarity = 0
	candidate = []
	for sub1 in clusters:
		sub1_set = frozenset(subs_dict[sub1])
		for sub2 in clusters:
			if sub1 != sub2:
				sub2_set = frozenset(subs_dict[sub2])
				similarity = len(sub1_set.intersection(sub2_set)) / math.sqrt(len(subs_dict[sub])*len(subs_dict[sub2]))
				if similarity > max_similarity:
					max_similarity = similarity
					candidate = []
					candidate.append(sub1)
					candidate.append(sub2)

	for item in candidate:
		clusters.remove(item)
		print type(candidate)
	clusters.append(candidate)
	break

pprint.pprint(clusters)
"""


def kmeans (this_subs_dict):

	centers = []
	clusters = {}
	cycle = 0

	for i in range(n_clusters_per_level):
		centers.append(random.choice(this_subs_dict.keys()))

	while (cycle < 5):

		print "\n\n ***** CYCLE " + str(cycle) + " *****\n\n"	

		clusters = {}

		for center in centers:
			clusters[center] = []

		count = 0
		for sub in this_subs_dict:
			max_similarity = 0
			candidate = ""
			for center in centers:
				size_of_intersection = 0
				for user in this_subs_dict[sub]:
					if user in this_subs_dict[center]: size_of_intersection += 1
				similarity = size_of_intersection / math.sqrt(len(this_subs_dict[center])*len(this_subs_dict[sub]))
				if similarity > max_similarity:
					max_similarity = similarity
					candidate = center
			clusters[candidate].append(sub)

			count+=1
			print count,

		pprint.pprint(clusters)

		centers = []
		for item in clusters:
			
			avg = defaultdict(float)
			num_of_users_not_zero = 0
			for sub in clusters[item]:
				for user in this_subs_dict[sub]:
					avg[user] += 1
			for user in avg:
				avg[user] = int(round(avg[user]/len(clusters[item])))
				if avg[user] != 0: num_of_users_not_zero += 1

			candidate = ""
			max_similarity = 0
			for sub in clusters[item]:
				size_of_intersection = 0
				for user in avg:
					if avg[user] != 0 and user in this_subs_dict[sub]:
						size_of_intersection += 1
				similarity = size_of_intersection / math.sqrt(num_of_users_not_zero * len(this_subs_dict[sub]))
				if similarity > max_similarity:
					max_similarity = similarity
					candidate = sub
			centers.append(candidate)

		pprint.pprint(centers)

		cycle+=1

	return clusters	
	

tree = {}

this_subs_dict = {}

for sub in subs_dict:
	if len(subs_dict[sub]) > 900: this_subs_dict[sub] = subs_dict[sub]

first_cluster = kmeans(this_subs_dict)
for c in first_cluster:
	if len(first_cluster[c]) > 50:

json.dump()



