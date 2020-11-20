import os
import shutil
import sys
from datetime import datetime
import network

import numpy as np
from matplotlib import pyplot as plt
import sklearn.metrics as metrics
import time

def run(params):

    ### keep image size at 32 and original width (ow) at 64 for now
    for k, v in params.items():
        print("{:15s}: {}".format(k, v))
        
    c = network.get_classifier(params['datafile'], params['labelsfile'],
                               32, 5, params['clusterlist'],
                               channels=params['channels'],
                               ow=64, combine=params['combine'])
    
    try:
        shutil.rmtree(params['tensorboard_log_dir'])
        print('deleted logs')
    except:
        print("couldn't delete")
        
    time.sleep(4)
    while os.path.exists(params['tensorboard_log_dir']):
        shutil.rmtree(params['tensorboard_log_dir'])
        time.sleep(.1)

    if not os.path.exists(params['CheckpointDir']):
        os.makedirs(params['CheckpointDir'])
    np.save(params['CheckpointDir'] + "validation_images.npy", c.val_images)
    np.save(params['CheckpointDir'] + "validation_labels.npy", c.val_labels)
    c.train(n_iter=params['iterations'], learning_rate=params['learning_rate'],
            droprate=params['droprate'], l2f=params['l2f'],
            batchsize=params['batchsize'],
            checkpoint_dir=params['CheckpointDir'])

    # run all validation images
    vl, vsm, vlb, vcm = c.sess.run([c.loss, c.softmax, c.label_batch, c.confmat],
                        feed_dict={c.image_batch:c.val_images,
                                    c.label_batch:c.val_labels,
                                    c.is_training:False})


    #tl.shape, np.argmax(vsm, axis=-1).shape
    tls = np.argmax(c.val_labels, axis=-1)
    vsms = np.argmax(vsm, axis=-1)


    print(metrics.classification_report(tls, vsms))
    print(metrics.accuracy_score(tls, vsms))

    cm = metrics.confusion_matrix(tls, vsms)
    #cm = cm/cm.sum(axis=1)
    #import pandas as pd
    #cmdf = pd.DataFrame(cm)
    np.set_printoptions(precision=3)
    print(cm)
    print(cm.sum(axis=0, keepdims=True))
    print(cm.sum(axis=1, keepdims=True))
    print(cm.sum(axis=0).sum())
    print(cm.sum(axis=1).sum())
    print(cm.sum())
    print()
    print(metrics.confusion_matrix(tls, vsms))

    all_images = c.orig_images
    all_labels = c.orig_labels

    xm = all_images.mean(axis=(1,2), keepdims=True)
    sm = all_images.std(axis=(1,2), keepdims=True)
    all_images = (all_images - xm)/sm

    all_loss, all_sm, _, _ = c.sess.run([c.loss, c.softmax, c.label_batch, c.confmat],
                        feed_dict={c.image_batch:all_images,
                                    c.label_batch:all_labels,
                                    c.is_training:False})



    np.set_printoptions(precision=3)
    print(metrics.classification_report(all_labels.argmax(axis=-1), all_sm.argmax(axis=-1)))
    print(metrics.accuracy_score(all_labels.argmax(axis=-1), all_sm.argmax(axis=-1)))
    cm = metrics.confusion_matrix(all_labels.argmax(axis=-1), all_sm.argmax(axis=-1))

    print(cm)

    np.save(params['CheckpointDir'] + 'all_sm_pickle.pkl', all_sm)
    
    dtnow = datetime.now().timetuple()
    dtstring = '{}-{:02d}-{:02d}-{:02d}-{:02d}'.format(*dtnow[:5])
    with open(params['CheckpointDir'] + 'desc.txt', 'a+') as f:
        f.write('{:20s}: {}'.format(dtstring, params['description']))
        f.write('\n')
    



