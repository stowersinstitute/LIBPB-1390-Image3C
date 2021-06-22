# Step-by-step instructions for running Image3C analysis

## Data acquisition on the ImageStream

1.  Images of the events of interest should be acquired at the highest
    possible magnification (60x) that fully includes the events in the
    field of view and at a speed of max 1000 cell/min.

2.  About 10,000 nucleated and focused events should be saved for each
    sample and multiple samples should be run as biological replicates
    (4-7 replicates).

3.  Events from single color control samples should be collected for
    each channel used (except for brightfield).  

4.  The power of the lasers should be adjusted to not saturate the
    camera for any cells of interest. This can be verified in the
    acquisition software by plotting 'raw signal intensity' of events of
    interest and checking that raw pixel values are below 4046 for
    cellular events.

More information about sample preparation and data collection can be found in the manuscript “Image3C: a multimodal image-based and label independent integrative method for single-cell analysis” (Accorsi, Peuß, Bow et al., BioRxiv).

More information about the ImageStream Mark II (Amnis Millipore
Sigma) and how to use it can be found at:

<https://www.luminexcorp.com/imagestreamx-mk-ii/#documentation>

A dataset is provided as example at the Stowers Original Data Repository at http://www.stowers.org/research/publications/libpb-1390. These RIF files have been saved directly from the ImageStream after running 5 replicates for each of the 2 analyzed conditions (Females Untreated and Female EDTA Treatment).

**Data normalization** **and feature value** **calculation** **in**
**IDEAS**

1.  Open IDEAS software (Amnis Millipore, free for download once an Amnis user
    account is created)

2.  Perform color compensation following the Wizard and according to the IDEAS documentation.

3.  Apply the color compensation to all the RIF files using the batch
    analysis method.
    
    *Important: leave the option to specify a “DAF file to use as a reference” blank for now.* 

4.  Select a representative sample that contains all labels and use this
    to create masks. Make masks in the following manner (see also the IDEAS
    documentation for more information about creating
    masks).

    a.  *For texture features, use a mask that encompasses the whole
        cell such as adaptive erode on bright field channel. That same mask can be used to calculate texture features for other channels too, even though it was created using brightfield signal.*

    b.  *For shape features, use a mask that captures the shape of the
        signal* *such as a "morphology" mask.*

    c.  *For side scatter, create a mask that includes the "spots" of
        intensity that are often seen with this channel (a
        "morphology" mask is adequate if unsure).*

5. Calculate feature values that describe size, shape, texture, and
    intensity for any channels/dyes of interest. The tool "Feature finder" can be used
    to create multiple features* *at once based on channel and type of
    feature (shape, area, texture, intensity). Refer to the IDEAS documentation for use of the "Feature finder". 
    
    *Important: The exact complement of features used is not critical since
    typically many features have overlapping information content and
   redundant features will be removed later. The suggested attributes to capture are from these major classes:* *size,
    shape, texture, and* *intensity.*
    
6.  Save the analysis and close the file. This step creates the DAF file that will be used for analyzing in batch the rest of the files.


7.  Do a batch analysis to apply the DAF file, saved in the previous step, to all samples
    and to calculate features for all files. For achieving this, go to "Tools -\> Batch -\> Add batch", add all the CIF files, select the DAF file you just saved above as the "DAF file template". Click "Run Batch".

8.  Export in batch all feature values as FCS files. Click "Tools -\> Export feature values". Choose the
    population to export (this must match other work in this process, e.g.,
    nucleated cells), select the features to export, select "fcs file" as
    type. 
    
    *Important: At the end a DAF
    file (tabular data), a CIF file (compensated images) and a FCS file (per-object feature matrices) will be saved. It is important that each of them includes the same subset of events. For example, if a FCS file is exported with only nucleated events, remember to generate also a CIF file and a DAF file with the exact same population. This will become important later in the FCS Express Section.*

More information about feature descriptions and selection can be found in the manuscript “Image3C: a multimodal image-based and label independent integrative method for single-cell analysis” (Accorsi, Peuß, Bow et al., BioRxiv).

Tutorial videos for creating masks and calculating feature values in IDEAS are available in the GitHub location https://github.com/stowersinstitute/LIBPB-1390-Image3C/tree/master/TutorialVideos.

IDEAS® (Amnis Millipore Sigma) User Guide can be found at:

<https://www.luminexcorp.com/imagestreamx-mk-ii/#documentation>

CIF, DAF and FCS files are provided in the GitHub.

## FCS file pre-processing in R for clustering 

1.  Install the newest version of R and R Studio (https://cran.r-project.org, the newest version as of June 2021 works well with all libraries used).

2.  Create an R studio project in a folder containing your FCS files just
    exported from IDEAS.

3.  Open the script called \"1_processFcsFiles.R\" in the github
    location "... Code". 

4.  Run the code line by line to trim redundant features with high correlation values to each other, identify and remove outlier samples, transform fluorescence intensity values with estimateLogicle() and transform() functions, normalize and scale/center DNA intensity using gaussNorm() function and export new FCS files with "_processed.fcs" appended to the end using writeflowSet() function.
  
    *Important: Comments will indicate where changes should be made based on specific datasets to accommodate differences between experiments, files, etc. For example, to make and read-in a CSV file called "RowLabels.csv" is required at line 59 for use in annotations. This has to exactly match the sample names. See the example files in the GitHub location \LIBPB-1390-Image3C\1-ProcessFcsFiles\processing\RowLabels.csv and a full set of example files from this section.*
	
    *Important: Although it is possible to normalize out all the results, it is preferred to use it only for DNA content staining drift correction, where the true nature of 2N and 4N peaks is known and can be judged whether the underlying nature of distributions was changed. This normalization can also be used for antibody staining drift, but use caution needs to be used in deciding if this is a result of staining drift or a real intensity difference between samples.*

A tutorial page using the R markdown tool has been generated and made available as a step-by-step guide.

Example files that are required in the code are provided.

The full set of files that will be generated running this code, including the new FCS files, for the example dataset are provided.

## Clustering the events in VorteX Clustering Environment/Xshift 

1.  Install VorteX Clustering Environment
    <https://github.com/nolanlab/vortex/releases>

2.  Import the processed FCS files. Apply import settings of 
    preference but there should not be the need to apply any transformation since
    this was already done in R for fluorescent parameters.

3.  Run X-Shift k-nearest-neighbor clustering with K (number of nearest
    neighbors) across a range of values from approximately 5 to 150.
    Select all clusters, choose validation, and find elbow point for
    cluster number, or let the software auto-select the range of K
    values from the data.

4.  Select the clustering result with the desired value for K. To do
    this, click-shift to select all results for all K
    values, right click and choose "Find elbow point for cluster
    number". This is based on an optimization for finding an appropriate
    cluster number. Refer to the X-Shift publication for additional details (Samusik et al., 2016 - Automated mapping of phenotype space with single-cell data).

5.  Right click in the top-right list of clusters and choose "Create
    graph -\> force directed layout (FDL)". Based on the data, specify the number of
    events to use per cluster. 
    
    *Important: Use enough data points so that also
    rare populations contain several events.*

6.  Let it run until it reaches equilibrium (when the points are no longer moving significantly). This may take from a few minutes to hours depending on data size.

7.  Evaluate visually if the data have been over-clustered or under-clustered. If one ‘blob’ population comprises multiple clusters (i.e., multiple colors) then the data may be over-clustered. In such a case, it may be advantageous to select a K value that produces fewer clusters. 

8.  Stop the layout and run \"Export graph as graphml\" and \"Export
    cell coordinates\" and save the files as \"FDL.graphml\" and
    \"FDL_coords.csv\" respectively. Images can also be exported, but the same data will be plotted also later in R.

 9. Back in the main Vortex windows, right click the cluster result in
    the bottom left window and select \"Export as csv\". Save this file
    as \"ClusterIDs.csv\".

10. Right click the cluster result again and choose \"Computer group
    stats per cluster\". Select "all" in the results, copy and paste to
    excel and save this file as \"GroupStatsPerCluster.csv\".

11. Click into the window at the top right again, select all, copy and
    paste into a new excel sheet. Save this as
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

Tutorial video for clustering events in Vortex Clustering Environment is
available.

Instructions for using VorteX Clustering Environment can be found at:

<https://github.com/nolanlab/vortex/wiki/Getting-Started>

Example files that should be obtained at the end of the analysis in
VorteX Clustering Environment are provided.

## Analysis of Clustering results in R

1.  Create an R studio project in the folder with the tabular data
    above.

2.  Open the script called \"2_processClusteringResults.R\" in the
    github location "...".

3.  Run the code line by line. *[Important]{.ul}: Specify number of
    conditions in line 261.*

4.  Perform statistical analysis between conditions customizing the
    section under GLM method line 278 based on your variables. The
    purpose is to perform negative binomial modeling on cell counts per
    cluster between conditions of interest to find changes in cluster
    abundance between groups or variables.

5.  Save any desired plots manually in R studio (Force directed layout
    FDL plots are saved automatically for each condition).

6.  Make notes of any cluster abundance statistically significantly
    different between groups or variables. These can be displayed in FCS
    Express Plus in the next steps.

7.  Split (in the R script) the merged clustering results back into
    original files coping the new CSV files generated (one per sample)
    into a new folder to be used in the next section. These CSV files
    contain feature values per sample, cluster ID, FDL plot coordinates
    and spanning tree plot coordinates per each cell (or data point).
    This data can be merged into data and images within the DAF files in
    FCS Express Plus using the \"R add parameters\" transformation option and
    provided script. (see the section below)

8.  These data can be used to visualize Feature Values by Clusters and
    to plot FDL colored by cluster IDs.

9. Save R script to any edits made are captured and can be used to
    quickly re-process again later.

Example files that are required in the code and example files that
should be obtained running this code are provided in the github location
"...".

The final CSV files for the example dataset we provided are in the
github location "...".

## Data exploration and event visualization in FCS Express Plus

1.  Open FCS Express Plus. 

2.  Under File -\> options -\> startup, make sure \"Start the De Novo
    Software application external application bridge on login\" is
    selected.

3.  Restart FCS Express.

4.  Open the R script called \"3_AddClusterIDs_FCSe.R\" in the github
    location "..." and ensure any file paths point to the folder where
    your last CSV files are located.

5.  Important - be sure that line 42 is taking columns 1, 4, and then
    the last four columns (6 total) from your CSV files. This will
    ensure we can merge in the cluster IDs and plot coordinates into the
    DAF files. The last four columns will have different column number
    based on the total number of features in the csv file. This is why
    specifying these column numbers is important, because we want to get
    the last four columns which contain "FDL-X", "FDL-Y", "MST-X" and
    "MST-Y" columns. For plotting force direct plots and minimum
    spanning tree plots in FCS Express Plus, that can then be used for gating
    to show image galleries.

6.  Open a DAF file in FCS Express Plus.

7.  Rename the corresponding CSV file \"Template.csv\". We suggest to
    make a copy first and rename that, keeping the set with original
    names.

8.  In FCS Express Plus, go to Tools -\> Transformations -\> R add parameters
    ("R integration" feature).

9.  Point it to the \"3_AddClusterIDs_FCSe.R\" script and select
    \"object number\" for export. Ensure \"events as rows\" is checked.

10. Drag the transformation to a plot, it should run and generate two
    test files (just for debugging) in the folder with the CSV files
    called \"NewMatrix\" and \"OrigMatrix\". If these are not made, the
    code is not running properly. Check all the above steps carefully.

11. New parameters now are available for ClusterID, FDL-X, FDL-Y, MST-X
    and MST-Y.

12. Images of events in a given cluster or position in MST or FDL plots
    can now be displayed in a data grid for cluster annotation or for
    making figures. Subsets of events can be gated, and the
    corresponding images can be displayed. This data can be used to
    visualize Cell Images by Clusters. You can plot feature values,
    clustering results and FDL.

Tutorial video for exploring and visualizing data in FCS Express Plus is
available in the github location "..."

Instructions for using FCS Express Plus can be found at ...

Example files that should be obtained at the end of the analysis in FCS
Express Plus are provided in the github location "...".

## Exporting tiff images for neural network training and analysis

1.  Export/open raw images (RIF files) by selecting the Tools menu at
    the top of the screen and then "Export tiff images". In the dialog,
    select the population (gate) that matches what was used for previous
    analysis, then choose 16-bit and raw options from the radio buttons.

2.  Ensure you have a strategy for managing file names and directories,
    the tiff images will be pre-pended according to the name specified
    here. You will get one tiff per image channel including Bright Field (BF) and Side Scatter (SSC).


## Instructions for training and prediction

### Installation of python
- For best performance an NVIDIA GPU with CUDA is recommended

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
- For more detail about using conda to install CUDA see this article:
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
enviroment is recommended. We have written an environment file the takes care of
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
data from the ImageStream and be found here:

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

