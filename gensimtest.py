import praw
import pprint
import time
import json
from collections import defaultdict
import logging
import string
import nltk
from gensim import corpora, models, similarities
from gensim.models import Phrases
from nltk.corpus import stopwords
from nltk.corpus import movie_reviews
from nltk.stem import *
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
from itertools import chain
from gensim.summarization import summarize, keywords
import os
from gensim.models.phrases import Phraser

class CommentStream():

	#def __init__(self, yo):
	#	self.yo = yo


	def __iter__(self):
		for line in open('all_sentences.txt'):
			if len(line)>3:
				yield line.decode('utf-8', errors='ignore')


def load_a_bunch_of_comments(subreddit):
	input_file = open('./tmp_data/' + subreddit + '.json', 'r')
	output_dict = json.load(input_file)
	return output_dict

def fetch_comments_from_dict(sentences, bigram, working_list):
	for comment in working_list:
		words = nltk.word_tokenize(comment['body'])
		words = [word.lower() for word in words if word.isalpha()]
		#words = [word for word in words if word not in stopwords.words('english')]
		sentences.append(words)
		bigram.add_vocab([words])
		if('replies' in comment.keys()):
			fetch_comments_from_dict(sentences, bigram, comment['replies'])

def fetch_sentences(subreddit):
	sentences = []
	bigram = Phrases()
	working_dict = load_a_bunch_of_comments(subreddit)
	for item in working_dict:
		fetch_comments_from_dict(sentences, bigram, working_dict[item]['comments'])
	#return sentences

	bigram_model = models.Word2Vec(bigram[sentences], size=300)
	print len(sentences)
	return bigram_model

def word_feats(words):
    return dict([(word, True) for word in words])

def comment_sentiment_analysis():
	negids = movie_reviews.fileids('neg')
	posids = movie_reviews.fileids('pos')
	 
	negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
	posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
	 
	negcutoff = len(negfeats)*3/4
	poscutoff = len(posfeats)*3/4
	 
	trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
	testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
	print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
	 
	classifier = NaiveBayesClassifier.train(trainfeats)
	print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
	#classifier.show_most_informative_features()

	test_sentence = "This is horrible"
	#print word_tokenize(test_sentence)
	test_sent_features = {}
	for i in word_tokenize(test_sentence):
		if i in stopwords.words('english'): continue
		if i in movie_reviews.words():
			test_sent_features[i] = True
		else: test_sent_features[i] = False
	#test_sent_features = {i:(i in word_tokenize(test_sentence.lower())) for i in movie_reviews.words()}
	print test_sent_features
	print classifier.classify(test_sent_features)


def summarize_text():
	working_dict = load_a_bunch_of_comments('news')
	for item in working_dict:
		text = ""
		print working_dict[item]['title'].upper()
		for comment in working_dict[item]['comments']:
			text += comment['body'] + ""
		#print text
		print "****"
		try:
			print summarize(text, word_count=50)
			print keywords(text)
		except:
			print "ERROR"
		print '\n\n\n'
	#print text
	#print '****'
	#print summarize(text)

#def flatten_comments(submission):
#	result = []


def extract_keywords():
	working_dict = load_a_bunch_of_comments('gadgets')
	result_dict = {}
	stemmer = SnowballStemmer("english")
	for item in working_dict:
		#print working_dict[item]['title']
		for word in working_dict[item]['title'].lower().split():	
			if word not in stopwords.words('english'):
				word = stemmer.stem(word)
				#print word,
				if word not in result_dict:
					result_dict[word] = defaultdict(int)
				for word2 in working_dict[item]['title'].lower().split():
					if word2 not in stopwords.words('english'):
						word2 = stemmer.stem(word2)
						result_dict[word][word2] +=1

		for comment in working_dict[item]['comments']:
			print comment['body']
			if len(comment['body'].split())>5:
				try:
					print keywords(comment['body'])
				except:
					print 'EWW'
			print '*******\n*******\n'
		

	"""
	for item in result_dict:
		print item.upper()
		pprint.pprint(result_dict[item])
	"""
		#print '\n'
		#print keywords(working_dict[item]['title'], )
		#print len(keywords(working_dict[item]['title']))
		#for comment in working_dict[item]['comments']:


def retrieve_all_replies(working_list, file_to_write):
	for comment in working_list:
		file_to_write.write(comment['body'].replace('\n',' ').encode('utf-8', errors='ignore'))
		if('replies' in comment.keys()):
			retrieve_all_replies(comment['replies'], file_to_write)

def all_sentences_to_file():
	start_time = time.time()

	output_file = open('all_sentences.txt', 'w')

	for filename in os.listdir('./tmp_data/'):
		input_file = open('./tmp_data/' + filename, 'r')
		input_dict = json.load(input_file)
		
		for item in input_dict:

			output_file.write(input_dict[item]['title'].encode('utf-8', errors='ignore'))
			output_file.write(input_dict[item]['selftext'].replace('\n',' ').encode('utf-8', errors='ignore'))


			retrieve_all_replies(input_dict[item]['comments'], output_file)

			output_file.write('\n')

	print 'time: ' + str(time.time()-start_time)




def train_model_complete():
	
	start_time = time.time()
	count = 0

	corpora_iterable = CommentStream()

	bigram = Phrases()

	bigram_model = models.Word2Vec(corpora_iterable, size=50)
	#bigram_model.build_vocab(bigram[corpora_iterable])
	#bigram_model.build_vocab(corpora_iterable)

	#print time.time() - start_time

	#bigram_model.train(bigram[corpora_iterable])
	#bigram_model.train(corpora_iterable)
	
	"""
	for filename in os.listdir('./tmp_data/'):
		sentences = []
		bigram = Phrases()
		
		subreddit = filename.split('.')[0]

		print str(count) + ' learning from ' + filename

		working_dict = load_a_bunch_of_comments(subreddit)

		for item in working_dict:
			fetch_comments_from_dict(sentences, bigram, working_dict[item]['comments'])

		bigram = Phraser(bigram)

		if count==0: bigram_model.build_vocab(bigram[sentences])
		bigram_model.train(bigram[sentences])

		count += 1
		if count==10: break
	"""

	#bigram_model = models.Word2Vec(bigram[sentences], size=300)
	bigram_model.save('testmodel')
	#print len(sentences)
	print 'time: ' + str(time.time()-start_time)
	return bigram_model



#all_sentences_to_file()

#summarize_text()
#comment_sentiment_analysis()
#train_model_complete()

#stream = CommentStream('ciao')
#for item in stream:
#	print item
