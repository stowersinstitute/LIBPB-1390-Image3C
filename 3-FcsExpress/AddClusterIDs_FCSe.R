##This function does:
#Adds cluster IDs to events using template file from exported Vortex X-shift clustering 

#line 42 should be edited to ensure one is taking FDL x and y, and MST x and y coords from the table, along with ClusterID and Index in File.
#any references to file paths shoudl be adjusted to match the location of your data

#cbind.fill function from interwebs
cbind.fill <- function(...){
  nm <- list(...) 
  nm <- lapply(nm, as.matrix)
  n <- max(sapply(nm, nrow)) 
  do.call(cbind, lapply(nm, function (x) 
    rbind(x, matrix(, n-nrow(x), ncol(x))))) 
}

filename <- "S:\\cyto\\_Data\\Bazzini\\MDV\\18cy1293\\FcsExpress\\Template.csv" #table of cluseter IDs and object numbers

###code below is for troubleshooting in R studio###
#mat <- read.csv(file="OrigMatrix.csv")

##Function
Execute <- function(mat)
{
  setClass("TransformationResult",
           representation(
             newParamData="matrix",
             numberOfNewParams="integer",
             newParamNames="character"
           ),
           prototype(
             newParamData=c(),
             numberOfNewParams=as.integer(0),
             newParamNames=""
           )
  )
  
  write.csv(mat,file="S:\\cyto\\_Data\\Bazzini\\MDV\\18cy1293\\FcsExpress\\OrigMatrix.csv")
  
  result <-  new("TransformationResult")
  
  clId <- read.csv(file = filename)
  keep <- as.matrix(clId[,c(1,4,26,27,28,29)]) #pull out event number, AreaBF, FDX x and y, and cluster ID cols - use Area BF to ensure events match up (slope = 1)
  mat <- cbind.fill(mat, keep) #merge two matrices
  df1 <- as.data.frame(mat) #conv to df
  df1[is.na(df1)] <- 20000 #replace NAs with big number
  df1$FDL.Y <- df1$'FDL.Y' * -1 #flop Y axis for FDL plot to match vortex png versions
  mat <- as.matrix(df1) #conv back to matrix
  #mat <- mat[,-1] #remove col 'X'
  result@numberOfNewParams <- ncol(mat) #put num of new parms into object
  result@newParamData <- t(mat) #put data into object, EVENTS MUST BE AS COLS thus the transpose function!!!
  result@newParamNames <- paste("NewParm",colnames(mat)) #put parm names into object
  
  write.csv(mat,file="S:\\cyto\\_Data\\Bazzini\\MDV\\18cy1293\\FcsExpress\\NewMatrix.csv")
  
  return(result)
  
}