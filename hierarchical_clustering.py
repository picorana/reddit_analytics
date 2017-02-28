import json
import math
import pprint
import random
import numpy as np
from collections import defaultdict

users_file = open("./partial/users.txt", 'r')
subs_dict = json.load(open("./partial/inverted_subreddits.json", 'r'))
defaults_list = json.load(open("./partial/defaults.json", 'r'))

n_clusters_per_level = 50
kmeans_cycles = 4
users_threshold = 4
subs_per_user_threshold = 100
nodes_per_level = 100

def retrieve_inverted_subreddits(subs_per_user_threshold):

	subs_dict = defaultdict(list)

	for line in users_file:
		user = line.strip().split("\t")[0]
		if len(line.strip().split("\t"))==1: continue
		sublist = line.strip().split("\t")[1].split(" ")
		if len(sublist) < subs_per_user_threshold: continue
		for sub in sublist:
			sub = sub.split("::")[0]
			subs_dict[sub].append(user)
	return subs_dict


def kmeans (this_subs_dict, depth):

	print len(this_subs_dict)

	centers = []
	clusters = {}
	cycle = 0

	for i in range(n_clusters_per_level - depth*5):
		centers.append(random.choice(this_subs_dict.keys()))
	#if depth == 0: centers = defaults_list
	
	print centers

	while (cycle < kmeans_cycles):

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
				if similarity >= max_similarity:
					max_similarity = similarity
					candidate = center
			if candidate == "": candidate = random.choice(centers)
			clusters[candidate].append(sub)

			count+=1
			if count%100==0: print count

		pprint.pprint(clusters)

		centers = []

		for item in clusters:
			biggest_size = 0
			candidate = ""
			for sub in clusters[item]:
				if len(subs_dict[sub]) >= biggest_size:
					biggest_size = len(subs_dict[sub])
					candidate = sub
			centers.append(candidate)

		pprint.pprint(centers)

		cycle+=1

	return clusters	
	

def fill_tree(last_node, this_subs_dict, depth):
	first_cluster = kmeans(this_subs_dict, depth)
	pprint.pprint(first_cluster)

	list_of_separated_nodes = []

	for c in first_cluster:
		cluster_dict = {'name':c, 'children' = []}
		
		if len(first_cluster[c]) < 10:
			for sub in first_cluster[c]:
				subdict = {'name':sub, 'size':len(subs_dict[sub])}
				list_of_separated_nodes.append(sub)

		elif len(first_cluster[c]) < nodes_per_level:
			for sub in first_cluster[c]:
				cluster_dict['children'].append({ 'name' : sub, 'size' : len(subs_dict[sub]) })

		else:
			new_subs_dict = {}
			for sub in first_cluster[c]:
				new_subs_dict[sub] = subs_dict[sub]
			fill_tree(cluster_dict, new_subs_dict, depth+1)

		last_node['children'].append(cluster_dict)

	if len(list_of_separated_nodes) > 100 and depth < 8:
		new_subs_dict = {}
		for sub in list_of_separated_nodes:
			new_subs_dict[sub] = subs_dict[sub]
		print len(list_of_separated_nodes)
		print len(new_subs_dict)
		if len(new_subs_dict)>5: fill_tree(last_node, new_subs_dict, depth+1)
	else:
		for sub in list_of_separated_nodes:
			last_node['children'].append({ 'name' : sub, 'size' : len(subs_dict[sub]) })

print len(subs_dict)
subs_dict = retrieve_inverted_subreddits(subs_per_user_threshold)
print len(subs_dict)

tree = {}
tree['name'] = 'reddit'
tree['children'] = []

this_subs_dict = {}

for sub in subs_dict:
	#if sub in defaults_list: continue
	if len(subs_dict[sub]) > users_threshold and len(subs_dict[sub])<3000: this_subs_dict[sub] = subs_dict[sub]
	if len(subs_dict[sub]) > 3000: print len(subs_dict[sub])

fill_tree(tree, this_subs_dict, depth=0)

json.dump(tree, open('data2.json', 'w'), indent=4)



