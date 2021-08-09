# Step-by-step instructions for running Image3C analysis

## Data acquisition on the ImageStream

1.  Images of the events of interest should be acquired at the highest
    possible magnification (60x) that fully includes the events in the
    field of view and at a speed of max 1,000 cells/min.

2.  About 10,000 nucleated and focused events should be saved for each
    sample and multiple samples should be run as biological replicates
    (4-7 replicates).

3.  Events from single color control samples should be collected for
    each channel used (except for brightfield).  

4.  The power of the lasers should be adjusted to not saturate the
    camera for any cells of interest. This can be verified in the
    acquisition software by plotting "raw signal intensity" of events of
    interest and checking that raw pixel values are below 4046 for
    cellular events.

More information about sample preparation and data collection can be found in the manuscript “Image3C, a multimodal image-based and label independent integrative method for single-cell analysis” (Accorsi, Peuß, Box et al., 2021, eLife https://elifesciences.org/articles/65372).

More information about the ImageStream Mark II (Amnis Millipore
Sigma) and how to use it can be found at: <https://www.luminexcorp.com/imagestreamx-mk-ii/#documentation>.

A dataset is provided as example at the Stowers Original Data Repository at http://www.stowers.org/research/publications/libpb-1390. These RIF files have been saved directly from the ImageStream after running 5 replicates for each of the 2 analyzed conditions (Females Untreated and Female EDTA Treatment).

## Data normalization and feature value calculation in IDEAS

1.  Open IDEAS software (Amnis Millipore Sigma, free for download once an Amnis user
    account is created).

2.  Perform the color compensation following the Wizard and according to the IDEAS documentation.

3.  Apply the color compensation to all the RIF files using the batch
    analysis method.
    
    *Important: leave the option to specify a “DAF file to use as a reference” blank for now.* 

4.  Select a representative sample that contains all labels and use this
    to create masks. Create masks in the following manner (more information about creating
    masks in the IDEAS documentation):

    a.  *For texture features, use a mask that encompasses the whole
        cell, such as "adaptive erode" on bright field channel. The same mask can be used to calculate texture features for other channels too, even though it was created using brightfield signal.*

    b.  *For shape features, use a mask that captures the shape of the
        signal,* *such as a "morphology" mask.*

    c.  *For side scatter, use a mask that includes the "spots" of
        intensity that are often seen with this channel (if unsure, a
        "morphology" mask is adequate).*

5. Calculate feature values that describe size, shape, texture, and
    intensity for any channels/dyes of interest. The tool "Feature finder" can be used
    to create multiple features at once. Refer to the IDEAS documentation for use of the "Feature finder". 
    
    *Important: The exact complement of features used is not critical since
    typically many features have overlapping information content and
   redundant features will be removed later. The suggested attributes to capture are from these major classes:* *size,
    shape, texture, and* *intensity.*
    
6.  Save the analysis and close the file. This step creates the DAF file that will be used for analyzing in batch the rest of the files.


7.  Do a batch analysis to apply the DAF file, saved in the previous step, to all samples
    and to calculate features for all files. For achieving this, click "Tools -\> Batch -\> Add batch", add all the CIF files, select the DAF file you just saved above as "DAF file template" and click "Run Batch".

8.  Export in batch all feature values as FCS files. For doing this, click "Tools -\> Export feature values", choose the
    population of events to export (e.g.,
    nucleated cells), select the features to export and select "fcs file" as file
    type. 
    
    *Important: At the end a DAF
    file (tabular data), a CIF file (compensated images) and a FCS file (per-object feature matrices) will be saved. It is important that each of them includes the same subset of events. For example, if a FCS file is exported with only nucleated events, remember to generate also a CIF file and a DAF file with the exact same population. This will become important later in the FCS Express Section.*

More information about feature descriptions and selection can be found in the manuscript “Image3C, a multimodal image-based and label independent integrative method for single-cell analysis” (Accorsi, Peuß, Box et al., 2021, eLife https://elifesciences.org/articles/65372).

IDEAS (Amnis Millipore Sigma) User Guide can be found at: <https://www.luminexcorp.com/imagestreamx-mk-ii/#documentation>.

Tutorial videos for creating masks and calculating feature values in IDEAS are available in the GitHub location https://github.com/stowersinstitute/LIBPB-1390-Image3C/tree/master/TutorialVideos.

CIF, DAF and FCS files are provided in the GitHub.

## FCS file pre-processing in R for clustering 

1.  Install the newest version of R and R Studio (https://cran.r-project.org, the newest version as of June 2021 works well with all libraries used).

2.  Create an R studio project in a folder containing your FCS files just
    exported from IDEAS.

3.  Open the script called \"1_processFcsFiles.R\" in the github
    location "... Code". 

4.  Run the code line by line to trim redundant features with high correlation values to each other, identify and remove outlier samples, transform fluorescence intensity values with estimateLogicle() and transform() functions, normalize and scale/center DNA intensity using gaussNorm() function and export new FCS files with "_processed.fcs" appended to the end using writeflowSet() function.
  
    *Important: Comments will indicate where changes should be made based on specific datasets to accommodate differences between experiments, files, etc. For example, a CSV file called "RowLabels.csv" is required at line 59 for use in annotations. This has to exactly match the sample names. See the example files in the GitHub location \LIBPB-1390-Image3C\1-ProcessFcsFiles\processing\RowLabels.csv.*
	
    *Important: Although it is possible to normalize out all the results, it is preferred to use it only for DNA staining drift correction, where the true nature of 2N and 4N peaks is known and can be judged whether the underlying nature of distributions was changed. This normalization can also be used for antibody staining drift, but caution needs to be used in deciding if this is a result of staining drift or a real intensity difference between samples.*

A tutorial page using the R markdown tool has been generated and made available.

Example files required to run the code are provided.

The full set of files that are generated running this code, including the new FCS files, for the example dataset are provided.

## Clustering the events in VorteX Clustering Environment/Xshift 

1.  Install VorteX Clustering Environment
    <https://github.com/nolanlab/vortex/releases>.

2.  Import the processed FCS files. Apply import settings of 
    preference but there should not be the need to apply any transformation since
    this was already done in R for the fluorescent parameters.

3.  Run X-Shift k-nearest-neighbor clustering with K (number of nearest
    neighbors) across a range of values from approximately 5 to 150,
    select all clusters, choose validation, and find elbow point for
    cluster number, or let the software auto-select the range of K
    values from the data.

4.  Select the clustering result with the desired value for K. To do
    this, click-shift to select all results for all K
    values, right click and choose "Find elbow point for cluster
    number". This is based on an optimization for finding an appropriate
    cluster number. Refer to the X-Shift publication for additional details (Samusik et al., 2016 - Automated mapping of phenotype space with single-cell data).

5.  Right click in the top-right list of clusters and choose "Create
    graph -\> Force directed layout (FDL)". Based on the data, specify the number of
    events to use in the graph. 
    
    *Important: Use enough data points so that also
    rare populations contain several events.*

6.  Let it run until it reaches equilibrium (when the points are no longer moving significantly). This may take from a few minutes to hours depending on data size.

7.  Evaluate visually if the data have been over-clustered or under-clustered. If one population comprises multiple clusters (i.e., multiple colors) then the data may be over-clustered. In such a case, it may be advantageous to select a K value that produces fewer clusters. 

8.  Stop the layout, run \"Export graph as graphml\" and \"Export
    cell coordinates\" and save the files as \"FDL.graphml\" and
    \"FDL_coords.csv\" respectively. Images of the graphs can be exported too.

 9. Back in the main Vortex window, right click the cluster result in
    the bottom-left window, select \"Export as csv\" and save this file
    as \"ClusterIDs.csv\".

10. Right click the cluster result again, choose \"Computer group
    stats per cluster\", select "all" in the results, copy, paste to
    excel and save this file as \"GroupStatsPerCluster.csv\".

11. Click into the window at the top-right again, select all, copy,
    paste into a new excel sheet, save this as
    \"ClusterFeatureAverages.csv\".

12. The following tabular data items should be obtained now coming from Vortex:

    -   ClusterIDs.csv (master table with every event with its cluster
        assignment and original sample ID)

    -   GroupStatsPerCluster.csv (table of counts of events per cluster
        and per sample)

    -   ClusterFeatureAverages.csv (table of the average feature values
        for each cluster)

    -   FDL_coords.csv (event coordinates in a 2D space)

    -   FDL.graphml (a graph of a subset of cells for each set of
        samples)

Instructions for using VorteX Clustering Environment can be found at: <https://github.com/nolanlab/vortex/wiki/Getting-Started>.

Tutorial video for clustering events in VorteX Clustering Environment is
available.

Example files that should be obtained at the end of the analysis in
VorteX Clustering Environment are provided.

## Analysis of clustering results in R

1.  Create an R studio project in the folder with the tabular data listed
    above.

2.  Open the script called \"2_processClusteringResults.R\" in the
    github location "...".

3.  Run the code line by line. 

    *Important: Specify the number of
    conditions in line 261.*

4.  Perform statistical analysis between conditions customizing the
    section under "GLM method" (line 278) based on your variables. The
    purpose is to perform negative binomial modeling on
    cluster abundance between conditions/groups/variables of interest.

5.  Save any desired plots manually in R studio (FDL plots are saved automatically for each condition).

6.  Make notes of any cluster abundance statistically significantly
    different between conditions/groups/variables. 

7.  Running the R script, split the clustering results back into
    individual files. Copy the newly generated CSV files (one file/sample)
    into a new folder to be used in the next section. These CSV files
    contain feature values per sample and cluster ID, FDL plot coordinates
    and spanning tree plot coordinates per each cell (or data point).

8.  These data can be used to visualize Feature Values by Clusters and
    to plot FDL colored by cluster IDs.

9. Save the R script to capture any edits.

A tutorial page using the R markdown tool has been generated and made available.

Example files that are required in the code and example files that
should be obtained running this code are provided in the github location
"...".

The final CSV files for the example dataset we provided are in the
github location "...".

## Data exploration and event visualization in FCS Express

1.  Open FCS Express Plus version 6 (or FCS Express Image or Plus version 7). 

2.  Under "File -\> Options -\> Startup", make sure \"Start the De Novo
    Software application external application bridge on login\" is
    selected.

3.  Restart FCS Express Plus.

4.  Open the R script called \"3_AddClusterIDs_FCSe.R\" in the github
    location "..." and ensure that the all 3 file paths point to the folder where
    the last CSV files were moved.

    *Important: make sure that line 42 is using columns 1, 4, and
    the last four columns from your CSV files, named "FDL-X", "FDL-Y", "MST-X" and "MST-Y" respectively. The last four columns will have different column numbers
    based on the total number of features in the CSV file. This will
    ensure the merge of cluster IDs and plot coordinates with the
    DAF files. Plotting FDL and minimum
    spanning tree in FCS Express Plus allows for gating events to visualize their images.*

6.  Open a DAF file in FCS Express Plus.

7.  Make a copy of the corresponding CSV file and rename it \"Template.csv\".

8.  In FCS Express Plus, go to "Tools -\> Transformations -\> R add parameters"
    ("R integration" feature).

9.  Point it to the \"3_AddClusterIDs_FCSe.R\" script and select
    \"object number\" for export. Ensure \"events as rows\" is checked.

10. Drag the transformation to a plot, it will run and generate two
    test files (debugging purpose) called \"NewMatrix\" and \"OrigMatrix\" in the folder with the CSV files. If these are not made, the
    code is not running properly and the steps above should be carefully checked again.

12. Images of events in a given cluster or position in the FDL or minimum spanning tree plots
    can now be displayed in a data grid. Subsets of events can be gated, and the
    corresponding images can be displayed. This data can be used to
    visualize Cell Images by Clusters.

Tutorial video for exploring and visualizing data in FCS Express Plus is
available in the github location "..."

Instructions for using FCS Express Plus can be found at ...

Example files that should be obtained at the end of the analysis in FCS
Express Plus are provided in the github location "...".

## Exporting tiff images for neural network training and analysis

1.  Open IDEAS software (Amnis Millipore, free for download once an Amnis user
    account is created).
    
2.  Open the raw images (RIF files).

3.  Select the Tools menu at the top of the screen, click "Export tiff images", select the population (gate) that matches what was used for previous
    analysis, and choose "16-bit" as Bit depth and "raw (for analysis)" as pixel data.

    *Important: It is suggested to have a strategy for managing file names and directories. The tiff images will be pre-pended according to the name specified
    here. One tiff per image per channel, including Bright Field (BF) and Side Scatter (SSC), is going to be generated.*

IDEAS® (Amnis Millipore Sigma) User Guide can be found at: <https://www.luminexcorp.com/imagestreamx-mk-ii/#documentation>.

Tutorial video for exporting TIFF images in IDEAS is
available.

Example files are provided in the github location "...".

## Instructions for neural network training and prediction

### Installation of python
- For best performance an NVIDIA GPU with CUDA is recommended.

#### Install requirements for TensorFlow
- tensorflow_gpu-1.15.0	3.3-3.7
  - NVIDIA drivers
    - Linux : >= 410.48
    - Windows : >= 411.31
  - cuDNN 7.6 (See below to install with conda)
  - CUDA 10.2 (See below to install with conda)

The steps [below](README.md#create-a-conda-environment) 
install the CUDA libraries during the conda environment setup,
but more information about it are available at these links:
- For more detail about using conda to install CUDA, see this article:
  [Install CUDA with conda](https://towardsdatascience.com/managing-cuda-dependencies-with-conda-89c5d817e7e1)

- For more information regarding installation of CUDA, see this document:
  [NVIDIA CUDA](https://developer.download.nvidia.com/compute/cuda/10.0/Prod/docs/sidebar/CUDA_Quick_Start_Guide.pdf)

### Install miniconda (recommended) or anaconda
We recommend using [conda](https://docs.conda.io/projects/conda/en/latest/)
as an environment and package manager. It easily allows the creation of python
environments with specific version and package needs. If Anaconda
is already installed it will work and the instructions below will be the same.

1. Download [miniconda](https://docs.conda.io/projects/conda/en/latest/) for the used platform.
2. Follow the installation documentation for the target operating system: 
   -  [Windows](https://conda.io/projects/conda/en/latest/user-guide/install/windows.html)
   -  [Linux](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html)
   -  [Mac](https://conda.io/projects/conda/en/latest/user-guide/install/macos.html) 

After installation, open a terminal to start installing packages. On Windows find the
Anaconda Prompt command using the search tool.

### Create a conda environment
Image3C requires version 3.7 of python and TensorFlow version 1.15, so a fresh conda
enviroment is recommended. We have written an environment file that takes care of
creating the conda environment and installing all needed dependencies. If you are on
MacOS or do not have an NVIDA GPU with CUDA use environment.yml. If you are on Windows
or Linux and have a CUDA GPU then use environment_gpu.yml.

Creating the conda environment in this way also installs the correct CUDA
libraries in the conda python environment.

In the following command, a conda environment
named `image3c` is created with python 3.7:

`conda env create -f environment.yml`

if on Windows or Linux with a CUDA gpu

`conda env create -f environment_gpu.yml`

To activate this environment, use this command:
`conda activate image3c`

The Image3C python package is installed during the creation of the conda
environment, so no other installation command are needed.

### Install Image3C from pip
If you do not want to create an environment as described above, Image3C can
be installed with pip:

```pip install image3c```


### How to use the Image3C classifier

The documentation for using the Image3C classifier is in jupyter notebooks that can be downloaded to run on local workstations.

Jupyter notebooks giving details about training and predicting
data from the ImageStream can be found here:

[Notebooks](https://github.com/stowersinstitute/LIBPB-1390-Image3C/tree/master/4-Classifier)

### Dowload classifier data

To obtain the notebooks, this git repository can be cloned:

```git clone git@github.com:stowersinstitute/LIBPB-1390-Image3C.git```

or zip files containing the notebooks can be downloaded from the Stowers Original Data Repository ftp site.

The notebooks used in the example notebooks can be found on the original data ftp for the paper:

[Classifier Notebooks](ftp://odr.stowers.org/LIBPB-1390)

The notebooks and all of the data used in the classifier example can be downloaded here (3.3 GB):

[Classifier Notebooks and Data](ftp://odr.stowers.org/LIBPB-1390) (3.3 GB)

#### Links to individual classifier notebooks:

- [Image Pre-processing](4-Classifier/image_preprocessing.ipynb)
- [Training the Classifier](4-Classifier/training_the_classifier.ipynb)
- [Performance Evaluation](4-Classifier/performance_testing.ipynb)
- [Predicting a new dataset](4-Classifier/predict_new_dataset.ipynb)

