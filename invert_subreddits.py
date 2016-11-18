import json
import random
from collections import defaultdict
from sets import Set

init_dict = {}
nodes = []
links = []
sub_dict = defaultdict(int)
links_dict = defaultdict(int)

users_file = open("./partial/users.txt", 'r')
inverted_subreddits_file = open("./partial/inverted_subreddits.txt", 'r+')
outfile = open("data.json", 'w')

count = 0
for line in users_file:
	user = line.split('\t')[0]
	list_of_subreddits = line.split('\t')[1].strip().split(' ')
	for subreddit_line in list_of_subreddits:
		subreddit1 = subreddit_line.split('::')[0]
		sub_dict[subreddit1] += 1
		if len(subreddit_line.split('::'))==1: continue
		if int(subreddit_line.split('::')[1]) >=50:
			for subreddit_line2 in list_of_subreddits:
				if int(subreddit_line2.split('::')[1]) >=50:
					subreddit2 = subreddit_line2.split('::')[0]
					if subreddit1!=subreddit2:
						this_link = {}
						this_link['source'] = subreddit1
						this_link['target'] = subreddit2
						this_link['value'] = 1
						links.append(this_link)
		
	if count==20: break
	count+=1
	if count%10==0: print str(count) + " ",
	
for subreddit in sub_dict:
	this_subreddit_dict = {}
	this_subreddit_dict['id'] = subreddit
	this_subreddit_dict['group'] = random.randint(0, 5)
	this_subreddit_dict['radius'] = sub_dict[subreddit]
	if sub_dict[subreddit]>=0: 
		nodes.append(this_subreddit_dict)

init_dict['nodes'] = nodes
init_dict['links'] = links
json.dump(init_dict, outfile, indent=4)

