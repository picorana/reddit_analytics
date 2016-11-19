import json

outfile = open('data2.json', 'w')
inverted_subreddits_file = open('./partial/inverted_subreddits.json', 'r')
subs = json.load(inverted_subreddits_file)

init_dict = {}
init_dict['name'] = 'reddit'
init_dict['children'] = []

for i in range(20):
	cluster = json.load(open('./clusters/cluster_'+str(i)+'.json'))
	cluster_dict = {}
	init_dict['children'].append(cluster_dict)
	cluster_dict['name'] = 'cluster_' + str(i)
	cluster_dict['children'] = []
	for sub in cluster:
		sub_dict = {}
		sub_dict['name'] = sub
		sub_dict['size'] = len(subs[sub])
		cluster_dict['children'].append(sub_dict)

json.dump(init_dict, outfile, indent=4)