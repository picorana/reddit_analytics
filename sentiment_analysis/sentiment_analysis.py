import json
import string
import pprint
from datetime import datetime
from collections import defaultdict

from nltk.corpus import stopwords
from nltk.corpus import movie_reviews
from nltk.stem import *
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

positive_dict_by_day = defaultdict(float)
negative_dict_by_day = defaultdict(float)
number_of_relevant_comments = defaultdict(int)
output_file = open('data.tsv', 'w')
sid = SentimentIntensityAnalyzer()

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

for i in range(1, 13):	
	input_file = open('../partial/worldnews_comments_'+str(i)+'_2016.json', 'r')

	for line in input_file:
		comment = json.loads(line)
		date = datetime.fromtimestamp(float(comment['created_utc'])).replace(hour=0, minute=0, second=0, microsecond=0)
		date = date.replace(day=int( clamp(round(date.day/7)*7, 1, 31)))
		"""
		if 1<=date.day<7: date.replace(day=1)
		if 7<=date.day<14: date.replace(day=7)
		if 14<=date.day<21: date.replace(day=14)
		if 21<=date.day<28: date.replace(day=21)
		if 28<=date.day<32: date.replace(day=28)
		"""
		number_of_relevant_comments[date] += 1
		#print comment['body']
		ss = sid.polarity_scores(comment['body'])
		for k in sorted(ss): 
			#print k, ':', ss[k]
			if k=='neg': negative_dict_by_day[date] += ss[k]
			if k=='pos': positive_dict_by_day[date] += ss[k]

#for entry in number_of_relevant_comments:
#	print entry, number_of_relevant_comments[entry], negative_dict_by_day[entry]/float(number_of_relevant_comments[entry]), positive_dict_by_day[entry]/float(number_of_relevant_comments[entry])

output_file.write('date\tclose\n')
for entry in sorted(number_of_relevant_comments):
	output_file.write(entry.strftime('%d-%b-%y')+'\t' + str(-(negative_dict_by_day[entry]+positive_dict_by_day[entry])/float(number_of_relevant_comments[entry]))+'\n')

	