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


def sentiwordnet_analysis(start_month, end_month, base_input_path='../partial/worldnews_comments_'):

	lemmatizer = WordNetLemmatizer()
	model = ontospy.Ontospy("../NIL_ontoEmotion/emotions_v11.owl")

	nouns_dict = defaultdict(int)
	emotions_dict = {}

	for emotion_class in model.classes:
		emotions_dict[emotion_class.bestLabel().lower()] = []

	sentence_counter = 0

	for comment in iter_comment_bodies(start_month, end_month):	

		for sentence in sent_tokenize(comment):

			tokens = [word.lower() for word in word_tokenize(sentence) if word not in string.punctuation]
			
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
				if token[1][0] == 'N':
					noun = lemmatizer.lemmatize(token[0], 'n')
					nouns_dict[noun] += 1

					list_of_synsets = set([word.synset.name().split('.')[0] for word in list(swn.senti_synsets(noun))])
					for s in list_of_synsets:
						if s in emotions_dict:
							emotions_dict[s].append(sentence)

			"""
			for token in tags:
				try:
					if token[1][0] == 'N':
						noun = lemmatizer.lemmatize(token[0], 'n')
						nouns_dict[noun] += 1
						print noun
						print list(swn.senti_synset(noun + '.n' + '.01'))
						print '*\n\n'
					#if token[1][0] == 'V':
						#print swn.senti_synset(lemmatizer.lemmatize(token[0], 'v') + '.v' + '.01')
					#if token[1][0] == 'R':
						#print swn.senti_synset(lemmatizer.lemmatize(token[0], 'r') + '.r' + '.01')
					#if token[1][0] == 'J':
						#print swn.senti_synset(lemmatizer.lemmatize(token[0], 'a') + '.a' + '.01')
				except: 
					print token[0]
					n_of_lost_words += 1
			"""
			#print sentence
			sentence_counter += 1
			if sentence_counter % 100 == 0: print sentence_counter

	json.dump(nouns_dict, open('nouns.json', 'w'), indent=4)
	json.dump(emotions_dict, open('emotions_dict.json', 'w'), indent=4)


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
sentiwordnet_analysis(1, 10)







    