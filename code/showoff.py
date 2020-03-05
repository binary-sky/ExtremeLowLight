#-*- coding:utf-8 -*-
import cv2,time
import parameters as pa
import numpy as np

def init_show_window():
    if pa.show :
        if pa.Linux:
            cv2.namedWindow('output_gt',cv2.WINDOW_NORMAL)
        else:
            cv2.namedWindow('output_gt',cv2.WINDOW_GUI_NORMAL)

def show_image_all_batch_channel(window_name,img):
    if pa.show :
        batch_size = img.shape[0]
        channels = img.shape[3]

        def concate_batch(channel):
            numpy_horizontal_concat = img[0,:,:,channel]
            for i in range(1,batch_size):
                numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat, img[i,:,:,channel]), axis=1)
            return numpy_horizontal_concat


        numpy_vertical_concat = concate_batch(0)
        for j in range(1,channels):
            numpy_vertical_concat = np.concatenate((numpy_vertical_concat, concate_batch(j)), axis=0)


        cv2.imshow(window_name,numpy_vertical_concat)

def show_image_output_gt(input_check,
                            img_predict,
                            img_gt):
    if pa.show :
        #
        input_check = input_check[:,:,:,(0,1,2)]
        img_predict = img_predict[:,:,:,(0,1,2)]
        img_gt = img_gt[:,:,:,(0,1,2)]

        

        if (input_check.shape!= img_predict.shape):
            input_check_t = np.zeros(shape = img_predict.shape,dtype = np.float32)
            for t in range(input_check.shape[0]):
                input_check_t[t,:,:,:] = cv2.resize(input_check[t,:,:,:], dsize=(
                        img_predict.shape[2], img_predict.shape[1]), interpolation=cv2.INTER_LINEAR)
            input_check = input_check_t

        

        batch_size = img_predict.shape[0]
        channels = img_predict.shape[3]

        if (channels==3):
            numpy_horizontal_concat = img_predict[0,:,:,:]
            for i in range(1,batch_size):
                numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat, img_predict[i,:,:,:]), axis=1)

            numpy_horizontal_concat2 = img_gt[0,:,:,:]
            for i in range(1,batch_size):
                numpy_horizontal_concat2 = np.concatenate((numpy_horizontal_concat2, img_gt[i,:,:,:]), axis=1)

            numpy_horizontal_concat3 = input_check[0,:,:,:]
            for i in range(1,batch_size):
                numpy_horizontal_concat3 = np.concatenate((numpy_horizontal_concat3, input_check[i,:,:,:]), axis=1)

            numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat3,numpy_horizontal_concat, numpy_horizontal_concat2), axis=0)
        
        numpy_horizontal_concat=cv2.cvtColor(numpy_horizontal_concat, cv2.COLOR_RGB2BGR)
        cv2.imshow('output_gt',numpy_horizontal_concat)
        cv2.waitKey(1)