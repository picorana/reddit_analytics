import json
import string
import pprint
from datetime import datetime
from collections import defaultdict
import re

from nltk.corpus import stopwords
from nltk.corpus import movie_reviews
from nltk.tokenize import sent_tokenize
from nltk.stem import *
from nltk import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk.corpus import sentiwordnet as swn
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

import ontospy



def clamp(n, minn, maxn):
	"""Clamps a variable between a minimum and a maximum value

	Args:
		n (int): variable to clamp
		minn (int): min bound
		maxn (int): max bound
	
	Returns:
		int: clamped variable
	"""
	return max(min(maxn, n), minn)

def iter_comments(start_month, end_month, base_input_path='../partial/worldnews_comments_'):
	for i in range(start_month, end_month):
		input_file = open(base_input_path + str(i) + '_2016.json', 'r')
		
		for line in input_file:
			comment = json.loads(line)

			yield comment

def iter_comment_bodies(start_month, end_month, remove_links = True, base_input_path='../partial/worldnews_comments_'):
	"""Read and return comments from files
	
	Args:
		start_month (int): start month from which the comments are read
		end_month (int): end month from which the comments are read
		remove_links (bool): if true, comments are returned without links (default: {True})
		base_input_path (str): base path of the files (default: {'../partial/worldnews_comments_'})
	
	Yields:
		str: a comment body
	"""
	for i in range(start_month, end_month):
		input_file = open(base_input_path + str(i) + '_2016.json', 'r')
		
		for line in input_file:
			comment = json.loads(line)
			
			if remove_links:
				yield re.sub(r"http\S+", '', comment['body'].encode('utf-8', errors='ignore').decode("utf8", errors='ignore'), flags=re.MULTILINE)

			else: yield comment['body']


def read_emotions_dict(depth = 'inf', path="../NIL_ontoEmotion/emotions_v11.owl"):
	"""Reads the ontology and returns an empty dict containing word describing emotions at the specified depth of the tree
	
	Args:
		depth: depth of the tree in the ontology (default: {'inf'})
		path: path of the ontology (default: {"../NIL_ontoEmotion/emotions_v11.owl"})
	
	Returns:
		dict: the keys of this dict are the names of emotions
	"""
	
	model = ontospy.Ontospy("../NIL_ontoEmotion/emotions_v11.owl")
	emotions_dict = {}
	emotions_parents = {}

	print 'Reading NIL_ontoEmotion...'

	if depth=='inf':
		for emotion_class in model.classes:
			emotions_dict[emotion_class.bestLabel().lower()] = []

	elif depth==1:
		for emotion_class in model.getClass('http://nil.fdi.ucm.es/projects/emotions/onto/emotions_v11.owl#Emotion').children():
			emotions_dict[emotion_class.bestLabel().lower()] = []
			for emotion_class_2 in emotion_class.children():
				emotions_parents[emotion_class_2.bestLabel().lower()] = emotion_class.bestLabel().lower()
				for emotion_class_3 in emotion_class_2.children():
					emotions_parents[emotion_class_3.bestLabel().lower()] = emotion_class.bestLabel().lower()
					for emotion_class_4 in emotion_class_3.children():
						emotions_parents[emotion_class_4.bestLabel().lower()] = emotion_class.bestLabel().lower()
		return emotions_dict, emotions_parents

	else: print 'DEPTH IN read_emotions_dict NOT IMPLEMENTED YET'

	return emotions_dict


def sentiwordnet_analysis(start_month, end_month, base_input_path='../partial/worldnews_comments_', granularity = 7):

	lemmatizer = WordNetLemmatizer()
	nouns_dict = defaultdict(int)
	emotions_dict, emotions_parents = read_emotions_dict(depth=1)
	pprint.pprint(emotions_parents)
	date_with_emotions = {}

	sentence_counter = 0

	print 'Reading comments...'
	# for each comment from the iterator function
	for comment in iter_comments(start_month, end_month):	

		date = datetime.fromtimestamp(float(comment['created_utc'])).replace(hour=0, minute=0, second=0, microsecond=0)
		date = date.replace(day=int( clamp(round(date.day/granularity)*granularity, 1, 31))) # group days by week - not sure about this

		if date not in date_with_emotions: date_with_emotions[date] = defaultdict(int)

		comment = comment['body']

		for sentence in sent_tokenize(comment):

			tokens = [word.lower() for word in word_tokenize(sentence) if word not in string.punctuation]

			tags = nltk.pos_tag(tokens)
			
			n_of_lost_words= 0

			for token in tags:

				if token[1][0] == 'N':
					noun = lemmatizer.lemmatize(token[0], 'n')
					nouns_dict[noun] += 1

					list_of_synsets = set([word.synset.name().split('.')[0] for word in list(swn.senti_synsets(noun))])
					for s in list_of_synsets:
						if s in emotions_dict:
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1
						elif s in emotions_parents:
							s = emotions_parents[s]
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1

				if token[1][0] == 'V':
					noun = lemmatizer.lemmatize(token[0], 'v')
					nouns_dict[noun] += 1

					list_of_synsets = set([word.synset.name().split('.')[0] for word in list(swn.senti_synsets(noun))])
					for s in list_of_synsets:
						if s in emotions_dict:
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1
						elif s in emotions_parents:
							s = emotions_parents[s]
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1

				if token[1][0] == 'R':
					noun = lemmatizer.lemmatize(token[0], 'r')
					nouns_dict[noun] += 1

					list_of_synsets = set([word.synset.name().split('.')[0] for word in list(swn.senti_synsets(noun))])
					for s in list_of_synsets:
						if s in emotions_dict:
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1
						elif s in emotions_parents:
							s = emotions_parents[s]
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1

				if token[1][0] == 'J':
					noun = lemmatizer.lemmatize(token[0], 'a')
					nouns_dict[noun] += 1

					list_of_synsets = set([word.synset.name().split('.')[0] for word in list(swn.senti_synsets(noun))])
					for s in list_of_synsets:
						if s in emotions_dict:
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1
						elif s in emotions_parents:
							s = emotions_parents[s]
							emotions_dict[s].append(sentence)
							date_with_emotions[date][s] += 1

			sentence_counter += 1
			if sentence_counter % 100 == 0: print sentence_counter

	json.dump(nouns_dict, open('nouns.json', 'w'), indent=4)
	json.dump(emotions_dict, open('emotions_dict.json', 'w'), indent=4)

	pprint.pprint(date_with_emotions)

	output_file = open('data2b.csv', 'w')
	to_write = "date,"
	for word in emotions_dict: to_write += word + ','
	to_write = to_write[:-1]
	output_file.write(to_write + '\n')
	
	for date in sorted(date_with_emotions):
		to_write = date.strftime('%d-%b-%y') + ','

		val_normalize = 0
		for emotion in emotions_dict:
			val_normalize += date_with_emotions[date][emotion]

		for emotion in emotions_dict:

			to_write += str(float(date_with_emotions[date][emotion])/float(val_normalize)) + ','
		to_write = to_write[:-1]
		output_file.write(to_write + '\n')



"""
def sentiwordnet_analysis(start_month, end_month, base_input_path='../partial/worldnews_comments_'):

	lemmatizer = WordNetLemmatizer()

	for i in range(start_month, end_month):	
		input_file = open(base_input_path + str(i) + '_2016.json', 'r')

		for line in input_file:
			comment = json.loads(line)
			comment = re.sub(r"http\S+", '', str(comment['body']), flags=re.MULTILINE)

			tokens = [word.lower() for word in word_tokenize(comment) if word not in string.punctuation]
			
			# THIS NEEDS TO BE TAKEN CARE OF
			for i in range(0, len(tokens)):
				if tokens[i] == 'dont':
					tokens[i] = "don't"
				if tokens[i] == 'arent':
					tokens[i] = "aren't"
				if tokens[i] == "n't":
					tokens[i] = 'not'

			tags = nltk.pos_tag(tokens)
			
			n_of_lost_words= 0

			for token in tags:
				try:
					if token[1][0] == 'N':
						print swn.senti_synset(lemmatizer.lemmatize(token[0], 'n') + '.n' + '.01')
					if token[1][0] == 'V':
						print swn.senti_synset(lemmatizer.lemmatize(token[0], 'v') + '.v' + '.01')
					if token[1][0] == 'R':
						print swn.senti_synset(lemmatizer.lemmatize(token[0], 'r') + '.r' + '.01')
					if token[1][0] == 'J':
						print swn.senti_synset(lemmatizer.lemmatize(token[0], 'a') + '.a' + '.01')
				except: 
					print token[0]
					n_of_lost_words += 1

			print comment
			print tags
			print 'NUMBER OF LOST WORDS: ' + str(n_of_lost_words)
			
			break
		break
"""
def vader_sentiment_analysis(start_month, end_month, granularity=7, base_input_path='../partial/worldnews_comments_', output_path='tmp.tsv'):
	# Cycles through all the specified months, performs vader sentiment analysis on each comment body, stores them in three dicts

	positive_dict_by_day = defaultdict(float)
	negative_dict_by_day = defaultdict(float)
	number_of_relevant_comments = defaultdict(int)
	output_file = open(output_path, 'w')
	sid = SentimentIntensityAnalyzer()

	for i in range(start_month, end_month):	
		input_file = open(base_input_path + str(i) + '_2016.json', 'r')

		for line in input_file:
			comment = json.loads(line)

			date = datetime.fromtimestamp(float(comment['created_utc'])).replace(hour=0, minute=0, second=0, microsecond=0)
			date = date.replace(day=int( clamp(round(date.day/granularity)*granularity, 1, 31))) # group days by week - not sure about this

			number_of_relevant_comments[date] += 1

			# vader sentiment analysis on each comment body
			ss = sid.polarity_scores(comment['body'])
			# store the resulting values in the correct dictionary
			for k in sorted(ss): 
				if k=='neg': negative_dict_by_day[date] += ss[k]
				if k=='pos': positive_dict_by_day[date] += ss[k]

	# store in a tsv file 
	output_file.write( 'date\tclose\n' )
	for entry in sorted(number_of_relevant_comments):
		# print the average negativity by day
		output_file.write( entry.strftime('%d-%b-%y') + '\t' + \
			str(-(negative_dict_by_day[entry]+positive_dict_by_day[entry]) / float(number_of_relevant_comments[entry]))+'\n')

#vader_sentiment_analysis(12, 13)
sentiwordnet_analysis(1, 13)

#model = ontospy.Ontospy("../NIL_ontoEmotion/emotions_v11.owl")
#print model.getClass('http://nil.fdi.ucm.es/projects/emotions/onto/emotions_v11.owl#Emotion').children()






    