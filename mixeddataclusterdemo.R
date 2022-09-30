## Clustering mixed (continuous and categorical) data demo with my own notes added
## from https://stats.stackexchange.com/a/164694
## September 2022

library(cluster)
library(fpc)

set.seed(3296)
n <- 15
## Continuous data
cont <-  c(rnorm(n, mean=0, sd=1),
           rnorm(n, mean=1, sd=1),
           rnorm(n, mean=2, sd=1) )
## Binary data
bin    <- c(rbinom(n, size=1, prob=.2),
           rbinom(n, size=1, prob=.5),
           rbinom(n, size=1, prob=.8) )
## Ordinal data
ord    <- c(rbinom(n, size=5, prob=.2),
           rbinom(n, size=5, prob=.5),
           rbinom(n, size=5, prob=.8) )
## Combined...
data <- data.frame(cont=cont, bin=bin, ord=factor(ord, ordered=TRUE))

## The Gower's similarity coefficient is a composite measure which takes quantitative,
## binary, and nominal data and computes similarity/distance between individual observations
## with each variable and then averages across each variable.
## So essentially you're computing a distance matrix for the rows in the dataset for each
## variable in turn using a type of distance which is appropriate for variables of that type.
## The final distance is the (possibly weighted) average of distances for each variable.
## "For mixed data, Gower's distance is largely the only game in town"

## Return distance matrix using Gower's distance:
g.dist <- daisy(data, metric="gower", type=list(symm=2))

## PAM: Partition Around Medoids, a.k.a. K-Medoids clustering (analogous to K-means for
## binary data)
pc = pamk(g.dist, krange=1:5, criterion="asw")
pc$pamobject # So 2 clusters for this data, medoids around rows 29 and 33

## Compare these results to the results of hierarchichal clustering:
hc.median <- hclust(g.dist, method="median")
hc.single <- hclust(g.dist, method="single")
hc.complete <- hclust(g.dist, method="complete")
## Plot output of hierarchical clustering, note where 29 and 33 show up in these 
## You identify the number of clusters by cutting across the dendrogram at a certain level
## and observing the number of branches. Example from the famous iris dataset illustrates: 
## https://en.wikipedia.org/wiki/Hierarchical_clustering#/media/File:Iris_dendrogram.png
layout(matrix(1:3, nrow=1))
plot(hc.median) # 2 clusters, possibly 3
plot(hc.single) # 2 clusters
plot(hc.complete) # 3 clusters, possibly 4

## DBSCAN method: Density-based Spatial Clustering of Applications with Noise
## Given a set of points in some space, groups together points that are closely packed
## together / have many neighbours, marking as outliers points which lie alone in low-
## density regions. "DBSCAN is one of the most common clustering algorithms and one of the
## most cited in scientific literature" (https://en.wikipedia.org/wiki/DBSCAN)\

## DBSCAN requires specification of two parameters: eps or reachability distance (how close
## two observations have to be to be linked together) and minPts (the minimum number of points
## that need to be linked for you to consider them a cluster
## Bear in mind that it's probably wise for this linguistics data not to use methods which
## require too many assumptions when using unsupervised learning techniques like clustering,
## I don't want to be just telling the algorithm to produce the results I want to see...

## Approach to choosing params: 
## For minPts, use one more than number of dimensions in the data although
## having a number that's too small isn't recommended
## For eps, see what percentage of the distances are less than a given value by examining
## the distribution of the distances:
layout(matrix(1:2, nrow=1))
plot(density(na.omit(g.dist[upper.tri(g.dist)])), main="kernel density") 
plot(ecdf(g.dist[upper.tri(g.dist)]), main="ecdf")
## ⮑ 2 peaks, "nearer" and "further away".  0.3 is the trough between the peaks, seems to be
## the cleanest division
dbc3 = dbscan(g.dist, eps=.3, MinPts=5, method="dist");  dbc3
