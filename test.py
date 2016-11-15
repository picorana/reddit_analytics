import praw
import pprint
from sets import Set

# Initialize PRAW
user_agent = ("uiii")
r = praw.Reddit(user_agent=user_agent)

# Initialize used dictionaries:
# users_dict:		users      --> 	subreddits of interest
# subreddits_dict:	subreddits --> 	subscribed users
# users_checked and subreddits_checked are used to not check the same user/subreddit twice
users_dict = {}
users_checked = Set()
users_not_checked = Set()
subreddits_dict = {}
subreddits_checked = Set()
subreddits_not_checked = Set()

# open files that store data
users_file = open("./partial/users.txt", "r+")
subreddits_file = open("./partial/subreddits.txt", "r+")

# read previous results from files
for line in users_file:
	line = line.strip().split('\t')
	sub_set = Set()
	for subreddit in line[1].split(' '):
		sub_set.add(subreddit)
	users_dict[line[0]] = sub_set
	# users_checked.add(line[0])

for line in subreddits_file:
	line = line.strip().split('\t')
	users_set = Set()
	for user in line[1].split(' '):
		users_set.add(subreddit)
	subreddits_dict[line[0]] = users_set
	# subreddits_checked.add(line[0])

def retrieve_subreddits_from_username (username):
	if username in users_dict: return
	user = r.get_redditor(username)
	this_user_subreddits = Set()
	count = 0
	print "adding user: " + username + " ",
	for thing in user.get_overview(limit=None):
		s = str(thing.subreddit)
		this_user_subreddits.add(s)
		count+=1
		if count%100==0:
			print str(count) + " ",
	print ""
	users_dict[username] = this_user_subreddits
	towrite = ""
	for subreddit in this_user_subreddits:
		towrite+=subreddit + " "
	towrite = towrite[:-1]
	users_file.write(user_name + "\t" + towrite + "\n")

print users_dict['Balkan4']
print users_dict['mother-of-one']