import pims
from pims.bioformats import BioformatsReader
import numpy as np


class cifreader:
    
    def __init__(self, filename, channels):
        self.filename = filename
        self.channels = channels
        self.cif = BioformatsReader(filename)
        
        self.nseries = self.cif.size_series

    def get_image(self, series):
        self.cif.series = series
        shape = (len(self.channels),
                 self.cif.sizes['y'],
                self.cif.sizes['x'],
        )
        self.cif.bundle_axes = ['y', 'x']
        self.cif.iter_axes = 'c'
        image = np.zeros(shape, dtype=np.uint16)
        for i, c in enumerate(self.channels):
            image[i] = self.cif.get_frame(c)
        return image