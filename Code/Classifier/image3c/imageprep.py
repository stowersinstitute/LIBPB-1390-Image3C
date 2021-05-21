""" Use this module to prepare a tif series of FlowSight images for use with 
Tensorflow.  
"""
import os
import sys
import pickle

import numpy as np
#from matplotlib import pyplot as plt
from skimage import filters, io
from skimage.measure import label, regionprops
import tifffile
import logging 

logging.disable(30)

def readtiff(xdir, filename):
    """Just reads the tiff stack and returns a numpy array of the whole thing
    
    Parameters
    ----------
    filename : str
        The path to the image
    
    Returns
    -------
    mx : int
        The 
    stack : numpy array
        A numpy array of the image stack
    """
    
    if not xdir.endswith("/"):
        xdir = xdir + "/"

    filename = xdir + filename
    img = tifffile.imread(filename)
    mx = np.amax(img)
    mn = np.amin(img)
    return mn, mx, img

def pad_image(size, image, background):
    '''Create an image of size, either crop or pad

    Parameters
    ----------
    size : int
        the width and height of the final square image
    image : array
        the 2D input image
    background : float
        the background value for the image if padded

    Returns
    -------
    pad : array
        the padded or cropped image of shape (size, size)
    '''
    pad = np.zeros((256, 256), dtype=np.float32)
    pad += background

    h, w = image.shape
    x = 128 - w//2
    y = 128 - h//2

    try:
        pad[y:y+h, x:x+w] = image
    except:
        print('Could not create padded image', image.shape)

    return pad[128 - size//2:128 + size//2, 128 - size//2: 128 + size//2]

def parse_for_channels(filenames):
    '''Add docs
    '''
    channels = set()
    for f in filenames:
        try:
            numstart = f.index('_Ch') + 3  # where channel number starts
            num_end = f.index('.ome.tif')  #one past the last of the channel
            channel = int(f[numstart:num_end])
            channels.add(channel)
        except Exception as e:
            pass

    res = sorted(list(channels))
    return res

def get_image_dict(xdir, filename):
    '''Parses the filename for metadata, reads the image and returns a dict
    Specific to tiff files exported from ImageStream

    Parameters
    ----------
    xdir : str
        path to the image file
    filename : str
        name of the image file

    Returns
    -------
    dict
        index : int
            the index from the imagestream
        channel : int
            image channel from the filename
        filename : str
            filename from input parameter
        image : array
            the image pixels 
        min : float
            the image minimum
        max : float
            the image maximum
    '''
    try:
        numstart = filename.index('_Ch') + 3  # where channel number starts
        num_end = filename.index('.ome.tif')  #one past the last of the channel
        channel = int(filename[numstart:num_end])

        s_ = filename.split("_")
        id = int(s_[-2])

        mn, mx, img = readtiff(xdir,  filename)

    except Exception as e:
        channel = None
        id = None
        img = None
        mn = None
        mx = None
        return None
    return {'index': id, 'channel': channel,
                    'filename': filename,'image': img, 'min':mn, 'max':mx}

def get_images(xdir, images, chmap):
    '''Read image files and return a dictionary of channel images

    Parameters
    ----------
    xdir : str
        Path to the directory for the image file
    images: list
        List of image filenames

    Returns
    -------
    image_dict : dict
        key : int
            index corresponding to the imagestream id
        value : dict
            dictionary of channel image dicts from get_image_dict()
    '''
    images = sorted(images)
    image_dict = dict()
    #chmap = {1: 0, 2: 1, 6: 2, 7: 3, 11: 4}

    for ff in images:
        if not ff.endswith('.tif'):
            continue
        td = get_image_dict(xdir, ff)
        if td is None:
            continue
        ch = td['channel']
        index = td['index']
        if index in image_dict:
            image_dict[index][chmap[ch]] = td
        else:
            image_dict[index] = dict()
            image_dict[index][chmap[ch]] = td
    return image_dict

def form_image_array(image_dict, h, w, channel_map):
    '''Creates an array of all images in image_dict
    
    Parameters
    ----------
    image_dict : dict
        key : int
            index of the image
        value : dict
            dictionary from get_image_dict()

    Returns
    -------
    a : array
        the multichannel image array of shape (n, h, w, channels)
    index_dict : dict
        key: int
            enumerated index over the keys in image_dict
        value : int
            index of the image from imagestream
    '''

    n = len(image_dict)
    nc = len(channel_map)
    a = np.zeros((n, h, w, nc), dtype=np.float32)
    print(a.shape)
    indexes = sorted(image_dict.keys())
    index_dict = dict()
    for idx, index in enumerate(indexes):
        index_dict[idx] = index
        channel_images = image_dict[index]
        for kx in channel_images.keys():
            img = channel_images[kx]
            b = img['image']

            if kx in [0,3]:
                imax = np.max(b)
                imin = np.min(b)
                b1 = (b - imin)/(imax - imin)
            else:
                imax = np.max(b)
                imin = np.min(b)
                b1 = (b - imin)/(imax - imin)

            if kx in [0, 3]:
                bg = np.mean(b1)
            else:
                bg = np.amin(b1)
            b2 = pad_image(64, b1, bg)

            a[idx, :, :, kx] = b2

    return a, index_dict

def process_tifs(xdir, outdir='ImagesToTrain'):
    '''Iterates over tiff files in a folder and writes a numpy memmap file. Dictionary
    mapping the enumeration index of each file to it's ID name is written to a python
    pickle file.
    
    Parameters
    ----------
    xdir : str
        Path of the folder to process
    outdir : str
        Path to a folder to save the memmap. It will be created if if does
        not exist. Default ./ImagesToTrain
    '''

    if not outdir.endswith('/'):
        outdir += "/"
        
    imagefiles = os.listdir(xdir)
    channels = parse_for_channels(imagefiles)
    cdict = {c:i for i,c in enumerate(channels)}
    image_dict = get_images(xdir, imagefiles, cdict)
    a, index_dict = form_image_array(image_dict, 64, 64, cdict)
    
    maxis = np.amax(a, axis=(0,1,2))
    if outdir == None:
        outdir = "ImagesToTrain"

    try:
        if not os.path.exists(outdir):
            os.makedirs(outdir)
    except:
        print('Cannot make', outdir)
        pass

    if xdir.endswith("/"):
        xdir2 = xdir[:-1]
    else:
        xdir2 = xdir

    mm_name = "_".join(xdir2.split("/")[-2:])
    mm_file = outdir + mm_name + ".npy"

    pklname = mm_name + "_index.pkl"

    with open(pklname, mode='wb') as pkl:
        pickle.dump(index_dict, pkl)

    np.save(mm_file, a)
    #mmheader = np.memmap(mm_file, dtype='int32', mode='w+', shape=(4,))
    #mmheader[0] = len(image_dict)
    #mmheader[1] = 64
    #mmheader[2] = 64
    #mmheader[3] = a.shape[-1] 

    #mmheader.flush()
    #del mmheader

    #shape =a.shape #(len(image_dict), 64, 64, 5)
    #mmdata = np.memmap(mm_file, dtype=np.float32, offset=128,
    #                   mode='r+', shape=shape)

    #mmdata[:, :, :, :] = a
    #mmdata.flush()
    #del mmdata


def runscan(dir, dirs):
    """ a recursive method that finds tif files in a directory
    structure
    
    Parameters
    ----------
    dir : string 
        The path of the root directory to search
    
    dirs : list
        A list that will contain all ot the directories that have
        tiffs in the structure 
    Returns
    -------
    
    Nothing, use the input list dirs as the result
    """
    with os.scandir(dir) as scan:
        for entry in scan:
            if entry.is_dir():
                runscan(entry.path, dirs)
            else:
                if entry.name.endswith(".tif"):
                    dirs.append(dir)
                    return

def run(topdir, outdir):
    dirs = list()
    runscan(topdir, dirs) 
    for i, d in enumerate(dirs):
        print("Starting: ", i, d)
        process_tifs(d, outdir)

if __name__ == '__main__':

    print(sys.argv)
    if len(sys.argv) > 1:
        topdir = sys.argv[1]
        outdir = sys.argv[2]
    else:
        topdir = os.getcwd()
        outdir = os.getcwd()

    if outdir == '.':
        outdir = os.getcwd()
    ## dirs is an empty list that will be filled in runscan
    dirs = list()

    ## runscan starts from the top directory and finds all tifs
    runscan(topdir, dirs) 
    for i, d in enumerate(dirs):
        print("Starting: ", i, d)
        process_tifs(d, outdir)
