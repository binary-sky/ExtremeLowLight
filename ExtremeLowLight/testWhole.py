import tensorflow.contrib.slim as slim
import matplotlib.pyplot as plt
import tensorflow as tf
import scipy.io as iox
import numpy as np
import glob,os,time,sys,cv2,random,logging,configparser,scipy.io,rawpy,math
from termcolor import colored
import tensorflow.contrib.slim as slim
from matplotlib import pyplot as plt
import mainNet as net
import file_list as fl
import parameters as pa
import helper as hp
import exifread 
import input_channel as ic
import tkinter as tk
from tkinter import filedialog

remove_bounder = False
pa.testing_now = True
pa.buff = False
pa.ps = 512+256  # mean nothing,just to avoid assertion code


checkpointpath="./checkpoint/"

root = tk.Tk()
root.withdraw()
print('a file selection UI should pop up now, English path only, 不能有中文路径！ ~~')
path_name = filedialog.askopenfilenames(filetypes=[('raw image', '.dng')])
#collect raw image file to be enhanced


dng_image_files = path_name






#tensorflow network input portal
img_input_Graph = tf.placeholder(tf.float32, [None, None, None, 4])
wb_graph = tf.placeholder(tf.float32, None)
inp_iso_Graph = tf.placeholder(tf.float32, None)
inp_t_Graph = tf.placeholder(tf.float32, None)

'''
Notice:   vars with '_Graph' are nodes in the tensorflow network,otherwise they are not
'''
# construct network frame
gt_t_prediction_Graph = net.brightness_predict_net(img_input_Graph,wb_graph,inp_iso_Graph,inp_t_Graph)
Yhat_im_output_Graph , _ = net.quality_pri_net( img_input_Graph, \
                                                wb_graph, \
                                                inp_iso_Graph, \
                                                inp_t_Graph, \
                                                gt_t_prediction_Graph)


#tensorflow session and checkpoint/parameter loading
sess = tf.Session()
ckpt = tf.train.get_checkpoint_state(checkpointpath)
variables_to_restore = tf.contrib.framework.get_variables_to_restore()
saver_temp = tf.train.Saver(variables_to_restore)
saver_temp.restore(sess, ckpt.model_checkpoint_path)
print('ok')


def get_result(img_path,classID,time,iso):
    in_path = img_path
    ref_path = '00000000000'    # taking the place of ground truth path, ignore it
    X_img, _ , wb= ic._main_pre_process(in_path,ref_path,00000000,classID=classID,time=time,iso=iso)   
    #image channel order: R G1 B G2
    
    X_img   = np.expand_dims(X_img, axis=0)     #from file's Image Array
    wb      = np.expand_dims(wb, axis=0)        #from file's EXIF info
    iso     = np.expand_dims(iso, axis=0)       #from file's EXIF info
    time    = np.expand_dims(time, axis=0)      #from file's EXIF info

    #execute
    y_hat = sess.run([Yhat_im_output_Graph],feed_dict={ 
        img_input_Graph:X_img,
        wb_graph:wb,
        inp_iso_Graph:iso,
        inp_t_Graph:time,
         })

    #show and save
    output = np.minimum(np.maximum(y_hat[0], 0), 1)
    output = cv2.cvtColor(output[0,:,:,:], cv2.COLOR_RGB2BGR)
    print('note: there have to be a test_result1 folder!')
    cv2.imwrite('./test_result1/'+os.path.basename(img_path)+'enhanced.jpg',output*255)
    hp.printc('./test_result1/'+os.path.basename(img_path)+'enhanced.jpg\n','green')
    cv2.namedWindow('OUT',cv2.WINDOW_NORMAL)
    cv2.imshow('OUT',output)
    cv2.waitKey(1000)




#collecting complete,execute one by one
for path_name in dng_image_files: 
    f = open(path_name, 'rb')
    # Return Exif tags
    tags = exifread.process_file(f)
    print(tags) 
    time__ = float(tags['Image ExposureTime'].values[0].num/tags['Image ExposureTime'].values[0].den)
    iso__ = float(tags['Image ISOSpeedRatings'].values[0])
    get_result( img_path=path_name,
                classID=1,
                time=time__,
                iso=iso__)

os.system("pause")