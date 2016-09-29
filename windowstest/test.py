import praw
import pprint
import time
import nltk
from nltk.corpus import stopwords
from nltk.corpus import movie_reviews
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from string import punctuation
from nltk.tokenize import sent_tokenize,word_tokenize
from collections import defaultdict
from heapq import nlargest
from nltk.probability import FreqDist
from nltk.stem.snowball import SnowballStemmer
import math

def compute_summary(text, n):
	removable_words = set(stopwords.words('english') + list(punctuation))

	sents = sent_tokenize(text)

	#assert n <= len(sents)

	word_sent = [word_tokenize(s.lower()) for s in sents]

	freq = defaultdict(int)
	for s in word_sent:
		for word in s:
			if word not in removable_words:
				freq[word] += 1

	m = float(max(freq.values()))

	for w in freq.keys():
		freq[w] = freq[w]/m
		if freq[w] >= 0.9 or freq[w] <= 0.1:
			del freq[w]

	pprint.pprint(freq)

	ranking = defaultdict(int)

	for i,sent in enumerate(word_sent):
		for w in sent:
			if w in freq:
				ranking[i] += freq[w]

	pprint.pprint(ranking)
	sents_idx = nlargest(n, ranking, key=ranking.get)  
	return [sents[j] for j in sents_idx]

def word_feats(words):
    return dict([(word, True) for word in words])

def classify_with_naive_bayes():

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

def k_means(comments_list, cluster_number):

	stemmer = SnowballStemmer("english", ignore_stopwords=True)
	
	removable_words = set(stopwords.words('english') + list(punctuation) + list('http'))

	words_clean = []
	word_in_docs_count = defaultdict(int)

	for comment in comments_list:
		for sentence in nltk.tokenize.sent_tokenize(comment.body.encode(errors='ignore')):
			for word in nltk.tokenize.word_tokenize(sentence):
				if word.lower() not in removable_words:
					words_clean.append(stemmer.stem(word.lower()))
					word_in_docs_count[stemmer.stem(word.lower())] += 1

	frequencies = FreqDist(words_clean)

	max_frequency = frequencies.most_common(1)[0][1]
	tf = defaultdict(float)
	for freq in frequencies:
		tf[freq] = 0.5 + 0.5*float(frequencies[freq])/float(max_frequency)

	tfidf = defaultdict(float)

	for word in words_clean:
		tfidf[word] = tf[word]*math.log(float(len(comments_list))/float(word_in_docs_count[word]))

	#pprint.pprint(frequencies.most_common(50))
	pprint.pprint(tfidf)

    
	

r = praw.Reddit("heyy")
subreddit = r.get_subreddit('worldnews')
start_time = time.time()
comments_list = []
#classify_with_naive_bayes()

for submission in subreddit.get_hot(limit=1):
	#pprint.pprint(vars(submission))
	
	#uncomment this line only when you want the final result
	#submission.replace_more_comments(limit=2, threshold=0)

	number_of_comments = 0
	
	for comment in praw.helpers.flatten_tree(submission.comments):
		#print vars(comment)

		#you should really solve the MoreComments problem
		if not hasattr(comment, 'score'): continue

		#print "votes: " + str(comment.score)
		#print comment.body.encode(errors='ignore')
		comments_list.append(comment)
		
		#print "///RIASSUNTO:"
		#for s in compute_summary(comment.body, 2):
		#	print '*',s.encode(errors='ignore')
		#print '//////////////'
		number_of_comments += 1
	k_means(comments_list, 10)

print "comments processed: " + str(number_of_comments)
print "elapsed time: " + str(time.time() - start_time)

