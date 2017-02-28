# Reddit Clusters

A tool for visualizing relationships between subreddits.

This program uses a dictionary of which users posted in which subreddit to build a similarity matrix and tries to cluster the subreddits in a tree-like structure, in which each node contains similar subreddits.

In order to fill the tree, K-means clustering algorithm is used recursively, first on the whole group of subreddits, then on any one of the clusters that exceeds a fixed amount of items.

The results are then visualized using [d3.js](https://d3js.org/) and can be found [here](https://picorana.github.io/subreddit_recommender/graph2.html).

Data about which users posted in which subreddit is temporarily stored into the 'partial' folder and currently contains only data from October, November and December 2016.


