#-*- coding:utf-8 -*-
from multiprocessing import cpu_count

ps = 512        #patch size
epoch_togo = 1000
auto_batch_size = 1
show = True
path_father = "D:/datasets/"















##################### no need to change following paraters ##########################
bs = 1
active_partial_reload = False
dataset_size = 105  #auto detect

num_parallel_calls_ = cpu_count()
print("cpu cores:",num_parallel_calls_)
#num_parallel_calls_ = 1
prefetch_ = 16

SID_path = '............'

buff = False
dataset_buff_loc = "C:/TrainningTempCache/"

prefetch =True
shuffle = True

Linux = False
Y_data_8bit = True

enable_manual_batch = False      ### not available
manual_batch_size = 4
excute_whiteBalance = True
excute_mean_fix = False
excute_mid_fix = False
enable_my_datasets = False
enable_mini_map = False
enable_batch_norm = False
sig = False
half_size = True

#############################
testing_now = False
train_prefix = True
train_u_net = True
train_brightness_net = False
#############################



