import os
import sys
import argparse
import time
from datetime import datetime

import numpy as np
import pandas as pd
import tensorflow as tf

class Classifier:
    def __init__(self, datafile, labelsfile, w, nc, cnums,
                 offset=0, ow = 64, channels=None,
                dtype=np.float32, label_offset=0,
                combine=None):

        self.ow = ow
        self.w = w
        self.nc = nc
        self.nfilters = 8
        
        self.offset = offset
        self.channels = channels
        self.label_dtype = dtype
        self.label_offset = label_offset
        _images = np.load(datafile) # self.readmm(datafile, w=ow)
        if self.channels is None:
            self.channels = list(range(_images.shape[-1]))

        _images = self.crop(_images)
        _labels = np.load(labelsfile)
        #_labels = self.read_labels_mm(labelsfile, _images)

        if len(combine) > 0:
            for b in combine:
                _labels = self.combine_classes(b[0], b[1], _labels)

        print(_labels.shape, _labels.argmax(axis=1))
        self.orig_images = _images.copy()
        self.orig_labels = _labels.copy()
        
        self.images, self.labels = self.permute_data_and_labels(_images, _labels)

        self.label_nums = np.argmax(self.labels, axis=1)        

        cilist = list()
        cllist = list()

        print(self.labels.shape)
        print("reducing classes")
        for i, c in enumerate(cnums):
            cl = self.label_nums == c
            ci = self.images[cl]
            lc = np.zeros((ci.shape[0], len(cnums)), dtype=np.float32)
            ohv = np.zeros(len(cnums), dtype = np.float32)
            ohv[i] = 1
            lc[:] = ohv
            cilist.append(ci)
            cllist.append(lc)

        x_images = np.concatenate(cilist, axis=0)
        x_labels = np.concatenate(cllist, axis=0)        
        self.images, self.labels = self.permute_data_and_labels(x_images, x_labels)
        
        self.label_nums = np.argmax(self.labels, axis=1)        
        self.normalize()
        print('Done normalzing')
        self.nclasses = self.labels.shape[1]
        self.nclusters = self.label_nums.max() + 1
        self.set_ttv(.8, .1, .1)
        print('ok to train')

    def combine_classes(self, c1, c2, labels):
        nc = labels.shape[1]
        v1 = np.zeros((nc,), dtype=np.float32)
        v2 = np.zeros((nc,), dtype=np.float32)

        v1[c1] = 1.
        v2[c2] = 1.
        cx = labels.argmax(axis=1)

        wx1 = np.where(cx == c1)
        wx2 = np.where(cx == c2)
        new_labels = labels.copy()
        new_labels[wx2] = v1
        new_labels = np.delete(new_labels, c2, 1)

        return new_labels
    
    def crop(self, x):
        crop0 = (self.ow - self.w)//2
        crop1 = (crop0 + self.w)
        sy = slice(crop0, crop1)
        sx = slice(crop0, crop1)
        x = x[:,sy, sx, self.channels]
        return x

    def readmm(self, datafile, w=64, nc=5):
        mmh = np.memmap(datafile, dtype=np.int32, offset=0, shape=(4,))
        if mmh[1] == 64 and mmh[2] == 64:
            offset = 128
            shape = mmh[:]
        else:
            offset = 0 
            shape = 0
        del mmh

        if offset == 0:
            mm = np.memmap(datafile, dtype=np.float32, offset=self.offset)
            mm = mm.reshape((-1, self.ow, self.ow, self.nc))
        else:
            mm = np.memmap(datafile, dtype=np.float32, offset=offset,
                           shape=shape)
            
        crop0 = (self.ow - self.w)//2
        crop1 = (crop0 + self.w)
        print(mm.shape)
        if self.channels == -1:
            x = mm[:,crop0:crop1, crop0:crop1, :]
        else:
            x = mm[:,crop0:crop1, crop0:crop1, self.channels]
        del mm
        print(x.shape)
        return x 

    def read_labels_mm(self, labelsfile, images):
        mm = np.memmap(labelsfile, dtype=self.label_dtype, offset=self.label_offset)
        ns = images.shape[0]
        mm = mm.reshape((ns, -1))
        x = mm[:]
        del mm
        print(x.shape)
        return x

    def normalize(self, type=0):
        xm = self.images.mean(axis=(1,2), keepdims=True)
        sm = self.images.std(axis=(1,2), keepdims=True)
        self.images = (self.images - xm)/sm
        print(sm.sum(axis=0), self.images.min(), self.images.max())

    def permute_data_and_labels(self, data, labels):
        n = data.shape[0]
        perm = np.random.permutation(n)
        pdata = data[perm]
        plabels = labels[perm]
        return pdata, plabels

    def set_ttv(self, ptrain, ptest, pval):
        n = self.images.shape[0] 
        ntrain = int(ptrain*n)
        ntest = int(ptest*n)
        
        self.train_images = self.images[:ntrain]
        self.test_images = self.images[ntrain:ntrain + ntest]
        self.val_images = self.images[ntrain + ntest:]

        self.train_labels = self.labels[:ntrain]
        self.test_labels = self.labels[ntrain:ntrain + ntest]
        self.val_labels = self.labels[ntrain + ntest:]

        self.train_label_nums = self.label_nums[:ntrain]
        self.test_label_nums = self.label_nums[ntrain:ntrain + ntest]
        self.val_label_nums = self.label_nums[ntrain + ntest:]
        self.make_class_where()

    def make_class_where(self):

        self.class_where_train = list()
        self.class_where_test = list()
        self.class_where_val = list()
        
        for i in range(self.nclasses):
            wi = np.where(self.train_label_nums == i)
            self.class_where_train.append(wi)

        for i in range(self.nclasses):
            wi = np.where(self.test_label_nums == i)
            self.class_where_test.append(wi)

        for i in range(self.nclasses):
            wi = np.where(self.val_label_nums == i)
            self.class_where_val.append(wi)
            
            
            

    def balanced_set(self, x, y, yn, nsamples, cluster_num):
        # x is images
        # y is labels
        # yn is the label_nums

        # get the indices where label is cluster_num
        
        w = yn[cluster_num]
        # shuffle the contents of w
        # where returns a tuple, so need to index it to get the array
        np.random.shuffle(w[0])
        # get the first nsamples of nr
        nr = w[0][:nsamples]
        bx = x[nr]
        nrot  = np.random.randint(0, 4)
        bx = np.rot90(bx, nrot, axes=(1,2))
        by = y[nr]
        return bx, by
        

    def get_balanced_batch(self, x, y, yn, n):
        
        d = n//self.nclusters
        m = n % self.nclusters

        image_list = list()
        label_list = list()
        r = np.random.randint(0, self.nclusters)
        for i in range(self.nclusters):
            s = d
            if i == r:
                s += m
            abx, aby = self.balanced_set(x, y, yn, s, i)
            image_list.append(abx)
            label_list.append(aby)

        bx = np.concatenate(image_list, axis=0)
        by = np.concatenate(label_list, axis=0)

        kx = np.arange(bx.shape[0])
        np.random.shuffle(kx)
        bx = bx[kx]
        bx += .2*np.random.rand()
        by = by[kx]
        return bx, by
                                  
    def get_batch(self, x, y, n):
        xp, yp = self.permute_data_and_labels(x, y)
        xp = xp[:n]
        yp = yp[:n]
        xp += .2*np.random.standard_normal(size=xp.shape)
        return xp, yp



    def get_regularizer(self, scale=1.):
        return tf.contrib.layers.l2_regularizer(scale)
    
    def dnet_block(self, x, nf, k, drate, is_training=None, droprate=0):
        
        ns = x.get_shape().as_list()[-1]
        h = tf.layers.conv2d(x, nf, k, strides=1,
                             padding='same', dilation_rate=drate,
                             kernel_initializer=None,
                             use_bias=False,
                             kernel_regularizer=self.get_regularizer(),
                             activation=None)

        h = tf.nn.leaky_relu(h)
        hc = tf.concat([x, h], -1)
        
        h1 = tf.layers.conv2d(hc, nf, k, strides=1,
                             padding='same', dilation_rate=drate,
                             kernel_initializer=None,
                             use_bias=False,
                             kernel_regularizer=self.get_regularizer(),
                             activation=None)

        h1 = tf.nn.leaky_relu(h1)
        h1c = tf.concat([hc, h1], -1)
        
        h2 = tf.layers.conv2d(h1c, nf, k, strides=1,
                             padding='same', dilation_rate=drate,
                             kernel_initializer=None,
                             use_bias=False,
                             kernel_regularizer=self.get_regularizer(),
                             activation=None)
        
        h2 = tf.nn.leaky_relu(h2)
        h2c = tf.concat([x, h, h1, h2], -1)
        
        ns = h2c.get_shape().as_list()[-1]
        print("!!!!!!!!!     ", ns)
        hf = tf.layers.conv2d(h2c, ns, k, strides=2,
                             padding='same', dilation_rate=drate,
                             kernel_initializer=None,
                             kernel_regularizer=self.get_regularizer(),
                             use_bias=False,
                             activation=None)

        hf = tf.nn.leaky_relu(hf)

        return hf

    def create_network(self, batch, is_training, droprate=0):
        
        layers = list()
        layers.append(batch)
        
        h = self.dnet_block(batch, 4, 3, 1, is_training=is_training, droprate=droprate)
        layers.append(h)

        h = self.dnet_block(h, 8, 3, 1, is_training=is_training, droprate=droprate)
        layers.append(h)

        h = self.dnet_block(h, 16, 3, 1, is_training=is_training, droprate=droprate)
        layers.append(h)

        h = tf.layers.flatten(h)
        h = tf.layers.dense(h, 1024,
                            kernel_regularizer=self.get_regularizer(),
                            kernel_initializer=None,
                            bias_initializer=tf.constant_initializer(value=0))

        h = tf.nn.leaky_relu(h)
        h = tf.layers.dense(h, 128,
                            kernel_initializer=None,
                            bias_initializer=tf.constant_initializer(value=0),
                            kernel_regularizer=self.get_regularizer())

        h = tf.nn.leaky_relu(h)
        
        h = tf.layers.dense(h, self.nclasses ,
                            kernel_initializer=tf.constant_initializer(value=0.0),
                            bias_initializer=tf.constant_initializer(value=1./self.nclasses),
                             kernel_regularizer=self.get_regularizer())        
        
        self.logits = h
        self.softmax = tf.nn.softmax(h)

    def create_loss(self, labels, l2f=0):
        loss = tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.logits, labels=labels)
        loss = tf.reduce_mean(loss, axis=(-1))
        l2_loss = tf.losses.get_regularization_loss()
        self.loss = tf.reduce_mean(loss) + l2f*l2_loss
        self.l2_loss = l2_loss

    def create_opt(self):       
        optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate,
                                     name='adam_opt')
        extra_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(extra_ops):
            self.opt = optimizer.minimize(self.loss)

    def create_placeholders(self):
        sizeC = self.images.shape[-1]
        self.image_batch = tf.placeholder(tf.float32, shape=(None, self.w, self.w, sizeC))
        self.label_batch = tf.placeholder(tf.float32, shape=(None, self.nclasses))
        self.learning_rate = tf.placeholder(tf.float32, shape=())
        self.is_training = tf.placeholder(tf.bool, shape=())
        
    def create_accuracy(self, y, y_):
        cpred = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
        self.accuracy = tf.reduce_mean(tf.cast(cpred, tf.float32))
        p = tf.argmax(y, 1)
        p_ = tf.argmax(y_, 1)
        _, self.accuracy_score = tf.metrics.accuracy(p_, p)
        _, self.precision = tf.metrics.precision(p_, p)
        _, self.recall = tf.metrics.recall(p_, p)        
        self.confmat = tf.math.confusion_matrix(p_, p)
                                                    
    def train(self, n_iter=10000, learning_rate=0.001, droprate=0, l2f=0,
              batchsize=128, checkpoint_dir='Checkpoints'):
        tf.reset_default_graph()
        self.create_placeholders()
        self.create_network(self.image_batch, is_training=self.is_training, droprate=droprate)
        self.create_loss(self.label_batch, l2f=l2f)
        self.create_accuracy(self.softmax, self.label_batch)
        self.create_opt()
        print("***********************")


        sess = tf.Session()
        self.sess = sess
        xinit = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
        sess.run(xinit)
        tf.summary.scalar('loss', self.loss)
        tf.summary.scalar('accuracy', self.accuracy)
        tf.summary.scalar('accuracy_score', self.accuracy_score)
        tf.summary.scalar('precision', self.precision)
        tf.summary.scalar('recall', self.recall)                 
        tf.summary.histogram('logits', self.softmax)
        tf.summary.histogram('clusters', tf.argmax(self.softmax, 1))
        tf.summary.histogram('truth', tf.argmax(self.label_batch, 1))

        merged = tf.summary.merge_all()

        saver = tf.train.Saver(max_to_keep=1)
        best_saver = tf.train.Saver(max_to_keep=1)
        dtnow = datetime.now().timetuple()
        #checkpoint_dir = 'Checkpoints'
        if not os.path.exists(checkpoint_dir):
            try:
                os.makedirs(checkpoint_dir)
            except:
                print("Can't make checkpoint directory")
                checkpoint_dir = 'Checkpoints'
                
        cpstring = '{}/cp-{}-{:02d}-{:02d}-{:02d}-{:02d}/checkpoint'.format(checkpoint_dir, *dtnow[:5])
        beststring = '{}/best-{}-{:02d}-{:02d}-{:02d}-{:02d}/best-checkpoint'.format(checkpoint_dir, *dtnow[:5])
        best_loss = 1.e6
        best_acc = 0
        for i in range(n_iter):
            if i % 100 == 0:
                if learning_rate > 0.0004:
                    learning_rate -= .01*learning_rate # .0002
                #print('learning rate set to ', learning_rate)
            if i % 2 == 0:
                bx, by = self.get_balanced_batch(self.train_images,
                                             self.train_labels,
                                             self.class_where_train, batchsize)
            else:
                bx, by = self.get_batch(self.train_images,
                                             self.train_labels, batchsize)

            _, xl, summary = sess.run([self.opt, self.loss, merged],
                             feed_dict={self.image_batch:bx, self.label_batch:by,
                                        self.learning_rate:learning_rate,
                                        self.is_training:True})
            
            
            if i % 100 == 0:
                tb, tl = self.get_balanced_batch(self.test_images,
                                                 self.test_labels,
                                                 self.class_where_test,
                                                 512)
                vl, vacc, _, _, vcm, test_summary = sess.run([self.loss, self.accuracy,
                                                        self.softmax, self.label_batch,
                                                        self.confmat, merged],
                                                        feed_dict={self.image_batch:tb,
                                                                    self.label_batch:tl,
                                                                    self.is_training:False})
        
                if vacc > best_acc:
                    best_saver.save(sess, beststring, i)
                    best_acc = vacc
                    print("!!! Best accuracy: ", i, vacc, vl)
                    
            if i % 1000 == 0:
                print(i, xl, vl, learning_rate)
                saver.save(sess, cpstring, i)
        ''' run the final test'''
        saver.save(sess, cpstring, i)
        tb, tl = self.get_balanced_batch(self.val_images,
                                         self.val_labels,
                                         self.class_where_test,
                                         1024)

        vl, _, _, vcm = sess.run([self.loss, self.softmax, self.label_batch, self.confmat],
                              feed_dict={self.image_batch:tb,
                                         self.label_batch:tl,
                                         self.is_training:False})

        print(vcm)
'''###### end of Classifier #######'''

def test_err(x):
    print(x)
    
def get_classifier(datafile, labelsfile, w, nc, cc, offset=0, ow=65,
                   channels=[1,2,3], dtype=np.float32, label_offset=0,
                   combine=None):
    print(datafile)
    c = Classifier(datafile, labelsfile, w, nc, cc, offset=offset,
                   ow=ow, channels=channels, dtype=dtype,
                   label_offset=label_offset, combine=combine)
    return c

if __name__ == '__main__':
    if sys.platform == 'darwin':
        datapre = ''
    else:
        datapre = ''

    parser = argparse.ArgumentParser(description='Train the classifier.')
    parser.add_argument('--cc', type=str)
    args = parser.parse_args()
    cc = np.array(args.cc.split(','), dtype=np.int32)
    print("Train on these", cc)

    datafile = datapre + 'Data/cc_images.mm'
    labelsfile = datapre + 'Data/cc_labels.mm'
    c = Classifier(datafile, labelsfile, 32, 5, cc)
    c.train(n_iter=10000, learning_rate=0.0008)
