from pattern.web    import Google, plaintext
from pattern.en     import parsetree
from pattern.search import search
from pattern.graph  import Graph
 
g = Graph()
for i in range(50):
    for result in Google().search('"more important than"', start=i+1, count=200):
        s = result.text.lower() 
        s = plaintext(s)
        s = parsetree(s)
        p = '{NP} (VP) more important than {NP}'
        for m in search(p, s):
            x = m.group(1).string # NP left
            y = m.group(2).string # NP right
            if x not in g:
                g.add_node(x)
            if y not in g:
                g.add_node(y)
            g.add_edge(g[x], g[y], stroke=(0,0,0,0.75)) # R,G,B,A
 
#g = g.split()[0] # Largest subgraph.
 
for n in g.sorted()[:40]: # Sort by Node.weight.
    n.fill = (0, 0.5, 1, 0.75 * n.weight)
 
g.export('test', directed=True, weighted=0.6)