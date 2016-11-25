import praw
import pprint
from time import time
from sets import Set
from praw.helpers import submissions_between
from praw.helpers import flatten_tree
from collections import defaultdict

# Initialize PRAW
user_agent = ("uiii")
r = praw.Reddit(user_agent=user_agent)

# Initialize used dictionaries:
# users_dict:		users      --> 	subreddits of interest
# subreddits_dict:	subreddits --> 	subscribed users
# users_checked and subreddits_checked are used to not check the same user/subreddit twice
users_dict = {}
users_checked = Set()
users_queue = Set()
subreddits_dict = {}
subreddits_checked = Set()
subreddits_queue = Set()

# open files that store data
users_file = open("./partial/users.txt", "r+")
users_queue_file = open("./partial/users_queue.txt", "r+")
subreddits_file = open("./partial/subreddits.txt", "r+")
subreddits_queue_file = open("./partial/subreddits_queue.txt", "r+")

# read previous results from files
for line in users_file:
	line = line.strip().split('\t')
	sub_set = defaultdict(int)
	if len(line)==1: continue
	for subreddit in line[1].strip().split(' '):
		if len(subreddit.split('::'))==1: continue
		value = subreddit.split('::')[1]
		if value == '': continue
		sub_set[subreddit.split('::')[0]] = int(value)
	users_dict[line[0]] = sub_set

for line in users_queue_file:
	users_queue.add(line.strip())

for line in subreddits_file:
	line = line.strip().split('\t')
	users_set = Set()
	for user in line[1].split(' '):
		users_set.add(user)
	subreddits_dict[line[0]] = users_set

for line in subreddits_queue_file:
	subreddits_queue.add(line.strip())

def retrieve_subreddits_from_username (username):
	if username in users_dict: return
	if username in users_queue: users_queue.remove(username)

	print "\n\nadding user: " + username + " ",
	user = r.get_redditor(username)
	this_user_subreddits = defaultdict(int)

	count = 0
	for thing in user.get_overview(limit=None):
		s = str(thing.subreddit)
		this_user_subreddits[s] += 1
		count+=1
		if count%100==0:
			print str(count) + " ",
	print ""

	users_dict[username] = this_user_subreddits

	for subreddit in this_user_subreddits:
		if subreddit not in subreddits_queue and subreddit not in subreddits_dict:
			subreddits_queue.add(subreddit)

	print_user_to_user_file(username)
	
def print_user_to_user_file (username):
	if username not in users_dict: 
		print "!!!!!!!!!\n\n\n	ERROR in print_user_to_user_file \n\n\n!!!!!!!!!"
	
	towrite = ""
	for subreddit in users_dict[username]:
		towrite+=subreddit +"::"+str(users_dict[username][subreddit])+ " "
	towrite = towrite[:-1]
	users_file.write(username + "\t" + towrite + "\n")

def retrieve_usernames_from_subreddit (subreddit):
	start_time = time()
	if subreddit in subreddits_dict: return
	if subreddit in subreddits_queue: subreddits_queue.remove(subreddit)
	subredditr = r.get_subreddit(subreddit)

	this_subreddit_users = Set()

	count = 0
	count2 = 0
	for submission in subredditr.get_hot(limit=None):
		user = str(submission.author)
		this_subreddit_users.add(user)
		for comment in flatten_tree(submission.comments):
			if (hasattr(comment, 'author')): 
				user = str(comment.author)
				this_subreddit_users.add(user)
			count += 1
			if count%10==0: print "#",
		count2+=1
		if count2%100==0: print "\nsubmission count: " + str(count2)

	subreddits_dict[subreddit] = this_subreddit_users

	for user in this_subreddit_users:
		if user not in users_dict and user not in users_queue: users_queue.add(user)

	print_subreddit_to_subreddit_file(subreddit)

	print "\ntime for subreddit " + subreddit + ": " + str(time()-start_time)

def print_subreddit_to_subreddit_file (subreddit):
	if subreddit not in subreddits_dict: 
		print "!!!!!!!!!\n\n\n	ERROR in print_subreddit_to_subreddit_file \n\n\n!!!!!!!!!"
	
	towrite = ""
	for user in subreddits_dict[subreddit]:
		towrite+=user + " "
	towrite = towrite[:-1]
	subreddits_file.write(subreddit + "\t" + towrite + "\n")

# use this method when closing the program, it saves the current state and what is still there to do
def print_queues_to_file():
	users_queue_file = open("./partial/users_queue.txt", "r+")
	subreddits_queue_file = open("./partial/subreddits_queue.txt", "r+")
	
	for item in users_queue:
		users_queue_file.write(item+"\n")
	users_queue_file.truncate()

	for item in subreddits_queue:
		subreddits_queue_file.write(item+"\n")
	subreddits_queue_file.truncate()


def print_current_stats():
	print "\n\n ******** \n\n ********"
	print "users in users_dict:\t" + str(len(users_dict))
	print "users in users_queue:\t" + str(len(users_queue))
	print "subreddits in subreddits_dict:\t" + str(len(subreddits_dict))
	print "subreddits in subreddits_queue:\t" + str(len(subreddits_queue))
	print "\n\n ******** \n\n ********"

retrieve_usernames_from_subreddit('gonewild')
"""
users_queue2 = users_queue.copy()
for user in users_queue2:
	try: retrieve_subreddits_from_username(user)
	except: print 'error!!!'
"""	
print_queues_to_file()
print_current_stats()