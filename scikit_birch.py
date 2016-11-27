from sklearn.cluster import Birch
import json
import numpy as np
from collections import defaultdict
import pprint

json_file = open("./partial/inverted_subreddits.json", 'r')
users_file = open("./partial/users.txt", 'r')
defaults_file = open("./partial/defaults.json", 'r')
subs_dict = json.load(json_file)
defaults_list = json.load(defaults_file)

users = []
subs_list = []
this_subs_dict = {}
users_min_threshold = 500

for sub in subs_dict:
		if sub in defaults_list: continue
		if len(subs_dict[sub]) < users_min_threshold: continue
		this_subs_dict[sub] = subs_dict[sub]
		subs_list.append(sub)

def build_matrix(): 
	for line in users_file:
		if len(line.split('\t'))>1 and len(line.split('\t')[1].split(' ')) > 50: 
			users.append(line.split("\t")[0])

	print len(users)
	print len(this_subs_dict)

	X = np.zeros([len(this_subs_dict), len(users)])

	index = 0
	for sub in this_subs_dict:
		index2 = 0
		for user in users:
			if user in this_subs_dict[sub]:
				X[index][index2] = 1
			index2 += 1
		index += 1
		print index
	f = open('user_matrix.npy', 'w')
	np.save(f, X)
	return X

#X = build_matrix()
X = np.load(open('user_matrix.npy', 'r'))

brc = Birch(branching_factor=50, n_clusters=10, threshold=10, compute_labels=True)
brc.fit_predict(X)
#for item in brc.root_.subclusters_:
#	print vars(item.child_)
#print vars(brc.root_)

cluster_dict = defaultdict(set)
index = 0
for item in brc.labels_:
	cluster_dict[item].add(subs_list[index])
	index += 1

for c in cluster_dict:
	print cluster_dict[c]