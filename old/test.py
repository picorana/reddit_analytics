import praw
import pprint
from pattern.en     import parsetree
from pattern.search import search
from pattern.graph  import Graph
from pattern.web    import plaintext

r = praw.Reddit('tralala')
g = Graph()

#r.login()

subreddit = r.get_subreddit('worldnews')

for submission in subreddit.get_hot(limit=1):
#	pprint.pprint(vars(submission))

	flat_comments = praw.helpers.flatten_tree(submission.comments)
	numcomments = 0
	for comment in flat_comments:
		#pprint.pprint(vars(comment))
		if hasattr(comment, 'body'): 
			print comment.body
			s = comment.body.lower().encode('ascii', 'ignore')
			s = plaintext(s)
        	s = parsetree(str(s))
        	p = '{NP} {JJ}'
        	for m in search(p, s):
	            x = m.group(1).string # NP left
	            y = m.group(2).string # NP right
	            if x not in g:
	                g.add_node(x)
	            if y not in g:
	                g.add_node(y)
	            g.add_edge(g[x], g[y], stroke=(0,0,0,0.75))
		
		numcomments+=1

	print "analyzed comments: " + str(numcomments)

g = g.split()[0] # Largest subgraph.

for n in g.sorted()[:40]: # Sort by Node.weight.
    n.fill = (0, 0.5, 1, 0.75 * n.weight)
 
g.export('test', directed=True, weighted=0.6)