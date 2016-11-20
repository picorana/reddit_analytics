from sklearn.cluster import KMeans
from collections import defaultdict
import json
import numpy as np

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

kmeans = KMeans(n_clusters=20).fit(X)

clusters = defaultdict(set)


for sub in subs_array_dict:
	clusters[kmeans.predict(subs_array_dict[sub])[0]].add(sub)

index = 0
for cluster in clusters:
	f = open("./clusters/cluster_" + str(index) + ".json", 'w')
	cluster_list = list(clusters[cluster])
	json.dump(cluster_list, f, indent=4)
	print "**** CLUSTER " + str(index) + " ****"
	for item in clusters[cluster]:
		print item,
	print "\n****\n"
	index+=1