import json
import random
import math
from collections import defaultdict

n_clusters = 50

json_file = open("./partial/inverted_subreddits.json", 'r')
subs_dict = json.load(json_file)

centroids = set()
new_centroids = set()

clusters = defaultdict(set)

for i in range(n_clusters):
	centroid = random.choice(subs_dict.keys())
	centroids.add(centroid)
	clusters[centroid].add(centroid)

for sub in subs_dict:
	list_of_users = set(subs_dict[sub])

	candidate_centroid = 'ERROR'
	min_distance = float('inf')

	for center in centroids:
		set_center = set(subs_dict[center])
		this_min_distance = math.sqrt(len(set_center.intersection(list_of_users)) * len(list_of_users.intersection(set_center))) / math.sqrt(len(list_of_users) * len(subs_dict[center]))
		if this_min_distance < min_distance:
			min_distance = this_min_distance
			candidate_centroid = center

	clusters[candidate_centroid].add(sub)

count = 0
for cluster in clusters:
	f = open("./clusters/cluster_" + str(count) + ".json", 'w')
	cluster_list = list(clusters[cluster])
	json.dump(cluster_list, f, indent=4)
	count+=1