import json
import pprint
import itertools
from collections import defaultdict
import numpy as np
import random
from gensim.utils import smart_open, simple_preprocess
from gensim.corpora.wikicorpus import _extract_pages, filter_wiki
from gensim.parsing.preprocessing import STOPWORDS
from gensim import similarities, models
import gensim.corpora
import logging
import re
from gensim.summarization import summarize
from gensim.summarization import keywords
from nltk.stem.porter import *

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

# questa funzione serve solo nel disegno del grafo per d3
# non aggiunge altre info al modello di gensim
def append_replies(comment_list, data_dict, working_list, prev_node, score):
	for reply in working_list:
		if reply['body'] == '[deleted]': continue
		reply['body'] = re.sub(r'^https?:\/\/.*[\r\n]*', '', reply['body'], flags=re.MULTILINE)
		comment_list.append(reply['body'])
		reply_dict = {}
		link_dict = {}
		reply_dict['id'] = reply['body']
		reply_dict['score'] = score
		reply_dict['num_node'] = comment_list.index(reply['body'])
		data_dict['nodes'].append(reply_dict)
		link_dict['source'] = prev_node['num_node']
		link_dict['target'] = reply_dict['num_node']
		data_dict['links'].append(link_dict)
		if 'replies' in reply.keys():
			append_replies(comment_list, data_dict, reply['replies'], reply_dict, score-0.1)

# disegna il grafo in json per d3
def create_graph(topic_dict):
	data_dict = {}
	data_dict['graph'] = []
	data_dict['links'] = []
	data_dict['nodes'] = []

	comment_list = []

	count = 0
	for comment in input_dict['comments']:
		if comment['body'] == '[deleted]': continue
		comment['body'] = re.sub(r'^https?:\/\/.*[\r\n]*', '', comment['body'], flags=re.MULTILINE)
		comment_list.append(comment['body'])
		node_dict = {}
		node_dict['id'] = comment['body']
		node_dict['type'] = 'circle'
		node_dict['size'] = comment['ups']/100
		node_dict['score'] = 1
		node_dict['num_node'] = comment_list.index(comment['body'])
		data_dict['nodes'].append(node_dict)
		if 'replies' in comment.keys():
			append_replies(comment_list, data_dict, comment['replies'], node_dict, node_dict['score']-0.1)

		count += 1
		#if count == 50: break
	"""
	for topic in topic_dict:
		for comment in topic_dict[topic]:
			for comment2 in topic_dict[topic]:
				if comment == comment2: continue
				link_dict = {}
				if comment not in comment_list or comment2 not in comment_list: continue
				link_dict['source'] = comment_list.index(comment)
				link_dict['target'] = comment_list.index(comment2)
				data_dict['links'].append(link_dict)
	"""
	json.dump(data_dict, output_file, indent=4)

	return comment_list

def create_standard_force_directed_graph_aux(data_dict, working_list, prev_node, topic_dict, lsi_model, link_into_topic=False):
	
	for reply in working_list:
		if reply['body'] == '[deleted]': continue
		reply_dict = {}
		link_dict = {}
		reply_dict['id'] = reply['id']
		reply_dict['body'] = reply['body']
		reply_dict['size'] = reply['ups']

		doc_bowed = id2word.doc2bow(tokenize(reply['body']))
		best_topic = 199 
		best_score = 0
		for result in lsi_model[doc_bowed]:
			if result[1] >= best_score:
				best_topic = result[0]
				best_score = result[1]
		reply_dict['group'] = best_topic

		data_dict['nodes'].append(reply_dict)
		link_dict['source'] = prev_node['id']
		link_dict['target'] = reply_dict['id']
		data_dict['links'].append(link_dict)

		doc_bowed = id2word.doc2bow(tokenize(reply['body']))
		best_topic = 199 
		best_score = 0
		for result in lsi_model[doc_bowed]:
			if result[1] >= best_score:
				best_topic = result[0]
				best_score = result[1]
		reply_dict['group'] = best_topic

		if link_into_topic:
			if best_topic in topic_dict.keys():
				for othernode in topic_dict[best_topic]:
					link_dict = {}
					link_dict['source'] = reply_dict['id']
					link_dict['target'] = othernode['id']
					data_dict['links'].append(link_dict)
		
		
		if best_topic in topic_dict.keys():
			topic_dict[best_topic].append(reply_dict)
		else:
			topic_dict[best_topic] = []
			topic_dict[best_topic].append(reply_dict)

		if 'replies' in reply.keys():
			create_standard_force_directed_graph_aux(data_dict, reply['replies'], reply_dict, topic_dict, lsi_model)



def create_standard_force_directed_graph(lsi_model, id2word, link_into_topic=True):
	data_dict = {}

	topic_dict = {}

	data_dict['links'] = []
	data_dict['nodes'] = []
	data_dict['submission_title'] = [input_dict['title']]

	for comment in input_dict['comments']:
		if comment['body'] == '[deleted]': continue
		node_dict = {}
		node_dict['id'] = comment['id']
		node_dict['body'] = comment['body']
		node_dict['size'] = comment['ups']
		data_dict['nodes'].append(node_dict)
		#try: node_dict['keywords'] = keywords(comment['body'])
		#except: print node_dict['body'] 

		doc_bowed = id2word.doc2bow(tokenize(comment['body']))
		best_topic = 201 
		best_score = 0
		for result in lsi_model[doc_bowed]:
			if result[1] >= best_score:
				best_topic = result[0]
				best_score = result[1]
		node_dict['group'] = best_topic
		
		if link_into_topic:
			if best_topic in topic_dict.keys():
				for othernode in topic_dict[best_topic]:
					link_dict = {}
					link_dict['source'] = node_dict['id']
					link_dict['target'] = othernode['id']
					data_dict['links'].append(link_dict)
		
		if best_topic in topic_dict.keys():
			topic_dict[best_topic].append(node_dict)
		else:
			topic_dict[best_topic] = []
			topic_dict[best_topic].append(node_dict)
		
		
		if 'replies' in comment.keys():
			create_standard_force_directed_graph_aux(data_dict, comment['replies'], node_dict, topic_dict, lsi_model)

	return data_dict
	#json.dump(data_dict, output_file, indent=4)


def tokenize(text):
	text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
	MORESTOPWORDS = ['www', 'http', 'com', 'https', 'imgur', '[deleted]']
	return [token for token in simple_preprocess(text) if (token not in STOPWORDS and token not in MORESTOPWORDS)]


def generate_topics(comment_list, num_topics):
	
	comment_list_tokenized = []
	for comment in comment_list:
		comment_list_tokenized.append(tokenize(comment))

	id2word = gensim.corpora.Dictionary(comment_list_tokenized)
	print(id2word)

	bowed_comments = []
	for comment in comment_list_tokenized:
		bowed_comments.append(id2word.doc2bow(comment))

	lda_model = gensim.models.LdaModel(bowed_comments, num_topics=num_topics, id2word=id2word, passes=16)
	lda_model.print_topics()

	topic_dict = {}
	for i in range(num_topics+1):
		topic_dict[i] = []
	for comment in comment_list:
		doc_bowed = id2word.doc2bow(tokenize(comment))
		best_topic = num_topics + 1
		best_score = 0
		for result in lda_model[doc_bowed]:
			if result[1] >= best_score:
				best_topic = result[0]
				best_score = result[1]
		topic_dict[best_topic].append(comment)

	
	for topic in topic_dict:
		tmp_string = ""
		for comment in topic_dict[topic]:
			tmp_string += comment.replace('\n', ' ') + '\n'
		print summarize(tmp_string, word_count = 50)
		try:
			print lda_model.print_topic(topic, topn=10) 
			print keywords(tmp_string)
		except: continue
		print '\n\n\n'
	
	json.dump(topic_dict, open('tmp2.json', 'w'), indent=4)

	return topic_dict

def lsi_test(comment_list):

	comment_list_tokenized = []
	for comment in comment_list:
		comment_list_tokenized.append(tokenize(comment))

	bigram = models.Phrases(comment_list_tokenized)
	comment_list_tokenized = bigram[comment_list_tokenized]

	id2word = gensim.corpora.Dictionary(comment_list_tokenized)
	print(id2word)

	bowed_comments = []
	for comment in comment_list_tokenized:
		bowed_comments.append(id2word.doc2bow(comment))

	tfidf_model = gensim.models.TfidfModel(bowed_comments, id2word=id2word)

	corpus = tfidf_model[bowed_comments]

	lsi_model = gensim.models.LsiModel(corpus, id2word=id2word, num_topics=500)
	#lsi_model.print_topics(num_topics=-1)

	topic_dict = {}
	for i in range(600):
		topic_dict[i] = []


	for comment in comment_list:
		doc_bowed = id2word.doc2bow(tokenize(comment))
		best_topic = 199 
		best_score = 0
		for result in lsi_model[doc_bowed]:
			if result[1] >= best_score:
				best_topic = result[0]
				best_score = result[1]
		topic_dict[best_topic].append(comment)



	"""

	for topic in topic_dict:
		tmp_string = ""
		for comment in topic_dict[topic]:
			tmp_string += comment.replace('\n', ' ') + '\n'

		try:
			print summarize(tmp_string, word_count = 50)
			print lsi_model.print_topic(topic, topn=10) 
			print keywords(tmp_string)
		except: continue
		
		print '\n\n\n'
		"""

	json.dump(topic_dict, open('tmp.json', 'w'), indent=4)
	

	return lsi_model, id2word, topic_dict, corpus

def refine_data_dict(data_dict, lsi_model, id2word, comment_list, corpus, topic_dict, add_topic_nodes=True, min_threshold=0.4, max_threshold=0.7):

	print 'starting nodes len: ' + str(len(data_dict['nodes']))
	print 'starting links len: ' + str(len(data_dict['links']))
	
	nodes_to_remove = []
	links_to_remove = []
	for node in data_dict['nodes']:
		for node2 in data_dict['nodes']:
			if node == node2: continue
			if node['body'] == node2['body']:
				nodes_to_remove.append(node2)
				if 'merged' in node.keys():
					node['merged'] += 1
				else: node['merged'] = 1
				node['size'] += node2['size']

				for link in data_dict['links']:
					if link['source'] == node2['id']:
						links_to_remove.append(link)
					if link['target'] == node2['id']:
						links_to_remove.append(link)


	for node in nodes_to_remove:
		if node in data_dict['nodes']:
			data_dict['nodes'].remove(node)
	for link in links_to_remove:
		if link in data_dict['links']:
			data_dict['links'].remove(link)
	
	count = 0
	nodes_to_remove = []
	links_to_remove = []

	print 'med nodes len: ' + str(len(data_dict['nodes']))
	print 'med links len: ' + str(len(data_dict['links']))

	index = similarities.MatrixSimilarity(lsi_model[corpus])

	for node in data_dict['nodes']:

		doc_bowed = id2word.doc2bow(tokenize(node['body']))
		vec_lsi = lsi_model[doc_bowed]

		sims = index[vec_lsi]
		sims = sorted(enumerate(sims), key=lambda item: -item[1])

		for values in sims:

			if values[1] > max_threshold:
				for node2 in data_dict['nodes']:
					if node == node2: continue
					elif node2['body'] == comment_list[values[0]]:
						nodes_to_remove.append(node2)
						if 'merged' in node.keys():
							node['merged'] += 1
						else: node['merged'] = 1
						node['size'] += node2['size']

						for link in data_dict['links']:
							if link['source'] == node2['id']:
								links_to_remove.append(link)
							if link['target'] == node2['id']:
								links_to_remove.append(link)
			
			if values[1] > min_threshold and values[1] <= max_threshold:
				for node2 in data_dict['nodes']:
					if node == node2: continue
					elif node2['body'] == comment_list[values[0]] and node2 not in nodes_to_remove and node not in nodes_to_remove:
						link1 = {}
						link1['source'] = node['id']
						link1['target'] = node2['id']
						link2 = {}
						link1['source'] = node2['id']
						link1['target'] = node['id']
						if link1 in data_dict['links']:
							link1['value'] = values[1] * 5
						elif link2 in data_dict['links']:
							link2['value'] = values[1] * 5
						else: 
							link1['value'] = values[1] * 5
							data_dict['links'].append(link1)
			
	for node in nodes_to_remove:
		if node in data_dict['nodes']:
			data_dict['nodes'].remove(node)
	for link in links_to_remove:
		if link in data_dict['links']:
			data_dict['links'].remove(link)

	stemmer = PorterStemmer()
	if add_topic_nodes:
		for topic in topic_dict:
			if len(topic_dict[topic])<15: continue
			summarization_string = ""
			node_dict = {'type':'topic_node', 'id':topic, 'size':500}
			links_to_append = []
			for string in topic_dict[topic]:
				for node in data_dict['nodes']:
					if node['body'] == string:
						link_dict = {'source': node['id'], 'target':topic, 'value': 1}
						links_to_append.append(link_dict)
				summarization_string += string.encode('utf-8', errors='ignore') + '\n '
			if len(summarization_string) < 10: continue
			#try:
			summarized_string = ""
			#summarized_string = summarize(summarization_string, word_count=10)
			already_found = []
			try:
				keywrds = keywords(summarization_string)
				for word in keywrds.split('\n'):
					if stemmer.stem(word) in already_found: continue
					else: already_found.append(stemmer.stem(word))
					summarized_string += word + ' '
			except: print 'meh'
			node_dict['body'] = summarized_string
			print summarized_string + '\n\n'
			if len(node_dict['body']) > 10:
				data_dict['nodes'].append(node_dict)
				for link in links_to_append:
					data_dict['links'].append(link)
			#except: print 'meh',#print summarization_string

	json.dump(topic_dict, open('topic_dict.json', 'w'), indent=4)

	print 'finishing nodes len: ' + str(len(data_dict['nodes']))
	print 'finishing links len: ' + str(len(data_dict['links']))
	
	return data_dict

def print_topics(topic_dict, lsi_model, id2word):
	
	output_f = open('./d3/topics.csv', 'w')

	first_string = 'Topic,'

	count = 0
	most_significative_words_list = []
	for topic in topic_dict:
		#toprint = 'topic ' + str(count) + ',' 
		if len(topic_dict[topic])<2: continue
		for values in lsi_model.show_topic(topic, topn=3):
			if values[0] not in most_significative_words_list:
				most_significative_words_list.append(values[0])
		count += 1
		if count == 4: break

	for word in most_significative_words_list:
		first_string += word + ','

	output_f.write(first_string[:-1]+'\n')

	count = 0
	towrite = ''
	for topic in topic_dict:
		towrite = 'T' + str(count) + ',' 
		if len(topic_dict[topic])<2: continue
		this_topic_words = []
		this_topic_words_weights = []
		for values in lsi_model.show_topic(topic, topn=3):
			this_topic_words.append(values[0])
			this_topic_words_weights.append(values[1])
		for word in most_significative_words_list:
			if word in this_topic_words:
				towrite += str(abs(this_topic_words_weights[this_topic_words.index(word)]))
				towrite += ','
			else: towrite += '0.0000000001,'
		count += 1
		if count == 4: break
		output_f.write(towrite[:-1] + '\n')

def summarize_topics():
	
	thisdict = json.load(open('./tmp.json', 'r'))
	for topic in thisdict:
		if len(thisdict[topic])<=10: continue
		tosummarize = ""
		for item in thisdict[topic]:
			tosummarize += item + '\n'
			print item.encode('utf-8', errors='ignore')
		print '****'
		try:
			print summarize(tosummarize, ratio=0.1).encode('utf-8', errors='ignore')
			print keywords(tosummarize)
		except:
			print 'ERROR: ' + tosummarize
		print '*****'
		
def transform_for_d3v3(data_dict):
	id_to_index = defaultdict(int)
	index = 0
	
	for node in data_dict['nodes']:
		id_to_index[node['id']] = index
		index += 1

	for link in data_dict['links']:
		link['source'] = id_to_index[link['source']]
		link['target'] = id_to_index[link['target']]
		link['value'] = random.randint(0,10)

	return data_dict





logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO


while True:
	input_dict = json.load(open('./single_threads/5bzjgp.json', 'r'))
	output_file = open('./d3/data.json', 'w')

	comment_list = retrieve_comment_list()
	lsi_model, id2word, topic_dict, corpus = lsi_test(comment_list)

	#topic_dict = generate_topics(retrieve_comment_list(), 8)
	data_dict = create_standard_force_directed_graph(lsi_model, id2word)
	if len(data_dict['links']) > 8000: continue
	data_dict = refine_data_dict(data_dict, lsi_model, id2word, comment_list, corpus, topic_dict, min_threshold=0.7, max_threshold=0.8)

	data_dict = transform_for_d3v3(data_dict)

	json.dump(data_dict, output_file, indent=4)

	#print_topics(topic_dict, lsi_model, id2word)
	if len(data_dict['links']) <=6000: break

#summarize_topics()
