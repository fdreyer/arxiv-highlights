# arxiv-highlights

arxiv-highlights is a small python program to crawl through the most
recent arXiv papers of any given subject area, and create a list of
likely interesting submissions.

Simply run 
> ./arxiv-highlights [-n ntop] [-o filename] [-a listings.txt]

This will print out a selection of ntop articles.

Currently, default scoring is based on the total citation count of the 25
most cited papers by a given article's authors.