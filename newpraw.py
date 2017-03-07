import praw
import pprint
import time
import json
from collections import defaultdict
from pattern.en import parse
from pattern.en import parsetree
from pattern.en.wordlist import PROFANITY
from pattern.search import search
from pattern.search import Pattern
from pattern.search import taxonomy, WordNetClassifier
from pattern.search import match
from os import listdir

def get_reddit_instance():

	config_file = open('config_keys.txt', 'r')
	client_id = config_file.readline().split('=')[1].strip()
	client_secret = config_file.readline().split('=')[1].strip()

	reddit = praw.Reddit(client_id=client_id,
	                     client_secret=client_secret,
	                     user_agent='subreddit_map')
	return reddit
	
def save_a_bunch_of_comments(reddit, subreddit):
	cur_dict = {}
	start_time = time.time()
	count = 0

	for submission in reddit.subreddit(subreddit).hot(limit=0):
		print submission.title
		#submission.comments.replace_more(limit=0)
		for comment in submission.comments.list():
			#print vars(comment)
			if(hasattr(comment, 'body')):
				cur_dict[comment.id] = comment.body
			
			if hasattr(comment, 'replies'):
				for reply in comment.replies:
					if hasattr(reply, 'body'):
						cur_dict[reply.id] = reply.body

	print time.time() - start_time

	output_file = open('./tmp_data/'+ subreddit +'.json', 'w')
	json.dump(cur_dict, output_file, indent=4)

	print len(cur_dict)
	return cur_dict

def fetch_comments(comment_list):

	tmp_list = list()

	for comment in comment_list:
			#pprint.pprint(vars(comment))

		if(hasattr(comment, 'body')):

			comment_dict = {}

			comment_dict['id'] = comment.id
			if(comment.author!=None):
				comment_dict['author'] = comment.author.name
			else:
				comment_dict['author'] = "NONE"
			comment_dict['body'] = comment.body
			comment_dict['score'] = comment.score
			comment_dict['ups'] = comment.ups
			comment_dict['downs'] = comment.downs
			comment_dict['created'] = comment.created
			comment_dict['subreddit'] = comment.subreddit.display_name
			comment_dict['link_id'] = comment.link_id
			comment_dict['gilded'] = comment.gilded

			if len(comment.replies)>0:
				comment_dict['replies'] = fetch_comments(comment.replies)

			tmp_list.append(comment_dict)
	
	return tmp_list

def save_a_bunch_of_comments_structured(reddit, subreddit):
	cur_dict = {}
	
	
	start_time = time.time()
	count = 0

	for submission in reddit.subreddit(subreddit).hot(limit=1000):

		submission_dict = {}

		submission_dict['id'] = submission.id
		submission_dict['title'] = submission.title
		submission_dict['selftext'] = submission.selftext
		submission_dict['num_comments'] = submission.num_comments
		submission_dict['score'] = submission.score
		if(submission.author!=None):
			submission_dict['author'] = submission.author.name
		else:
			submission_dict['author'] = "NONE"
		#submission_dict['author'] = submission.author.name
		#pprint.pprint(vars(submission.author))
		submission_dict['gilded'] = submission.gilded
		submission_dict['comments'] = list()

		if len(submission.comments)>0:
			submission_dict['comments'] = fetch_comments(submission.comments)

		cur_dict[submission_dict['id']] = submission_dict
		count += 1
		if count%10==0: print subreddit + ": " + str(count)

	print time.time() - start_time

	output_file = open('./tmp_data/'+ subreddit +'.json', 'w')
	json.dump(cur_dict, output_file, indent=4)

	print len(cur_dict)
	return cur_dict

def load_a_bunch_of_comments(subreddit):
	input_file = open('./tmp_data/'+ subreddit +'.json', 'r')
	output_dict = json.load(input_file)
	return output_dict

def download_a_single_thread(reddit, url):
	submission = reddit.submission(url=url)
	submission_dict = {}

	submission_dict['id'] = submission.id
	submission_dict['title'] = submission.title
	submission_dict['selftext'] = submission.selftext
	submission_dict['num_comments'] = submission.num_comments
	submission_dict['score'] = submission.score
	submission_dict['subreddit'] = submission.subreddit.display_name
	if(submission.author!=None):
		submission_dict['author'] = submission.author.name
	else:
		submission_dict['author'] = "NONE"
	submission_dict['gilded'] = submission.gilded
	submission_dict['comments'] = list()

	if len(submission.comments)>0:
		submission.comments.replace_more()
		submission_dict['comments'] = fetch_comments(submission.comments)

	output_file = open('./single_threads/'+ submission.id +'.json', 'w')
	json.dump(submission_dict, output_file, indent=4)

def download_subreddit_data(reddit):
	subreddit_data_dict = defaultdict(int)

	users_file = open("../partial/users.txt", 'r')
	subs_per_user_threshold = 100

	subs_dict = defaultdict(list)

	for line in users_file:
		user = line.strip().split("\t")[0]
		if len(line.strip().split("\t"))==1: continue
		sublist = line.strip().split("\t")[1].split(" ")
		if len(sublist) < subs_per_user_threshold: continue
		if len(sublist) > 400: 
			#print "this user posted in: " + str(len(sublist))
			continue
		for sub in sublist:
			sub = sub.split("::")[0]
			subs_dict[sub].append(user)

	count = 0
	for sub in subs_dict:
		try:
			subr = reddit.subreddit(sub)
			subreddit_data_dict[sub] = subr.subscribers
		except: subreddit_data_dict[sub] = 0
		count += 1
		if count % 10 == 0: print count

	json.dump(subreddit_data_dict, open('subreddit_data.json', 'w'), indent=4)


reddit = get_reddit_instance()
download_subreddit_data(reddit)
#download_a_single_thread(reddit, 'https://www.reddit.com/r/movies/comments/2ljk71/official_discussion_interstellar_wide_release/')




#save_a_bunch_of_comments_structured(reddit, 'technology')

#working_dict = load_a_bunch_of_comments()
#pprint.pprint(working_dict)

"""
files_in_data = listdir('./tmp_data/')
input_file_subreddits = open('../nice_clustering/data2.json', 'r')
sub_dict = json.load(input_file_subreddits)
"""
"""
list_of_subs_to_download = []
for cluster in sub_dict['children']:
	if cluster['name'] == 'technology':
		for subcluster in cluster['children']:
			#list_of_subs_to_download.append(subcluster['name'])
			#save_a_bunch_of_comments_structured(reddit, subcluster['name'])
			for subsubcluster in subcluster['children']:
				#list_of_subs_to_download.append(subsubcluster['name'])
				#save_a_bunch_of_comments_structured(reddit, subsubcluster['name'])
				#pprint.pprint(subsubcluster)
				if ('children' in subsubcluster.keys()):
					for subsubsubcluster in subsubcluster['children']:
						pprint.pprint(subsubsubcluster['name'])

pprint.pprint(list_of_subs_to_download)

for sub in list_of_subs_to_download:
	if (sub + '.json') not in files_in_data:
		success = False
		while success!=True:
			try:
				save_a_bunch_of_comments_structured(reddit, sub)
				success = True
			except:
				print 'connection error'

"""
#save_a_bunch_of_comments_structured(reddit, 'programming')


"""
listadicose = []
for entry in working_dict:
	s = parsetree(working_dict[entry], relations=True, lemmata=True)
	for match in search('SBJ VP NP', s):
		tmpstring = ""
		tmpstring2 = ""
		for word in match.words:
			if len(taxonomy.parents(word.string))!=0:
				for item in taxonomy.parents(word.string):
					tmpstring += item.upper() + " "
			else:
				tmpstring += word.string + " "
			tmpstring2 += word.string + " "
		listadicose.append(tmpstring2)
		listadicose.append(tmpstring)
pprint.pprint(listadicose)
"""

"""
taxonomy.classifiers.append(WordNetClassifier())
for item in taxonomy.parents('lion'):
	print item
"""

