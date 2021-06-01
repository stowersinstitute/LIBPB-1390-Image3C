# Step-by-step instructions for running Image3C analysis

## Data acquisition on the Imagestream

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

5.  More information about sample preparation and data collection can be
    found in the related manuscript.

More information about the Imagestream®^X^ Mark II (Amnis Millipore
Sigma) and how to use it can be found at:

<https://www.luminexcorp.com/imagestreamx-mk-ii/#documentation>

A dataset is provided as example in the github location "...". These RIF
files have been saved directly from the Imagestream after running ...
replicate for each of the ... analyzed conditions.

**Data normalization** **and feature value** **calculation** **in**
**IDEAS**

1.  Open IDEAS software (link, free for download once an Amnis user
    account is created)

2.  Perform color compensation according to the software documentation.

3.  Apply the color compensation to all the RIF files using the batch
    analysis method. It can be done leaving the "daf file" blank if you
    just wish to compensate (you will create the daf file which contains
    regions and feature values next).

4.  Select a representative sample that contains all labels and use this
    to create masks. Make masks in the following manner (see the IDEAS
    documentation for more info how the specific steps for creating
    masks).

    1.  *For texture features, use a mask that encompasses the whole
        cell such as adaptive erode on bright field channel. Note, you
        can* *use that same mask to calculate texture features for other
        channels, even though it's created using brightfield signal.*

    2.  *For shape features, use a mask that captures the shape of the
        signal* *such as a "morphology" mask.*

    3.  *For side scatter, create a mask that includes the "spots" of
        intensity that are often seen with this channel. But a
        "morphology" mask is adequate if you're unsure.*

5. Calculate feature values that describe size, shape, texture, and
    intensity for any channels/dyes of interest. *[Important]{.ul}:*
    *The* *exact complement* *of features used is not critical since
    typically many features have overlapping information content* *and
    we will remove the* *redundant* *once later in the analysis.* *We
    suggest* *capturing attributes from these major classes:* *size,
    shape, texture, and* *intensity.* *The "feature finder" can be used
    to create multiple features* *at once based on channel and type of
    feature (shape, area, texture, intensity). Refer to the
    documentation for use of the feature finder. Once done, save the
    analysis which will create the daf file you'll use for batching the
    rest of the* *files.*

6.  Do a batch analysis to apply this new DAF file to all samples
    (calculates features for all files). This can be done by saving the
    previous file once features are calculated and closing the file
    (leave IDEAS open). Then go to "tools -\> batch", and click "add
    batch". Add all the cif files (or rif files if not yet compensated),
    select the daf file you just made above as the daf template. If
    running on rif files, choose the daf file from before, or a ctm or
    cif file, as compensation matrix. Click add back and click "Run
    Batch".

7.  Export all feature values as FCS files (per-object feature matrices)
    in batch. See "tools" and "export feature values". Choose the
    population to export (must match other work in this process, e.g.
    nucleated cells), select the feature to export, select "fcs file" as
    type. *[Important]{.ul}:* *At the end you want* *to have* *a DAF
    file, a CIF file and a FCS file, each of them* *including exactly*
    *the* *same subset of events. For example,* *if you export only
    nucleated events* *for the* *FCS* *file, generate also* *a CIF file
    and a DAF file* *with the exact same population. This will become
    important later when* *we will use FCS Express.*

More information about feature descriptions and selection can be found
in the related manuscript.

Tutorial video for calculating feature values in IDEAS is available in
the github location "..."

IDEAS® (Amnis Millipore Sigma) User Guide can be found at:

<https://www.luminexcorp.com/imagestreamx-mk-ii/#documentation>

CIF and DAF files for all the files of the dataset we provided as
example are in the github location "...".

## FCS file pre-processing in R for clustering 

1.  Install the newest version of R and R Studio.
    <https://cran.r-project.org>

2.  Install the following R packages: flowCore, flowStats, ggcyto,
    ggridges, stringr, Hmisc, caret, pheatmap, reshape2, data.table,
    RColorBrewer, edgeR, plyr, ggplot2, pastecs, igraph.

3.  Create R studio project in a folder containing your FCS files
    exported from IDEAS.

4.  Open the script called \"1_processFcsFiles.R\" in the github
    location "... Code". 

5.  Run the code line by line. *[Important]{.ul}:* *Comments will*
    *suggest you* *where* *changes should be made based on your
    specific* *dataset* *to accommodate differences between experiments,
    files, etc. For example, you* *will need to make and read-in a*
    *CSV* *file called \"RowLabels.csv\" at line 59 for use in
    annotations. This has to exactly* *match your sample names. See the
    example files in the github location
    \\LIBPB-1390-Image3C\\1-ProcessFcsFiles\\processing\\RowLabels.csv
    and* *a full set of example files from this section.*
	
6.  Trim redundant features with high correlation values to each other
    (line ...).

7.  Identify and remove outlier samples (line ...).

8.  Transform fluorescence intensity values with estimateLogicle() and
    transform() functions (line ...).

9.  Normalize and scale/center DNA intensity using gaussNorm() function
    (line ...). *[Important]{.ul}:* *Although it* *is possible to
    normalize out all* *your results, we* *prefer to use only for DNA
    content staining drift correction, where the true nature of 2N and
    4N peaks is known and can be judged whether you have changed the
    underlying nature of distributions.* *This normalization can also be
    used for antibody staining drift but use caution* *in deciding if
    this is a result of staining \'drift\'* *or a* *real intensity
    difference* *between samples.* 

10. New FCS files are exported at the end of the script with
    \"\_processed.fcs\" appended to the end using writeflowSet()
    function (line ...). These files will be imported into VorteX
    Clustering Environment/Xshift for clustering.

Example files that are required in the code and example files that
should be obtained running this code are provided in the github location
"...".

The new FCS files for the example dataset we provided are in the github
location "...".

## Clustering the events in VorteX Clustering Environment/Xshift 

1.  Install VorteX Clustering Environment from here:
    <https://github.com/nolanlab/vortex/releases>

2.  Import your processed FCS files. Apply import settings of your
    preference but you shouldn't need to apply any transformation since
    this was done in R for fluorescent parameters.

3.  Run X-Shift k-nearest-neighbor clustering with K (number of nearest
    neighbors) across a range of values from approximately 10 to 150.
    Select all clusters, choose validation and find elbow point for
    cluster number. Or let the software auto-select the range of K
    values from the data.

4.  Select the clustering result with the desired value for K. To do
    this, click-shift to select all resulting clusterings for all K
    values, right click and choose "find elbow point for cluster
    number". This is based on an optimization for finding an appropriate
    cluster number. Refer to the Xshift publication for details.

5.  Right click in the top-right list of clusters and choose \"create
    graph -\> force directed layout (FDL)\". Specify the number of
    events per cluster you want to use. Use enough data points so that
    rare populations contain several events. This depends on the data.

6.  Let it run until it reaches equilibrium. You will see points no
    longer moving significantly. It may take minutes to hours depending
    on data size to reach this point.

7.  You can visually attempt to evaluate at this step if you have
    over-clustered. If you see one 'blob' population that's comprised of
    multiple clusters (by color) thean you may find the data is
    over-clustered. In such a case, it may be advantageous to select a K
    value that produces fewer clusters.

8.  Stop the layout and run \"export graph as graphml\" and \"export
    cell coordinates\" below. Save the files as \"FDL.graphml\" and
    \"FDL_coords.csv\" respectively. If you would like, you can export
    images, but we will plot this in R.

9. Back in the main Vortex windows, right click your cluster result in
    the bottom left window and select \"Export as csv\". Save this file
    as \"ClusterIDs.csv\".

10. Right click the cluster result again and choose \"Computer group
    stats per cluster\". Select all in the results, copy and paste to
    excel and save this file as \"GroupStatsPerCluster.csv\".

11. Click into the window at the top right again, select all, copy and
    paste into a new excel sheet. Save this as
    \"ClusterFeatureAverages.csv\".

12. You should have the following tabular data items now coming from
    Vortex:

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
available in the github location "..."

Instructions for using VorteX Clustering Environment can be found at:

<https://github.com/nolanlab/vortex/wiki/Getting-Started>

Example files that should be obtained at the end of the analysis in
VorteX Clustering Environment are provided in the github location "...".

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
    Express in the next steps.

7.  Split (in the R script) the merged clustering results back into
    original files coping the new CSV files generated (one per sample)
    into a new folder to be used in the next section. These CSV files
    contain feature values per sample, cluster ID, FDL plot coordinates
    and spanning tree plot coordinates per each cell (or data point).
    This data can be merged into data and images within the DAF files in
    FCS Express using the \"R add parameters\" transformation option and
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

## Data exploration and event visualization in FCS Express

1.  Open FCS Express.

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
    spanning tree plots in FCS Express, that can then be used for gating
    to show image galleries.

6.  Open a DAF file in FCS Express.

7.  Rename the corresponding CSV file \"Template.csv\". We suggest to
    make a copy first and rename that, keeping the set with original
    names.

8.  In FCS Express, go to Tools -\> Transformations -\> R add parameters
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

Tutorial video for exploring and visualizing data in FCS Express is
available in the github location "..."

Instructions for using FCS Express can be found at ...

Example files that should be obtained at the end of the analysis in FCS
Express are provided in the github location "...".

## Exporting tiff images for neural network training & analysis

1.  Export/open raw images (RIF files) by selecting the Tools menu at
    the top of the screen and then "export tiff images". In the dialog,
    select the population (gate) that matches what was used for previous
    analysis, then choose 16-bit and raw options from the radio buttons.

2.  Ensure you have a strategy for managing file names and directories,
    the tiff images will be pre-pended according to the name specified
    here. You will get 1 tiff per image channel including BF and SSC.


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
but if you want more information about it see these links:
- For more detail about using conda to install CUDA see this article:
  [Install CUDA with conda](https://towardsdatascience.com/managing-cuda-dependencies-with-conda-89c5d817e7e1)

- For more information regarding installation of CUDA, see this document:
  [NVIDIA CUDA](https://developer.download.nvidia.com/compute/cuda/10.0/Prod/docs/sidebar/CUDA_Quick_Start_Guide.pdf)

### Install miniconda (recommended) or anaconda
We recommend using [conda](https://docs.conda.io/projects/conda/en/latest/)
as an environment and package manager. It will allow easily creating python
environments with specific version and package needs. If you already have Anaconda
installed it will work and the instructions below will be the same.

1. Download [miniconda](https://docs.conda.io/projects/conda/en/latest/) for your platform.
2. Follow the installation documentation for the target operating system: 
   -  [Windows](https://conda.io/projects/conda/en/latest/user-guide/install/windows.html)
   -  [Linux](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html)
   -  [Mac](https://conda.io/projects/conda/en/latest/user-guide/install/macos.html) 

After installation, open a terminal to start installing packages. On Windows find the
Anaconda Prompt command using the search tool.

### Create a conda environment
Image3c requires version 3.7 of python and TensorFlow version 1.15, so a fresh conda
enviroment is recommended. We have written an environment file the takes care of
creating the conda environment and installing all needed dependencies. If you are on
MacOS or don't have an NVIDA GPU with CUDA use environment.yml. If you are on Windows
or Linux and have a CUDA GPU then use environment_gpu.yml

Creating the conda environment in this way also installs the correct CUDA
libraries in the conda python environment.

In the following command, a conda environment
named `image3c` is created with python 3.7:

`conda env create -f environment.yml`

if on windows or linux with a CUDA gpu

`conda env create -f environment_gpu.yml`

To activate this environment, use this command:
`conda activate image3c`

The image3c python package is installed during the creation of the conda
environment, so no other installation command are needed.

### Install image3c from pip
If you don't want to create an environment as described above, image3c can
be installed with pip:

```pip install image3c```


# How to use Image3c

The main documentation can be found at:
[Image3c Github](https://github.com/stowersinstitute/LIBPB-1390-Image3C/)

Jupyter notebooks giving details about training and predicting
data from the ImageStream and be found here:

[Notebooks](https://github.com/stowersinstitute/LIBPB-1390-Image3C/tree/master/4-Classifier)

Links to classifier notebooks:

- [Image Pre-processing](4-Classifier/image_preprocessing.ipynb)
- [Training the Classifier](4-Classifier/training_the_classifier.ipynb)
- [Performance Evaluation](4-Classifier/performance_testing.ipynb)
- [Predicting a new dataset](4-Classifier/predict_new_dataset.ipynb)