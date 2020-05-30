# -*- coding:utf-8 -*-
import rawpy
import os
import glob
import cv2
import parameters as pa
import helper as hp
import tensorflow as tf
import numpy as np
import scipy.misc as sm
import showoff as so
import file_list as fl


def get_dataset_iterator():
    X, Y, ratiot , classidt ,timein,Iso = fl.get_XYZL_file_list_mydatasets()
    X_input = tf.constant(X)
    Y_gt = tf.constant(Y)
    ratio = tf.constant(ratiot)
    classID = tf.constant(classidt)
    time = tf.constant(timein)
    iso = tf.constant(Iso)


    dataset = tf.data.Dataset.from_tensor_slices(
        (X_input, Y_gt, ratio, classID,time,iso))  # 定义一个Dataset实例
    if pa.shuffle:
        dataset = dataset.shuffle(pa.dataset_size*pa.auto_batch_size)
    # 对dataset中的每一对（filename， label）调用_parse_function进行处理
    dataset = dataset.map(
        _parse_function, num_parallel_calls=pa.num_parallel_calls_)
    #至此dataset为[H,W,C],rank = 3
    pa.bs = pa.manual_batch_size
    
    if not pa.enable_manual_batch:
        dataset = dataset.batch(batch_size=pa.auto_batch_size)   # 设置每批次的大小
        pa.bs = pa.auto_batch_size
    
    #至此dataset为[N,H,W,C],rank = 4
    dataset = dataset.repeat()              # 无限重复数据集
    if pa.prefetch:
        dataset = dataset.prefetch(pa.prefetch_)
    # 打印dataset的相关信息
    print('dataset shapes:', dataset.output_shapes)
    print('dataset types:',  dataset.output_types)
    # 获取一个用来迭代数据的iterator
    return dataset.make_one_shot_iterator()

def _parse_function(X, Y, ratio, classID, time, iso ):
    X_img, Y_img,wb = tf.py_func(_main_pre_process, [X, Y, ratio, classID,time,iso],
                              [tf.float32, tf.float32, tf.float32])
    X_img.set_shape(shape=(pa.ps, pa.ps, 4))
    Y_img.set_shape(shape=(2*pa.ps, 2*pa.ps, 3))
    ratio.set_shape(shape=())
    time.set_shape(shape=())
    iso.set_shape(shape=())
    timegt = time * ratio
    timegt.set_shape(shape=())
    wb.set_shape(shape=(4))
    return X_img, Y_img ,iso, time, ratio, timegt, wb


def _main_pre_process(X, Y, ratio, classID, time, iso):
    X_img, Y_img, WB_vec = read_image_from_file(X, Y)
    
    X_img = X_img.astype(np.float32)                        #膨胀成float32
    Y_img = Y_img.astype(np.float32)                        #膨胀成float32
    
    if np.equal(classID, 0):    # if classID == 0:          #不同设备需要不同的归一化
        X_img = np.maximum(X_img - 512, 0) / (16383 - 512)
    elif np.equal(classID, 1):  # if classID == 1:          #不同设备需要不同的归一化
        X_img = X_img / 959.0

       
    Y_img = Y_img / 255.0 #8位存储的图像


    if not pa.testing_now:
        X_img, Y_img = _crop_filp_transpose_same(X_img, Y_img)


    return X_img, Y_img , WB_vec







def input_nonlin(X):
    X = np.minimum(X, (X-1)/100.0 + 1   )
    Y = np.minimum(X, 2)
    return Y









def _readX(X_path):
    raw_FILE = rawpy.imread(X_path)
    X_img = raw_FILE.raw_image_visible.astype(np.uint16)  # 2 dim [H  W]
    raw_pattern = raw_FILE.raw_pattern
    raw_pattern = raw_pattern.flatten().astype(np.int32)
    white_balance = raw_FILE.camera_whitebalance
    white_balance = np.array(white_balance, dtype=np.float32)
    X_img = np.expand_dims(X_img, axis=2)  # 3 dim [H  W  C=1]
    height = X_img.shape[0]
    width = X_img.shape[1]
    # Blue          2          #for SONY   Red        0
    # Green 1       1                      Green 1    1
    # Green 2       1x                     Green 2    1x
    # Red           0                      Blue       2
    X_img = np.concatenate((X_img[0:height:2, 0:width:2, :],
                            X_img[0:height:2, 1:width:2, :],
                            X_img[1:height:2, 0:width:2, :],
                            X_img[1:height:2, 1:width:2, :]),
                           axis=2)
    raw_pattern_reverse = [np.argwhere(raw_pattern == 0)[0][0],
                           np.argwhere(raw_pattern == 1)[0][0],
                           np.argwhere(raw_pattern == 2)[0][0],
                           np.argwhere(raw_pattern == 3)[0][0]]
    X_img = X_img[:, :, raw_pattern_reverse]  # 通道顺序转变为统一的 R G1 B G2

    if white_balance[3] == 0:
        white_balance[3] = white_balance[1]

    white_balance = white_balance/white_balance[1]

    return X_img, white_balance

def autostr(strx):
    if type(strx) is str:
        return strx
    else:
        return str(strx, encoding = "utf8")

def _readYfX(Y_path,X_path):

    file_path =  autostr(X_path)    +'.Nofusion'+'.jpg'

    if not pa.testing_now:
        if not os.path.exists(file_path):
            Y_raw = rawpy.imread(Y_path)
            Y_img = Y_raw.postprocess(
                use_camera_wb=True, half_size=False, no_auto_bright=True, output_bps=16).astype(np.float32)/65535.0
            Y_img=cv2.cvtColor(Y_img, cv2.COLOR_RGB2BGR)
            Y_img = Y_img * 255   #float 0~255
            cv2.imwrite(file_path,Y_img)
            print("making cache: cv2 imwrite complete")
            Y_img=cv2.cvtColor(Y_img, cv2.COLOR_BGR2RGB)
        else:
            Y_img = cv2.imread(file_path)  #uint8 0~255
            Y_img=cv2.cvtColor(Y_img, cv2.COLOR_BGR2RGB)
        
        return Y_img
    else:
        return np.zeros((2*pa.ps,2*pa.ps,3),dtype=np.float32)


def get_buff_loc(X):
    X=autostr(X)
    return str(pa.dataset_buff_loc + os.path.split(X)[1] + ".npz")

def get_buff_loc_fu(X,Y):
    X=autostr(X)
    Y=autostr(Y)
    return str(pa.dataset_buff_loc + os.path.basename(Y)+' f '+os.path.basename(X) + ".npz")

def read_image_from_file(X, Y):  # 输入字符串tensor路径 #输出<1> :  4 channel 半图像 tensor，uint16
    # 输出<2> :  3 channel 全图像 tensor，uint16
    if pa.buff == True:
        X_buff_loc = get_buff_loc(X)
        Y_buff_loc = get_buff_loc(Y)
        YfX_buff_loc = get_buff_loc_fu(X,Y)
        #print(YfX_buff_loc)

        if os.path.exists(X_buff_loc):
            try:
                loadedX = np.load(X_buff_loc)
                X_img = loadedX['X']
                WB_vec = loadedX['WB']
            except BaseException:
                print('无法读取文件：',X_buff_loc)
        else:
            X_img, WB_vec = _readX(X)
            print("save:"+X_buff_loc)
            np.savez_compressed(X_buff_loc, X=X_img, WB=WB_vec)

        ###############################
        if not pa.testing_now:
            if os.path.exists(YfX_buff_loc):
                try:
                    loadedY = np.load(YfX_buff_loc)
                    Y_img = loadedY['YfX']
                except BaseException:
                    print('无法读取文件：',Y_buff_loc)
            else:
                Y_img = _readYfX(Y,X)
                print("save:"+YfX_buff_loc)
                np.savez_compressed(YfX_buff_loc, YfX=Y_img)
        else:   # when testing Y_img is not needed
            Y_img = np.zeros_like(X_img)    # when testing Y_img is not needed
        ###############################
    else:
        X_img, WB_vec = _readX(X)
        if not pa.testing_now:
            Y_img = _readYfX(Y,X)
        else:   # when testing Y_img is not needed
            Y_img = np.zeros_like(X_img)    # when testing Y_img is not needed
    return X_img, Y_img, WB_vec


def _crop_filp_transpose_same(X_img, Y_img):
    
    if not pa.enable_manual_batch:
        H = X_img.shape[0]
        W = X_img.shape[1]
        xx = np.random.randint(0, W - pa.ps)
        yy = np.random.randint(0, H - pa.ps)
        X_img = X_img[yy:yy + pa.ps, xx:xx + pa.ps, :]
        if not pa.half_size:
            Y_img = Y_img[yy:yy + pa.ps, xx:xx + pa.ps, :]
        else:
            Y_img = Y_img[yy*2 : yy*2 + pa.ps*2,xx*2 : xx*2 + pa.ps*2,:]

        if np.random.randint(2, size=1)[0] == 1:    # random flip
            X_img = np.flip(X_img, axis=0)
            Y_img = np.flip(Y_img, axis=0)
        if np.random.randint(2, size=1)[0] == 1:    # random flip
            X_img = np.flip(X_img, axis=1)
            Y_img = np.flip(Y_img, axis=1)
        if np.random.randint(2, size=1)[0] == 1:    # random transpose
            X_img = np.transpose(X_img, (1, 0, 2))
            Y_img = np.transpose(Y_img, (1, 0, 2))

        return X_img, Y_img
    else:
        H = X_img.shape[1]
        W = X_img.shape[2]
        xx = np.random.randint(0, W - pa.ps)
        yy = np.random.randint(0, H - pa.ps)
        X_img = X_img[:, yy:yy + pa.ps , xx:xx + pa.ps, :]
        if not pa.half_size:
            Y_img = Y_img[:,yy:yy + pa.ps, xx:xx + pa.ps, :]
        else:
            Y_img = Y_img[:,yy*2 : yy*2 + pa.ps*2,xx*2 : xx*2 + pa.ps*2,:]
        if np.random.randint(2, size=1)[0] == 1:    # random flip
            X_img = np.flip(X_img, axis=1)
            Y_img = np.flip(Y_img, axis=1)
        if np.random.randint(2, size=1)[0] == 1:    # random flip
            X_img = np.flip(X_img, axis=2)
            Y_img = np.flip(Y_img, axis=2)
        if np.random.randint(2, size=1)[0] == 1:    # random transpose
            X_img = np.transpose(X_img, (0, 2, 1, 3))
            Y_img = np.transpose(Y_img, (0, 2, 1, 3))


        return X_img, Y_img