#-*- coding:utf-8 -*-

# please use Anaconda for convienience
# python 3.7 and tensorflow 1.13 required, does not support TF2

# env configuration:

# conda install tensorflow=1.13.1 numpy opencv scipy pillow matplotlib   
# pip install rawpy exifread



import tensorflow as tf
import scipy.io as iox
import numpy as np
import glob,os,time,sys,cv2,random,logging,configparser
from termcolor import colored
from helper import printc
import parameters as pa
import input_channel as ic
import mainNet as net
import showoff as so
import helper as hp
from tensorflow.python.client import timeline
import cal_weight as cw
from ssim import cal_ssim_loss
from tensorflow.python import debug as tf_debug

checkpoint_dir = "./checkpoint/ESN_only/"
logs_path = "./logs/"
train_prefix = True
train_u_net = True
logging.basicConfig(filename='./LOG/train.log',format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', \
                    level = logging.DEBUG,filemode='a',datefmt='%Y-%m-%d%I:%M:%S %p')
logging.info("init")

#step one dataset reconstruction
logging.info("step one dataset reconstruction")
data_it = ic.get_dataset_iterator()
img_input_Graph, Y_im_gt_Graph,inp_iso_Graph,inp_t_Graph,amp_ratio_Graph,gt_t_Graph , wb_graph = data_it.get_next()
#step two network reconstruction
logging.info("step two network reconstruction")

#Exposure Shifting Network(ESN)
Yhat_im_output_Graph , _ = net.quality_pri_net(img_input_Graph,wb_graph, \
                                                    inp_iso_Graph,inp_t_Graph,gt_t_Graph)

loss_MAE_Graph = tf.reduce_mean(tf.abs(Yhat_im_output_Graph - Y_im_gt_Graph))
loss_SSIM_Graph = cal_ssim_loss(       Yhat_im_output_Graph,  Y_im_gt_Graph)

loss_Graph = 0.85*(loss_MAE_Graph)  + 0.15*(loss_SSIM_Graph)

learning_rate_Graph = tf.Variable(initial_value =1e-4,trainable = False,name='lrG')
#var_list_ = [var for var in tf.trainable_variables() if 'prefix_net' in var.name]
var_list_ = tf.trainable_variables()
opt_Graph = tf.train.AdamOptimizer(learning_rate=learning_rate_Graph).minimize(loss_Graph,var_list=var_list_)

#################################################################################################################
tf.set_random_seed(2020)
sess = tf.Session()
# sess = tf_debug.LocalCLIDebugWrapperSession(sess)
# sess.add_tensor_filter("has_inf_or_nan", tf_debug.has_inf_or_nan)

#step three load network parameters
logging.info("step three load network parameters")
epoch_pickup = int(hp.read_epoch())
sess.run(tf.global_variables_initializer())
saver = tf.train.Saver()
ckpt = tf.train.get_checkpoint_state(checkpoint_dir)


if ckpt:
    print('loaded ' + ckpt.model_checkpoint_path)
    saver.restore(sess, ckpt.model_checkpoint_path)
else:
    hp.update_epoch(0)
    epoch_pickup = 0
    printc('new model,epoch 0\n','green')


decend_log = open('decend_log.txt','a')
so.init_show_window()

#step four start trainning and save
logging.info("step four start trainning and save")

one_epoch_time = -1.0
start_lr = 0.000200
end_lr   = 0.000010
for epoch in range(epoch_pickup,pa.epoch_togo):
    time_start=time.time()
    logging.info("epoch:%d starting",epoch)

    lr_c = start_lr/(1+ ( start_lr/end_lr - 1  )  * epoch/pa.epoch_togo)
    sess.run(tf.assign(learning_rate_Graph,lr_c))

    epoch_loss_sumup = 0
    for step in range(pa.dataset_size):

        if pa.show: #show the trainning process
            #1                 2                   3                     4                    5            6
            _,               loss,            prediction,            ground_truth  ,    input_check      ,lr2               ,  ratio_Graph_= sess.run([
            opt_Graph,       loss_Graph,      Yhat_im_output_Graph,  Y_im_gt_Graph ,    img_input_Graph  ,learning_rate_Graph,  amp_ratio_Graph ])
            so.show_image_output_gt(input_check,prediction,ground_truth)
        else:
            #1               2                   3              4
            _,           loss,       lr2                     ,  ratio_Graph_    = sess.run([
            opt_Graph,   loss_Graph ,learning_rate_Graph     ,  amp_ratio_Graph    ] )


        print("Training(instant save)  epoch:",epoch,"\tstep:",step,"/",pa.dataset_size, \
            "\tloss",loss,"\tratio_Graph_\t",ratio_Graph_,     \
            "\tLR:",lr2,'\t ETA:',one_epoch_time*(pa.epoch_togo-epoch)/3600,'h')

        epoch_loss_sumup = epoch_loss_sumup + loss

    logging.info("save checkpoint")
    print(epoch_loss_sumup/pa.dataset_size*280,file=decend_log)
    decend_log.flush()
    if epoch % 2 == 1:
        saver.save(sess, checkpoint_dir + 'model.ckpt')
        printc('save\n','green')
    hp.update_epoch(epoch+1)

    time_end=time.time();one_epoch_time = (time_end-time_start) if one_epoch_time < 0 else ((time_end-time_start)+one_epoch_time)/2

#end of programe
print("terminate")
#new try