#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


requirements = [
#tensorflow==1.15
    "numpy",
    "scikit-learn",
    "scikit-image",
    "tifffile",
    "matplotlib",
    "pandas",
    "traitlets",
    "pygments",
    "appnope",
    "backcall",
    "decorator",
    "jedi>=0.16",
    "pexpect>4.3",
    "pickleshare",
    "prompt-toolkit!=3.0.0,!=3.0.1,<3.1.0,>=2.0.0",
    "jupyter",
    "ipython",
]

#with open('requirements.txt') as f:
#    for line in f:
#        stripped = line.split("#")[0].strip()
#        if len(stripped) > 0:
#            requirements.append(stripped)


setup(
    name='image3c',
    version="0.1.4",
    author='Chris Wood',
    author_email='cjw@stowers.org',
    license='Apache Software License 2.0',
    url='https://github.com/stowersinstitute/LIBPB-1390-Image3C',
    description='Classifier for Image3c',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6,<3.8',
    #install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
)
