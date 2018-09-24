#####functions needed############

#scale & center matrices of exprs in each flow frame in the set
scaleSet <- function(fs){
  fsApply(fs, FUN = function(fr){
    mat <- exprs(fr)
    mat <- scale(mat) #scale draq5 intensity parm
    exprs(fr) <- mat
    exprs(fr)
    
    fr
  })
}

#scale & center DNA intensity parm
scaleDNA <- function(fs, ...){
  fsApply(fs, FUN = function(fr, y){
    mat <- exprs(fr)
    mat[,y] <- scale(mat[,y]) #scale draq5 intensity parm
    exprs(fr) <- mat
    exprs(fr)
    
    return(fr)
  })
}

#function to return list of feature means for each sample in a flowset
extractMeans <- function(fs){
  
  fsApply(fs, FUN = function(fr){
    myrownames <- colnames(fs[[1]])
    
    frname <- fr@description$GUID
    frname <- strsplit(frname, "\\.") #string split on "."
    frname <- frname[[1]][[1]] #get out 1st element from strsplit output
    mat1 <- exprs(fr)
    means <- colMeans(mat1)
    output1 <- data.frame(cbind(frname, means))
    output1$feature <- rownames(output1)
    rownames(output1) <- seq(length=nrow(output1))
    colnames(output1) <- c("Sample","Means","Feature")
    return(output1)
  })
}


#function from DaMiRseq package to remove features with high correlation to one another
DaMiR.FReduct <- function(data,
                          th.corr=0.85,
                          type=c("spearman","pearson")){
  
  # check arguments
  if (missing(data)) stop("'data' argument must be provided")
  if (missing(type)){
    type <- type[1]
  }
  
  # check the type of argument
  if(!(is.numeric(th.corr)))
    stop("'th.corr' must be numeric")
  if(!(is.data.frame(data)))
    stop("'data' must be a data.frame")
  
  # check the presence of NA or Inf
  if (any(is.na(data)))
    stop("NA values are not allowed in the 'data' matrix")
  if (any(is.infinite(as.matrix(data))))
    stop("Inf values are not allowed in the 'data' matrix")
  
  # specific checks
  if (th.corr >1 | th.corr < 0)
    stop("'th.corr must be between 0 and 1")
  if (all((as.matrix(data) %%1) == 0))
    warning("It seems that you are using raw counts!
            This function works with normalized data")
  
  features<-dim(data)[2]
  
  # remove redundancy
  if(type == "spearman"){
    cormatrix <- abs(rcorr(as.matrix(data), type='spearman')$r)
  } else if (type == "pearson"){
    cormatrix <- abs(rcorr(as.matrix(data), type='pearson')$r)
  } else {
    stop("Please set 'spearman or 'pearson' as correlation type.")
  }
  
  index_geneHighCorr<- findCorrelation(cormatrix, cutoff = th.corr)
  data_reduced<-data[, -index_geneHighCorr, drop=FALSE]
  
  cat(features-dim(data_reduced)[2],
      "Highly correlated features have been discarded for classification.",
      "\n",
      dim(data_reduced)[2],
      "Features remained.",
      "\n")
  return(data_reduced)
}

#drop specified colnames
dropSet <- function(fs, toremove){
  fsApply(fs, FUN = function(fr){
    exprs(fr) <- exprs(fr)[,-which(colnames(exprs(fr)) %in% toremove)]
    fr
  })
}