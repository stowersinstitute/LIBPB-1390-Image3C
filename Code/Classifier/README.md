# Instructions for training and prediction

## Installation of python
- For best performance an NVIDIA GPU with CUDA is recommended

### Install requirements for TensorFlow
- tensorflow_gpu-1.15.0	3.3-3.7
  - NVIDIA drivers
    - Linux : >= 410.48
    - Windows : >= 411.31
  - cuDNN 7.6 (See below to install with conda)
  - CUDA 10.0 (See below to install with conda)

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
enviroment is recommended. In the following command, a conda environment
named `image3c` is created with python 3.7:

`conda create -n image3c python=3.7`

To activate this environment, use this command:
`conda activate image3c`

### Install the CUDA libraries with conda

The classifier portion of Image3c was built using TensorFlow version 1.15, and
this requires CUDA 10.0 and cuDNN 7.6. Fortunately these libraries can be
installed with conda. 
The commands to install CUDA with conda are as follows:

1. `conda install cudatoolkit=10.0.130`
2. `conda install cudnn=7.6.0`

For more detail about using conda to install CUDA ee this article:
[Install CUDA with conda](https://towardsdatascience.com/managing-cuda-dependencies-with-conda-89c5d817e7e1)

For more information regarding installation of CUDA, see this document:
[NVIDIA CUDA](https://developer.download.nvidia.com/compute/cuda/10.0/Prod/docs/sidebar/CUDA_Quick_Start_Guide.pdf)


### Install tensorflow and other packages with pip
The python package manager pip can be install tensorflow and it's dependencies.
- should have a requirements.txt file

### How to crop and resize images

### How to run training
- path to training data
- parameters to set
- where to save stuff

### How to infer
