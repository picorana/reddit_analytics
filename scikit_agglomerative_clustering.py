import numpy as np
import json
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from collections import defaultdict
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

n_clusters = 10

json_file = open("./partial/inverted_subreddits.json", 'r')
users_file = open("./partial/users.txt", 'r')
defaults_file = open("./partial/defaults.json", 'r')
subs_dict = json.load(json_file)
defaults_list = json.load(defaults_file)

users = []

for line in users_file:
	users.append(line.split("\t")[0])

subcount = 0
for sub in subs_dict:
	if sub in defaults_list: continue
	if len(subs_dict[sub])>=100: subcount+=1

X = np.empty((subcount, len(users)))
subs_array_dict = {}

count = 0
for sub in subs_dict:
	if sub in defaults_list: continue
	if len(subs_dict[sub])<100: continue

	user_count = 0
	array = []
	for user in users:
		if user in subs_dict[sub]:
			array.append(1)
			user_count+=1
		else:
			array.append(0)

	for i in range(len(array)):
		array[i] = float(array[i])/float(user_count)

	X[count] = array
	subs_array_dict[sub] = array

	count +=1
	print count

model = AgglomerativeClustering(n_clusters=10, linkage="complete", affinity="cityblock")
model.fit_predict(X)

clusters = defaultdict(set)

index = 0
for item in model.labels_:
	for sub in subs_array_dict:
		if np.array_equal(X[index], subs_array_dict[sub]): 
			clusters[item].add(sub)

for cluster in clusters:
	print "**** CLUSTER " + str(cluster) + " ****"
	for item in clusters[cluster]:
		print item,
	print "\n****\n"
	index+=1