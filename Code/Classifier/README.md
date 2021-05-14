# Instructions for training and prediction

## Installation of python
- For best performance an NVIDIA GPU with CUDA is recommended

### Install requirements for TensorFlow
- tensorflow_gpu-1.15.0	3.3-3.7
  - NVIDIA drivers
    - Linux : >= 410.48
    - Windows : >= 411.31
  - cuDNN 7.6 (See below to install with conda)
  - CUDA 10.2 (See below to install with conda)

The steps below install the CUDA libraries during the conda environment setup,
but if you want more information about it see these links:
- For more detail about using conda to install CUDA ee this article:
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

### How to crop and resize images

### How to run training
- path to training data
- parameters to set
- where to save stuff

### How to infer
