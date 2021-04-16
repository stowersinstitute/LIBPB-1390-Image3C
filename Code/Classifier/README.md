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

### Install the cuda stuff with conda

The classifier portion of Image3c was built using TensorFlow version 1.15.
This requires CUDA 10.0 and cuDNN 7.4. Fortunately these libraries can be
installed with conda. For more detail see this article:

[Install CUDA with conda](https://towardsdatascience.com/managing-cuda-dependencies-with-conda-89c5d817e7e1)







### Install tensorflow and other packages with pip
- should have a requirements.txt file

### How to crop and resize images

### How to run training
- path to training data
- parameters to set
- where to save stuff

### How to infer
