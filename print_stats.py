import json

users_file = open('./partial/users.txt', 'r')
inverted_subreddits_file = open('./partial/inverted_subreddits.json', 'r')
default_file = open('./partial/defaults.json', 'r')

subs = json.load(inverted_subreddits_file)
defaults = json.load(default_file)

count = 0
for line in users_file:
	count+=1
print "collected data about " + str(count) + " users"

count = 0
count2 = 0
for sub in subs:
	count+=1
	if len(subs[sub])>50: count2+=1
print "collected data about " + str(count) + " subreddits"
print str(count2) + " subreddits have more than 50 users"
count = 0
print "subreddits with most users: (no defaults)"
for k in sorted(subs, key=lambda k: len(subs[k]), reverse=True):

    if k not in defaults:
    	print k + ":" + str(len(subs[k])),
    	count += 1
    	if count == 200: break
    