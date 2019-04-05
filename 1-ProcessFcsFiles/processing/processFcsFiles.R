library(flowCore)
library(flowStats)
library(ggcyto)
library(ggridges)
library(stringr)
library(Hmisc)
library(caret)
library(pheatmap)
library(reshape2)
library(data.table)
library(RColorBrewer)
source("AuxFunctions.R") #sources functions from this file in same directory


###############################
#read in files, pull out some header data etc that we'll need
myflowset <- read.flowSet(pattern = ".fcs", path = ".", alter.names = TRUE, transformation = FALSE, emptyValue = FALSE) #read all fcs files in current dir to flowset
mycolnames <- as.character(colnames(exprs(myflowset[[4]]))) #get all channel names
autoplot(myflowset[[4]]) #use "snail1_phago"

#generate clustering heatmap of feature correlation from a frame in the set
myframe <- myflowset[[4]] #pull out a single flow frame
mat <- exprs(myframe) #extract matrix
cor_mat <- cor(mat, method = "spearman") #get correlation matrix
pheatmap(cor_mat) #plot it using clustering heatmaps

#####
#remove redundant features based on correlation
#####

myfrm <- data.frame(exprs(myframe)) #convert data from 1st sample to data frame object
frmTrim <- DaMiR.FReduct(myfrm, th.corr = 0.85) #removes features with Cor values > 0.85
colstrimmed <- colnames(frmTrim) #get names of remaining features
toremove <- setdiff(mycolnames, colstrimmed) #set operation to find difference with total

myflowset <- dropSet(myflowset, toremove)

#generate new clustering heatmap 
myframe <- myflowset[[4]] #pull out a single flow frame
mat <- exprs(myframe) #extract matrix
cor_mat <- cor(mat, method = "spearman") #get correlation matrix
pheatmap(cor_mat) #plot it using clustering heatmaps

#sample correlations by feature means
myMeans <- extractMeans(myflowset) #get a list of features means, one list item per file
myMeans <- rbindlist(myMeans) #combine to one big table
myMeans <- dcast(myMeans, Sample ~ Feature, value.var = "Means") #recast to wide form
rownames(myMeans) <- myMeans$Sample #rename rownames
myMeans[,1] <- NULL #remove redundant col
#convert all to numeric
myMeans[] <- lapply(myMeans, function(x) {
  if(is.factor(x)) as.numeric(as.character(x)) else x
})

meansMat <- as.matrix(myMeans) #convert to matrix
rownames(meansMat) <- rownames(myMeans)
meansMat[!is.finite(meansMat)] #check for infinite values
write.csv(rownames(meansMat), file="NamesToGroup.csv") #save table to manually annotate things if needed
rowAnnot <- read.csv(file="RowLabels.csv")
rownames(rowAnnot) <- rownames(meansMat) #put rownames from means table
rowAnnot[,1] <- NULL #remove redudant column
setdiff(myflowset@phenoData@data$names,rowAnnot$X) #check that sample names match, should return NULL


pheatmap(meansMat, scale = "column", annotation_row = rowAnnot) #make clustering heatmap of feature means per sample
breaksList <- seq(0.9,1, by = 0.01)
pheatmap(cor(t(meansMat)), annotation_row = rowAnnot[,c(1:3)],
         color = colorRampPalette(rev(brewer.pal(n = 10, name = "RdYlBu")))(length(breaksList)),
         breaks = breaksList) #heatmap of correlation 
pheatmap(cor(t(meansMat)))

####
#remove outlier samples, can skip if correlation is high among all, uncomment and run to do it
####

# meansCor <- cor(t(meansMat)) #correlation on transposted means matrix
# tokeep <- findCorrelation(meansCor, cutoff = 0.95, names = FALSE) #list of samples with mean cor >0.9
# tokeepnames <- findCorrelation(meansCor, cutoff = 0.9, names = TRUE) #same but return names not index
# myflowset <- myflowset[c(tokeep)] #subset flowset to remove low cor samples
# rowAnnot <- rowAnnot[tokeepnames,] #remove dropped samples from annotation data
# rowAnnot <- as.data.frame(rowAnnot)
# colnames(rowAnnot) <- "Desc"
# rownames(rowAnnot) <- myflowset@phenoData@data$name
# 
# #sample correlations by feature means, do again w/out outliers
# myMeans <- extractMeans(myflowset) #get a list of features means, one list item per file
# myMeans <- rbindlist(myMeans) #combine to one big table
# myMeans <- dcast(myMeans, Sample ~ Feature, value.var = "Means") #recast to wide form
# rownames(myMeans) <- myMeans$Sample #rename rownames
# myMeans[,1] <- NULL #remove redundant col
# #convert all to numeric
# myMeans[] <- lapply(myMeans, function(x) {
#   if(is.factor(x)) as.numeric(as.character(x)) else x
# })
# 
# meansMat <- as.matrix(myMeans) #convert to matrix
# rownames(meansMat) <- rownames(myMeans)
# meansMat[!is.finite(meansMat)] #check for infinite values
# setdiff(myflowset@phenoData@data$names,rownames(rowAnnot)) #check that sample names match, should return NULL
# 
# pheatmap(meansMat, scale = "column", annotation_row = rowAnnot) #make clustering heatmap of feature means per sample
# breaksList <- seq(0.9,1, by = 0.01)
# pheatmap(cor(t(meansMat)), annotation_row = rowAnnot,
#          color = colorRampPalette(rev(brewer.pal(n = 10, name = "RdYlBu")))(length(breaksList)),
#          breaks = breaksList) #heatmap of correlation 
# pheatmap(cor(t(meansMat)), method = "spearman")
# 
#####
#transform fluorescent parms to allow gaussNorm normalization
#####
mycolnames <-  colnames(myflowset[[4]]) #get new list of parm names
autoplot(myflowset[[4]]) #plot all histograms
ChnlsToTrans <- mycolnames[c(15:18)] #which parms to transform
translist <- estimateLogicle(myflowset[[4]], ChnlsToTrans) #estimate logicle transform from data
myflowsetTrans <- transform(myflowset, translist) #apply logicle transform to flowset
autoplot(myflowsetTrans, mycolnames[19], mycolnames[21]) + geom_hex(bins=40) #have a look at some data
autoplot(myflowsetTrans[[4]])

#plot stacked hisograms
p <- ggcyto(myflowsetTrans, aes(x = 'Intensity_AdaptiveErode_BF_Ch11'))
p + geom_density_ridges(aes(y = as.factor(name))) + facet_null()

#####
#scale and center flow frames in set, one by one not merged
#only do for DNA intensity on this set
#####

mycolnames <- colnames(myflowset[[4]])

flowsetScaled <- scaleDNA(myflowsetTrans) #Make sure scaleDNA function in 'auxFunctions' script is working on correct column and parameter here!

#Snail3_Phago_18 has abnormal draq5 staining, will remove it
tokeep <- myflowset@phenoData@data$name
tokeep <- tokeep[c(1:11,13:20)]
flowsetScaled <- flowsetScaled[c(tokeep)]  #Remove that sample (keep all but index 12 in list of names)

#Check DNA content histograms before scaling data
p <- ggcyto(myflowsetTrans, aes(x = 'Intensity_AdaptiveErode_BF_Ch11'))
p + geom_density_ridges(aes(y = as.factor(name))) + facet_null() #+ xlim(c(-3,3))


#plot stacked histograms of transformed, orig data
p <- ggcyto(flowsetScaled, aes(x = 'Intensity_AdaptiveErode_BF_Ch02'))
p + geom_density_ridges(aes(y = as.factor(name))) + facet_null()

p2 <- ggcyto(flowsetScaled, aes(x = 'Intensity_AdaptiveErode_BF_Ch07'))
p2 + geom_density_ridges(aes(y = as.factor(name))) + facet_null()

p3 <- ggcyto(flowsetScaled, aes(x = 'Intensity_AdaptiveErode_BF_Ch11'))
p3 + geom_density_ridges(aes(y = as.factor(name))) + facet_null() + xlim(c(-3,3))



#use gaussNorm functino from flowStats to normalize each channel across files
maxlms <- c(2)
ChnlsToNorm <- mycolnames[18] #Intensity CTV, Max Pixel draq5
normResult <- gaussNorm(flowsetScaled, channel.names = ChnlsToNorm,
                        max.lms = maxlms,
                        peak.distance.thr = 0.1,
                        peak.density.thr = 0.05) #normalize DNA parm

myflowsetNorm <- normResult$flowset #pull out flowset from returned object

p2 <- ggcyto(myflowsetNorm, aes(x = 'Intensity_AdaptiveErode_BF_Ch11'))
p2 + geom_density_ridges(aes(y = as.factor(name))) + facet_null() + xlim(c(-3,3))


# #can do again with different settings if above doesn't work for some params
# maxlms <- c(2)
# ChnlsToNorm <- mycolnames[c(16)] #Intensity DHR
# normResult <- gaussNorm(myflowsetNorm, channel.names = ChnlsToNorm,
#                         max.lms = maxlms,
#                         peak.distance.thr = 0.2,
#                         peak.density.thr = 0.05) #normalize DNA parm
# 
# myflowsetNorm1 <- normResult$flowset #pull out flowset from returned object
# 
# 
# p3 <- ggcyto(myflowsetNorm1, aes(x = 'Intensity_AdaptiveErode_BF_Ch02'))
# p3 + geom_density_ridges(aes(y = as.factor(name))) + facet_null()

##and one more time

# maxlms <- c(2)
# ChnlsToNorm <- mycolnames[c(18)] #Intensity draq5, set using the assumption that most cells are 2n, 
# #ie, EDTA hasn't induced arrest at 4n, but should confirm.
# normResult <- gaussNorm(myflowsetNorm, channel.names = ChnlsToNorm,
#                         max.lms = maxlms,
#                         peak.distance.thr = 0.3,
#                         peak.density.thr = 0.1) #normalize DNA parm
# 
# myflowsetNorm2 <- normResult$flowset #pull out flowset from returned object
# 
# 
# p3 <- ggcyto(myflowsetNorm2, aes(x = 'Intensity_AdaptiveErode_BF_Ch11'))
# p3 + geom_density_ridges(aes(y = as.factor(name))) + facet_null()


##############Save new fcs files###############

#set up file names

dir <- getwd()
mynames <- myflowsetNorm@phenoData@data$name #get file names from flowset
mynames <- strsplit(mynames, "\\.") #string split on "."
mynames <- sapply(mynames, function(x) strsplit(x, ":")[[1]][1]) #get out 1st element from strsplit output
mynames <- paste(mynames, "_processed.fcs", sep = "") #paste in new suffixes

#save new fcs files
write.flowSet(myflowsetNorm, dir, filename = mynames) #make sure you point to the correct flowSet here!




