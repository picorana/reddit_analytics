import logging
import itertools
import numpy as np
import gensim
from gensim.utils import smart_open, simple_preprocess
from gensim.corpora.wikicorpus import _extract_pages, filter_wiki
from gensim.parsing.preprocessing import STOPWORDS
import gensim.corpora

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO  # ipython sometimes messes up the logging setup; restore

def tokenize(text):
    return [token for token in simple_preprocess(text) if token not in STOPWORDS]

def iter_wiki(dump_file):
    """Yield each article from the Wikipedia dump, as a `(title, tokens)` 2-tuple."""
    ignore_namespaces = 'Wikipedia Category File Portal Template MediaWiki User Help Book Draft'.split()
    for title, text, pageid in _extract_pages(smart_open(dump_file)):
        text = filter_wiki(text)
        tokens = tokenize(text)
        if len(tokens) < 50 or any(title.startswith(ns + ':') for ns in ignore_namespaces):
            continue  # ignore short articles and various meta-articles
        yield title, tokens

class WikiCorpus(object):
    def __init__(self, dump_file, dictionary, clip_docs=None):
        """
        Parse the first `clip_docs` Wikipedia documents from file `dump_file`.
        Yield each document in turn, as a list of tokens (unicode strings).
        
        """
        self.dump_file = dump_file
        self.dictionary = dictionary
        self.clip_docs = clip_docs
    
    def __iter__(self):
        self.titles = []
        for title, tokens in itertools.islice(iter_wiki(self.dump_file), self.clip_docs):
            self.titles.append(title)
            yield self.dictionary.doc2bow(tokens)
    
    def __len__(self):
        return self.clip_docs

"""
# only use simplewiki in this tutorial (fewer documents)
# the full wiki dump is exactly the same format, but larger
stream = iter_wiki('simplewiki-latest-pages-articles.xml.bz2')
for title, tokens in itertools.islice(iter_wiki('simplewiki-latest-pages-articles.xml.bz2'), 8):
    print title, tokens[:10]  # print the article title and its first ten tokens

doc_stream = (tokens for _, tokens in iter_wiki('simplewiki-latest-pages-articles.xml.bz2'))

id2word_wiki = gensim.corpora.Dictionary(doc_stream)
print(id2word_wiki)

# ignore words that appear in less than 20 documents or more than 10% documents
id2word_wiki.filter_extremes(no_below=20, no_above=0.1)
print(id2word_wiki)


wiki_corpus = WikiCorpus('simplewiki-latest-pages-articles.xml.bz2', id2word_wiki)
gensim.corpora.MmCorpus.serialize('wiki_bow.mm', wiki_corpus)

mm_corpus = gensim.corpora.MmCorpus('wiki_bow.mm')

clipped_corpus = gensim.utils.ClippedCorpus(mm_corpus, 4000)  # use fewer documents during training, LDA is slow
# ClippedCorpus new in gensim 0.10.1
# copy&paste it from https://github.com/piskvorky/gensim/blob/0.10.1/gensim/utils.py#L467 if necessary (or upgrade your gensim)
lda_model = gensim.models.LdaModel(clipped_corpus, num_topics=10, id2word=id2word_wiki, passes=4)

#tfidf_model = gensim.models.TfidfModel(mm_corpus, id2word=id2word_wiki)

#lsi_model = gensim.models.LsiModel(tfidf_model[mm_corpus], id2word=id2word_wiki, num_topics=200)

#gensim.corpora.MmCorpus.serialize('./data/wiki_tfidf.mm', tfidf_model[mm_corpus])
#gensim.corpora.MmCorpus.serialize('./data/wiki_lsa.mm', lsi_model[tfidf_model[mm_corpus]])

#lda_model.save('./data/lda_wiki.model')
#lsi_model.save('./data/lsi_wiki.model')
#tfidf_model.save('./data/tfidf_wiki.model')
id2word_wiki.save('./data/wiki.dictionary')
"""
lda_model = gensim.models.LdaModel.load('./data/lda_wiki.model')
lda_model.print_topics()

id2word_wiki = gensim.corpora.Dictionary.load('./data/wiki.dictionary')
query2 = "Oh damn that looked pretty sick, the sea battles there looked really batshit crazy. Also just realized we're probably going to see a 4 way battle with the Black Pearl, Salazar's ship, Queen Anne's Revenge, and the Flying Dutchman. I NEED THIS NOW."
query = "So, I've been struggling with my health for the last three years. It's taken a real toll on my life, as well as my husband's. My mom...never really took me seriously. She and I have a decent relationship, but she has a long history of telling me I'm fine and being dramatic, only to find out, kidney stones, ruptured gallbladder, etc. She can also be a bit sensitive, and has a knack for taking things out of context, and blowing them up. All of that being said, she is a kind woman, and would do absolutely anything for me. We have a good relationship, but live 8 hours apart, so only see each other a few times a year."
doc_bowed = id2word_wiki.doc2bow(tokenize(query2))
print lda_model[doc_bowed]