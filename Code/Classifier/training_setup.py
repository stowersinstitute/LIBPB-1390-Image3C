import sys
from image3c import classifier_runner

print(sys.argv)
params = dict()
if sys.argv[1] == "-d":
    try:
        params['description'] = sys.argv[2]
    except:
        params['description'] = ""
else:
    params['description'] = ""
    

num_classes = 7
### where to read images from
params['datafile'] = ''  # path to the numpy memmap with images
### where are the labels
params['labelsfile'] = '.npy' # path to numpy file with labels
### what clusters from the labels to use
params['clusterlist'] = list(range(num_classes))
params['combine'] = [] #[[0, 8], [4, 7]] # any clusters from labels to combine
params['tensorboard_log_dir'] = 'logs' # path to tensorboard logs
params['num_channels'] = 3
params['channels'] = [0,1,2] # what channels to use

params['iterations'] = 1 #25000
params['learning_rate'] = 0.001 #0.0006
params['droprate'] = 0.0
params['l2f'] = 0.006 #0.004
params['batchsize'] = 256

### Name of output checkpoint directory
params['CheckpointDir'] = "Checkpoints/checkpoint_name" # path to checkpoints
classifier_runner.run(params)

print("Done")
