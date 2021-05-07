import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelBinarizer

def cluster_to_classes(idfile):
    '''Convert the cluster id from Vortex clustering to class id for training
    
    Parameters
    ----------
    idfile : str
        path to file with cluster ids

    Returns:
    --------
    labels : array
        1-d array with class labels
        
    '''
    df = pd.read_csv(idfile, usecols=[0,1,2,4,5])
    clusters = np.array(sorted(df.ClusterID.unique()))
    classes = list(np.arange(clusters.min(), clusters.max() + 1))
    b = LabelBinarizer()
    b.fit(classes)
    labels = b.transform(df.ClusterID)
    return labels