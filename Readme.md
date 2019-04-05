
# Instructions for running morphoClust analysis

## Data acquisition on the imagestream

 1. Acquire data at the highest possible magnification ensuring compensation controls are collected and the camera is not saturated.
 2. Perform color compensation in IDEAS and apply to an example data file when opening it in IDEAS for analysis.  
 3. Generate features that capture elements of size, shape, texture and intensity for any channels/dyes of interest.  
 
 #### *Important: For texture features, use a mask that encompasses the whole cell.  For shape features, use a mask that captures the shape of the signal, e.g. morphology for flourescence or adaptive erode for BF.*
 
 4. Export feature values as FCS.  Be sure to have daf files that correspond exactly to the events exported to the FCS format (i.e. don't export a subset of cells as fcs unless you also create a new cif file that matches).  This will become important later when analyzing and merging in new paramters in FCS Express.

## FCS file pre-processing for clustering

 1. Install R version 3.5.X and R studio (newest version).  
 
 #### *If on site at SIMR, run using R studio on a linux computational server.*
 
 2. Install the following R packages: flowCore, flowStats, ggcyto, ggridges, stringr, Hmisc, caret, pheatmap, reshape2, data.table, RColorBrewer, edgeR, plyr, ggplot2, pastecs, igraph.
 3. Create R studio project in a folder containing fcs files exported from IDEAS. 
 4. Open the script called "processFcsFiles.R" and run line by line.  

**Note where comments suggest that changes should be made based on your data set or to the code to accommodate differences between experiments, files, etc.  For example, you'll need to make an read in a csv file called "RowLabels.csv" around line 59 for use in annotations.  This has to match your sample names.  See the example files in the github.**

 6. Be careful using gaussNorm().  It's possible to normalize out your results.  We find it's best for DNA content staining drift correction, where the true nature of 2N and 4N peaks is known.  It can also be used for antibody staining drift but use caution that what you're seeing is drift due to a titer or cell number difference and not a result.
 7. New fcs files are exported at the end of the script with "_processed.fcs" appended to the end.  These files will be imported into Vortex/Xshift for clustering.
 

## Clustering in Vortex

 1. Install vortex from here:  https://github.com/nolanlab/vortex/releases
 2. Instructions for use are here: https://github.com/nolanlab/vortex/wiki/Getting-Started
 3. After Vortex is installed, import your processed FCS files.  Apply import settings of your preference, it depends on the data somewhat, but for example probably not necessary to transform again since we did it in R already for fluroescent parameters.
 4. Run clustering with K (number of nearest neighbors)  across a range of values from approximately 10-150, then select all clusters and choose validation, and find elbow point for cluster number.
 5. Next, select the clustering result with the desired value for "K", then right click in the top-right list of clusters and choose "create graph -> force directed layout".  Specify the number of events per cluster you want to use.  Be sure and get enough to each file has decent representation.  Let it run until it reaches equilibrium.
 6. Stop the layout and run "export graph as graphml" and "export cell coordinates" below.  Save the files as "FDL.graphml" and "FDL_coords.csv" respectively together in a folder for processing later.  Export images if you like, but we'll be plotting this again in R.
 7. Back in the main Vortex windows, right click your cluster result in the bottom left window and select "Export as csv".  Save this file as "ClusterIDs.csv".  Then, right click the cluster result again and choose "Computer group stats per cluster".  Select all in the results (control-A) then paste to excel and save this file as "GroupStatsPerCluster.csv".  Finally, click into the window at the top right again, select all with "cntl-A" and copy with "cntl-C" and past into a new excel sheet.  Save this as "ClusterFeatureAverages.csv".
 8. You should have the following tabular data items now coming from Vortex:
     * ClusterIDs.csv
     * GroupStatsPerCluster.csv
     * ClusterFeatureAverages.csv
     * FDL_coords.csv
     * FDL.graphml

## Analysis of Clustering results in R

1. Create an R studio project in the folder with the tabular data above.  Again, can run from R Studio on maple or hickory servers at SIMR.
2. Open the script called "processClusteringResults.R".
3. Line ~261 must specify number of conditions.
4. Section under GLM method ~line 278 must be customized for your variables.  Purpose is to perform negative binomial modeling on cell counts per cluster between conditions of interest to find clusters that are present in different amounts between groups or variables.
5. Save any resulting and desired plots manually in R studio (Force directed layout FDL plots per condition are saved automatically though).
6. Make note of any statistically significant clusters between groups or variables.  These can be displayed in FCS Express in the next steps.
7. Copy the new csv files generated (one per sample) into a new folder to be used in the next section.  These csv files contain feature values per sample, and also cluster ID, FDL plot coordinates and spanning tree plot coordinates per cell.  This data can be merged into daf files in FCS Express using the "R add parameters" transformation option.

## Data exploration and analysis in FCS Express

 1. Open FCS Express.  Under File -> options -> startup, make sure ""Start the De Novo Software application external application bridge on login" is selected. Restart FCS Express.
 2. Open the R script called "AddClusterIDs_FCSe.R" and ensure any file paths point to the folder where your new csv files are located.  Also, be sure that line 42 is taking columns 1, 4, and the last 4 columns (6 total) from your csv files.  This will ensure we can merge in the cluster IDs and plot coordinates into the daf files.
 3. Open a daf file in FCS Express.
 4. Rename the corresponding csv file "Template.csv".  I usually make a copy first and rename that, keeping the set with original names.
 5. In FCS Express, go to Tools -> Transformations -> R add parameters.
 6. Point it to the "AddClusterIDs_FCSe.R" script and select "object number" for export. Ensure "events as rows" is checked.  
 7. Drag the transformation to a plot, it should run and generate two test files (just for debugging) in the folder with the csv files called "NewMatrix" and "OrigMatrix".  If these aren't made, it's not running.  Check all the above steps carefully.
 8. If it's working, you should have new parameters now for ClusterID, FDL-X, FDL-Y, MST-X and MST-Y.  
 9. Cell images for cells in a given cluster or position in MST or FDL plots can now be displayed in a data grid for confirmation of their identities or making figures.

