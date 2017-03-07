from nltk.corpus import stopwords
from nltk.corpus import movie_reviews
from nltk.stem import *
import pprint
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.classify import MaxentClassifier
import nltk
import string
import json
import numpy as np
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def word_feats(words):
    return dict([(word, True) for word in words])

def retrieve_comment_list_aux(comment_list, working_list):
	for reply in working_list:
		reply['body'] = re.sub(r'^https?:\/\/.*[\r\n]*', '', reply['body'], flags=re.MULTILINE)
		comment_list.append(reply['body'])
		if 'replies' in reply.keys():
			retrieve_comment_list_aux(comment_list, reply['replies'])

# genera la lista piatta dei commenti a partire dal dizionario dei commenti in input
def retrieve_comment_list():
	comment_list = []
	for comment in input_dict['comments']:
		if comment['body'] == '[deleted]': continue
		comment['body'] = re.sub(r'^https?:\/\/.*[\r\n]*', '', comment['body'], flags=re.MULTILINE)
		comment_list.append(comment['body'])
		if 'replies' in comment.keys():
			retrieve_comment_list_aux(comment_list, comment['replies'])

	return comment_list

input_dict = json.load(open('./single_threads/2ljk71.json', 'r'))
comment_list = retrieve_comment_list()
print len(comment_list)


"""
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
classifier.show_most_informative_features()

#sent="I finished it last night! I'm glad I read it, but I never want to read it again. I wasn't put off by the lack of plot, but the middle chapters are very uneven. Some are fascinating and well-written and deep; some offered me nothing and I hated them. The buddy movie of the first 150 pages is top-notch and I read that in like two days. Ahab's soliloquies are fucking amazing. The chapter on the color white is astonishing.I can see why it's a classic and I can see why people read it and will continue to do so. But I think it's far more uneven than it gets credit for."
sent = "WORTHLESS PRETENTIOUS TRASH"

for sent in comment_list:
	test_sentence = sent.lower()
	#print word_tokenize(test_sentence)
	test_sent_features = {}
	for i in word_tokenize(test_sentence):
		if i in stopwords.words('english'): continue
		if i in movie_reviews.words():
			test_sent_features[i] = True
			#print i
			#print 'neg: ' +  str(classifier.prob_classify({i: True}).prob('neg'))
			#print 'pos: ' +  str(classifier.prob_classify({i: True}).prob('pos'))
		else: test_sent_features[i] = False
	#test_sent_features = {i:(i in word_tokenize(test_sentence.lower())) for i in movie_reviews.words()}
	print test_sent_features
	print 'neg: ' +  str(classifier.prob_classify(test_sent_features).prob('neg'))
	print 'pos: ' +  str(classifier.prob_classify(test_sent_features).prob('pos'))
"""

pos_dict = {}
neg_dict = {}
for i in np.arange(0.0, 1.1, 0.1):
	pos_dict[str(i)] = []
	neg_dict[str(i)] = []
neg_dict['1.0'] = []


sentences = comment_list
for sentence in sentences:
	#print sentence
	sid = SentimentIntensityAnalyzer()
	ss = sid.polarity_scores(sentence)
	for k in sorted(ss):
		#print('{0}: {1}, '.format(k, ss[k]))
		if k == 'pos' and ss['pos']>ss['neg']: pos_dict[str(round(ss[k]*10)/10)].append(sentence)
		if k == 'neg' and ss['neg']>ss['pos']: neg_dict[str(round(ss[k]*10)/10)].append(sentence)

output_list = []
avg = 0

print 'neg:'
for i in np.arange(1.0, 0.0, -0.1):
	print str(i) + ": " + str(len(neg_dict[str(i)]))
	output_list.append([i, -len(neg_dict[str(i)])])
	avg+=-len(neg_dict[str(i)])

print 'pos:'
for i in np.arange(0.0, 1.0, 0.1):
	print str(i) + ": " + str(len(pos_dict[str(i)]))
	output_list.append([i,len(pos_dict[str(i)])])
	avg += len(pos_dict[str(i)])

print pos_dict['0.5']
print pos_dict['0.6']
print pos_dict['0.7']

avg/=len(output_list)


print neg_dict['0.8']
print neg_dict['0.7']
print neg_dict['0.6']
print neg_dict['0.5']
print neg_dict['0.4']
print neg_dict['0.3']

print(output_list)
print 'AVG: ' + str(avg)
json.dump(output_list, open('./d3/ghostbusters_reviews.json', 'w'))

