import os
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn import metrics

### where is the best model checkpoint

cpdir = '' #path to the checkpoint directory
checkpoint = '' #the name of the checkpoint

if not cpdir.endswith('/'):
    cpdir += '/'
    
### where are the images and labels
sval = cpdir.split("/")
valdir = "/".join(sval[0:-2]) + "/"

# load the validation images
val_images = np.load(valdir + 'validation_images.npy')
val_labels = np.load(valdir + 'validation_labels.npy')
val_nums = val_labels.argmax(axis=1)

sess = tf.Session()
#### load the best model and do tf stuff
saver = tf.train.import_meta_graph(cpdir + checkpoint + '.meta')
saver.restore(sess, cpdir + checkpoint)

softmax = sess.graph.get_tensor_by_name('Softmax:0')
images = sess.graph.get_tensor_by_name('Placeholder:0')

vsm = sess.run(softmax, feed_dict={images:val_images})
vsm_nums = vsm.argmax(axis=1)

val_accuracy = metrics.accuracy_score(val_nums, vsm_nums)
print(val_accuracy)
val_cm = metrics.confusion_matrix(val_nums, vsm_nums)

val_report = metrics.classification_report(val_nums, vsm_nums)

print(val_report)
print(val_cm)


