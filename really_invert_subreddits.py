from collections import defaultdict
import json
from sets import Set

users_file = open("./partial/users.txt", 'r')
inverted_subreddits_file = open("./partial/inverted_subreddits.json", 'r+')

subs_dict = defaultdict(list)

for line in users_file:
	user = line.strip().split("\t")[0]
	if len(line.strip().split("\t"))==1: continue
	sublist = line.strip().split("\t")[1].split(" ")
	for sub in sublist:
		sub = sub.split("::")[0]
		subs_dict[sub].append(user)

json.dump(subs_dict, inverted_subreddits_file, indent=4)
