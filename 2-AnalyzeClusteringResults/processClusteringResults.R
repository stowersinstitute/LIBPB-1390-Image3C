library(pheatmap)
library(edgeR)
library(plyr)
library(ggplot2)
library(stringr)
library(reshape2)
library(pastecs)
library(igraph)
library(RColorBrewer)
library(data.table)

############
#read in table of counts per cluster and get it formatted correctly
###########

#function to get substring counting from the right
substrRight <- function(x, n){
  substr(x, nchar(x)-n+1, nchar(x))
}

mydata <- read.csv(file="GroupStatsPerCluster.csv")
mydata.orig <- mydata
mydata <- mydata[,1:3] 
melted <- melt(mydata, id.vars = c("Cluster", "Term"))
casted <- dcast(melted, Term ~ variable + Cluster)
mydata <- casted
rm(casted)

for(i in c(2:ncol(mydata))) {
  mydata[,i] <- as.numeric(as.character(mydata[,i]))
}

rownames(mydata) <- mydata[,1] #set row names
mydata[,1] <- NULL #remove redundant 1st col
colnames(mydata) <- gsub("Count_", "", colnames(mydata)) #take out some useless text
rownames(mydata) <- gsub("_processed", "", rownames(mydata)) #same

#spanning tree############

mstdata.orig <- read.csv(file = "ClusterFeatureAverages.csv") #from copy/paste aggregated data from vortex
vertexColors <- str_match_all(mstdata.orig$Color, "[0-9]{1,3}") #extract RGB values for cluster colors
vertexColors <- sapply(vertexColors, function(x) #convert to hex
  rgb(x[1], x[2], x[3], maxColorValue=255))


mstdata <- mstdata.orig[,-c(1,3,4,5)] #keep only cluster IDs and feature avg values
rownames(mstdata) <- mstdata$ClusterID
mstdata$ClusterID <- NULL

for(i in c(2:ncol(mstdata))) {
  mstdata[,i] <- as.numeric(as.character(mstdata[,i]))
}

mstmatrix <- as.matrix(mstdata)
#if not clustering on all params, need to scale params not used for clustering
plot(colMeans(mstmatrix), ylim = c(-10,10)) #all values should be near 0, very near
mstmatrix <- scale(mstmatrix[,c(10:27)])
plot(colMeans(mstmatrix))
pheatmap(mstdata, scale = "column") #have a look this way
mydist <- dist(mstmatrix, method = 'euclidean', diag =TRUE, upper = TRUE) #generate distance matrix object
distmat <- as.matrix(mydist) #convert to matrix object

#convert to igraph object and make minimum spanning tree
g <- graph.adjacency(distmat, weighted = TRUE) #create adjacency matrix
mymst <- mst(g)

V(mymst)$color <- vertexColors

list.vertex.attributes(mymst)

#make a layout so X/Y coords are accessible
layout <- layout_with_fr(mymst, dim = 2, niter = 1000)

treecoords <- as.data.frame(layout)
rownames(treecoords) <- rownames(mstdata)
colnames(treecoords) <- c("MST-X","MST-Y")
write.csv(treecoords, file = "MSTcoords.csv") #save this and integrate to big csv of all file events using "parse big csv" code

#Plot MST, all nodes same size, color by cluster ID to match FDL plots
plot(mymst, layout = layout, vertex.size = 10, edge.arrow.size = 0.5) #specifying layout here determines coords

######Parse Big Master Csv###
#accepts as input "ClusterIDs.csv", "FDL_coords.csv" and "MSTcoords.csv"
#generates "AllData.csv" for making FDL plots in R and individual csv files for FCS Express R import
######

mydata1 <- fread("ClusterIDs.csv") #read in csv file exported from Vortex
FDLdata <- fread("FDL_coords.csv", sep = ";") #read in force directed layout coordinates
colnames(FDLdata) <- c("EventID","Filename","Index_In_File","FDL-X","FDL-Y")
MSTdata <- fread("MSTcoords.csv")
colnames(MSTdata) <- c("ClusterID","MST-X","MST-Y")
MSTdata$ClusterID <- as.numeric(as.character(MSTdata$ClusterID))
FDLdata$EventID <- as.numeric(as.character(FDLdata$EventID))
mydata1$EventID <- sprintf("%07d", mydata1$EventID) #pad eventID for sorting 
FDLdata$EventID <- sprintf("%07d", FDLdata$EventID) #pad these too 

mydata1 <- mydata1[order(mydata1$EventID),] #order rows by eventID
FDLdata <- FDLdata[order(FDLdata$EventID),] #order rows by eventID

FDLdata[,c(2,3)] <- NULL #remove duplicate cols with mydata1

mydata2 <- merge(mydata1, FDLdata, by = "EventID", all.x=TRUE) #merge using data.table, fast!
mydata2 <- merge(mydata2, MSTdata, by = "ClusterID", all.x=TRUE)

mydata3 <- na.omit(mydata2, cols = "FDL-Y")

fwrite(mydata3, file = "AllData.csv") #to use for coloring graphml FDL plot by clusters

X <- split(mydata2, mydata2$`File Name`) #split big list into list of dataframes based on file name of orig files

X <- lapply(X, function(x) x[order(x$'Index in File'),]) #sort by original event numbers

#save a csv for each data frame in the list of frames
lapply(1:length(X), function(i) write.csv(X[[i]], 
                                          file = paste0(names(X[i]), ".csv"),
                                          row.names = FALSE))

####Force Directed Layout Graphs using graphml object###
#takes graphml file output from vortex as input, colors using info from tabular data in "AllData.csv"
####

FDL.all <- fread("AllData.csv") #Open this, comes from "ParseBigCsv" script

FDL.orig <- FDL.all

FDL.all <- FDL.all[,c("ClusterID","EventID","File Name","Index in File",
                      "FDL-X","FDL-Y")] #just take these cols out

colorkey <- as.data.frame(V(mymst)$name) #uses for key of clusters to colors
colorkey$Color <- V(mymst)$color #same

colnames(colorkey) <- c("ClusterID","Color")

colorkey <- data.table(colorkey) #convert to data table for fast merge later

colorkey$ClusterID <- factor(as.character(colorkey$ClusterID))

FDL <- read_graph(file = "FDL.graphml", format = "graphml")

list.vertex.attributes(FDL) #shows all vertex attributes

gmlclusters <- vertex_attr(FDL, "cluster") #pull out vertex list of cluster names for merging in color info

gmlclusters <- data.table(gmlclusters)

colnames(gmlclusters) <- "ClusterID"

gmlclusters$ClusterID <- factor(as.character(gmlclusters$ClusterID)) #factor cluster IDs
gmlclusters$Sort <- rownames(gmlclusters) #add col of numbers to use for sorting later
gmlclusters$Sort <- as.numeric(as.character(gmlclusters$Sort)) #as numeric
gmlclusters$Sort <- sprintf("%05d",gmlclusters$Sort) #pad zeros

gmlclusters1 <- merge(gmlclusters, colorkey, by = "ClusterID", all.x = TRUE) #combine colorkey and gmclusters table

gmlclusters1 <- gmlclusters1[order(Sort),] #reorder using sort column of numbers

V(FDL)$color <- gmlclusters1$Color #add color info to igraph object

V(FDL)$y <- -1 * V(FDL)$y #flip Y axis values to match vortex plots

plot(FDL, vertex.size = 1) #plot this, save as pdf


#use dataframe from above section as counts table, doing this part now to make groupKey for coloring FDL plots by cond.
counts <- t(mydata) #but must transpose it
write.csv(counts, file="counts.csv") #deal with this in excel to make group list
groupKey <- read.csv(file = "RowLabels.csv") #read it back in, make 1st col group numbers
groupKey <- groupKey[groupKey$X %in% rownames(mydata),] #keep only groupKey rows to match files used
rownames(groupKey) <- groupKey$X 
groupKey$X <- NULL
groupKey$Desc <- as.character(groupKey$Desc) #refactor
groupKey$Desc <- factor(groupKey$Desc) #refactor
groupKey$Group <- factor(groupKey$Group) #factor groups
#levels(groupKey$Group) <- c("1","2","3","4","5","6") #renumber for convenience
write.csv(groupKey, file = "groupKey.csv")

#setup key to color by cond

FDL.all <- FDL.all[order(EventID),] #now work with this b/c has sample info that can be parsed to treatment/condition

colnames(FDL.all) <- c("ClusterID","EventID","FileName","IndexInFile","FDL-X","FDL-Y")
FDL.all$FileName <- gsub("_processed", "", FDL.all$FileName)

temp1 <- groupKey #make a merge key data frame
temp1$FileName <- rownames(temp1) 
temp1[,1] <- NULL #remove column with group numbers
row.names(temp1) <- 1:nrow(temp1) #number row names
temp1 <- data.table(temp1)
  
gmlclusters2 <- as.data.frame(vertex_attr(FDL, "dpID")) #seems to be event number, data point ID?
gmlclusters2$sort <- rownames(gmlclusters2)
gmlclusters2$sort <- as.numeric(as.character(gmlclusters2$sort)) #as numeric
gmlclusters2$sort <- sprintf("%05d",gmlclusters2$sort) #pad zeros
colnames(gmlclusters2) <- c("EventID","Sort")
gmlclusters2 <- data.table(gmlclusters2)
  
gmlclusters3 <- merge(FDL.all, gmlclusters2, by = "EventID", all.x = TRUE) #merge the two things
gmlclusters4 <- merge(gmlclusters3, temp1, by = "FileName")

gmlclusters4 <- gmlclusters4[order(Sort),] #reorder using sort column of numbers



V(FDL)$Treatment <- as.character(gmlclusters4$Desc) #add color info to igraph object

FDL_Phago <- induced.subgraph(FDL, which(V(FDL)$Treatment=="Phago")) #make subgraph of only specified conditions

FDL_EDTA <- induced.subgraph(FDL, which(V(FDL)$Treatment=="EDTA")) #make subgraph of only specified conditions

FDL_Ice <- induced.subgraph(FDL, which(V(FDL)$Treatment=="Ice")) #make subgraph of only specified conditions

FDL_NoBact <- induced.subgraph(FDL, which(V(FDL)$Treatment=="NoBact"))


plot(FDL_Phago, vertex.size = 1, main = "Phago")

plot(FDL_EDTA, vertex.size = 1, main = "EDTA")

plot(FDL_NoBact, vertex.size = 1, main = "No Bacteria")

plot(FDL_Ice, vertex.size = 1, main = "Ice")



################################
#use edgeR glm approach for statistical analysis, employs a negative binomial distribution model
################################

group <- groupKey[,1] #define list of sample groups #make group list for modeling

## make DGElist
mylist <- DGEList(counts = counts, group = group)
write.csv(mylist$samples, file="AnnotatedSamples.csv")
dim(mylist)
mylist.full <- mylist
summary(cpm(mylist))


#reset libary sizes
mylist$samples$lib.size <- colSums(mylist$counts)
mylist$samples


#Normalize

mylist <- calcNormFactors(mylist, method = "none")
mylist


##
mycolors <- brewer.pal(4, "Set1")
jColors <- with(groupKey,
                data.frame(Desc = levels(Desc),
                      color = mycolors[1:4]))
##


plotMDS(mylist, method="bcv",
        col = jColors$color[match(groupKey$Desc, jColors$Desc)],
        pch=20)
legend("topright", levels(groupKey$Desc),
       col=jColors$color, pch=20)



############
#glm method#
############

design1 <- model.matrix(~ 0 + group, data=mylist$samples)  #define exp design
y <- estimateDisp(mylist, design1) #esimate common dispersion
plotBCV(y) #plot biological CVs
fit <- glmFit(y, design1) #fit model using design matrix

lrt.one <- glmLRT(fit, contrast = c(0,-1,0,1)) #groups Phago Minus Ice
DEG1 <- topTags(lrt.one, n=20, p.value = 0.05)

lrt.two <- glmLRT(fit, contrast = c(-1,0,0,1)) #groups Phago Minus EDTA
DEG2 <- topTags(lrt.two, n=20, p.value = 0.05)

lrt.three <- glmLRT(fit, contrast = c(0,0,-1,1)) #groups Phago Minus NoBact
DEG3 <- topTags(lrt.three, n=20, p.value = 0.05)



write.csv(DEG1, file = "PhagoMinusIce.csv")
write.csv(DEG2, file = "PhagoMinusEDTA.csv")
write.csv(DEG3, file = "PhagoMinusNoBact.csv")


plotSmear(lrt.one, de.tags = rownames(DEG1$table), main = "Phago Minus Ice")
text(x = DEG1$table$logCPM,
     y = DEG1$table$logFC,
     labels=rownames(DEG1$table),
     cex = 0.8,
     pos = 4,
     offset = 1)

plotSmear(lrt.two, de.tags = rownames(DEG2$table), main = "Phago Minus EDTA")
text(x = DEG2$table$logCPM,
     y = DEG2$table$logFC,
     labels=rownames(DEG2$table),
     cex = 0.8,
     pos = 4,
     offset = 1)

plotSmear(lrt.three, de.tags = rownames(DEG3$table), main = "Phago Minus NoBact")
text(x = DEG3$table$logCPM,
     y = DEG3$table$logFC + 6,
     labels=rownames(DEG3$table),
     cex = 0.8,
     pos = 4,
     offset = 1)



#Hua says, look at your data before doing statistical tests
#Also want to do correlation and throw out outliers
rowAnnot <- as.data.frame(groupKey$Desc)
rownames(rowAnnot) <- rownames(mydata)
#rowAnnot$Group <- NULL

pheatmap(log(mydata+1), scale = "column", annotation_row = rowAnnot)
pheatmap(cor(counts), annotation_row = rowAnnot)


####
#Plot MST with vertices sized proportional to counts per cluster
####

ClusterCounts <- as.data.frame(colSums(mydata))
colnames(ClusterCounts) <- "TotalCounts"
ClusterCounts$ClusterID <- rownames(ClusterCounts)
rownames(ClusterCounts) <- 1:nrow(ClusterCounts)
vertexatt <- merge(ClusterCounts, colorkey, by = "ClusterID")
vertexatt1 <- as.data.frame(V(mymst)$name)
colnames(vertexatt1) <- "ClusterID"
vertexatt1$Sort <- rownames(vertexatt1)
vertexatt1$Sort <- as.numeric(as.character(vertexatt1$Sort)) #as numeric
vertexatt1$Sort <- sprintf("%05d",vertexatt1$Sort) #pad zeros
vertexatt1 <- data.table(vertexatt1)
vertexatt <- data.table(vertexatt)
vertexatt <- merge(vertexatt, vertexatt1, by = "ClusterID")
vertexatt <- vertexatt[order(Sort),]

scaledvert <- ecdf(vertexatt$TotalCounts) #calculate CDF for cluster counts distribution

V(mymst)$size <- scaledvert(vertexatt$TotalCounts) * 10 #apply to cluster counts and scale to size nodes of graph

vertexatt$CumDist <- scaledvert(vertexatt$TotalCounts) #put into dataframe just to have it

#plot new MST, node sizes proportional to counts, nodes color to match FDL plots
plot(mymst, layout = layout,
     edge.arrow.size = 0.5,
     label.dist = 1,
     vertex.color = vertexColors) #specifying layout here determines coords

list.vertex.attributes(mymst)



