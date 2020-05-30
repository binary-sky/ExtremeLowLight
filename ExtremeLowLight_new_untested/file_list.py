# -*- coding:utf-8 -*-
import os
import glob
import cv2
import parameters as pa
import helper as hp
import rawpy
import numpy as np

def get_iso_for_test(in_fn):
    with open('Sony_test_list.txt','r') as listfile:
        lines = listfile.readlines()
        for i in range(len(lines)):
            parts = lines[i].split()
            if in_fn in parts[0]:
                
                if 'ISO' in parts[-2]:
                    return int(parts[-2].split('O')[-1])

def get_iso(in_fn):
    with open('Sony_train_list.txt','r') as listfile:
        lines = listfile.readlines()
        for i in range(len(lines)):
            parts = lines[i].split()
            if in_fn in parts[0]:
                
                if 'ISO' in parts[-2]:
                    return int(parts[-2].split('O')[-1])


def get_XYZL_file_list_mydatasets():

    file_listX = [] # low light raw image path
    file_listY = [] # ground truth raw image path
    file_listZ = [] # ty/tx
    file_listL = [] # not used
    file_listT = [] # tx
    file_listI = [] # ISO

    # load dataset from my dataset
    # path_father = "./CID train set/"
    dir_father = pa.path_father
    dir_children = hp.get_immediate_subdirectories(dir_father)

    for dir_child in dir_children:
        if dir_child == 'TFRECORD':
            continue
        dng_image_files = glob.glob(dir_father + dir_child + '/*.dng')
        dng_image_files = sorted(dng_image_files)
        list_txt = glob.glob(dir_father + dir_child + '/list.txt')
        list_txt_path = list_txt[0]
        cnt_0s = -1  # sel ground truth

        time_list = []  # expsoure time
        iso_list = []  # expsoure time
        input_tobe_list = []
        with open(list_txt_path, 'r') as f:
            list_lines = f.readlines()
            cnt_pp = -1
            for single_line in list_lines:
                cnt_pp = cnt_pp + 1
                parts = single_line.split()
                if 'exposure_time' in parts[-2]:
                    str = parts[-2]
                    time = float(str.split(':')[-1])
                    time_list.append(time)
                elif 'exposure_time' in parts[-3]:
                    str = parts[-3]
                    time = float(str.split(':')[-1])
                    time_list.append(time)
                else:
                    print("error")

                if 'iso_speed' in parts[-1]:
                    str = parts[-1]
                    iso = float(str.split(':')[-1])
                    iso_list.append(iso)
                elif 'iso_speed' in parts[-2]:
                    str = parts[-2]
                    iso = float(str.split(':')[-1])
                    iso_list.append(iso)
                else:
                    print("error")

                if cnt_0s != -1:
                    if parts[-1]!='X':      # detected excluded image
                        input_tobe_list.append(1)
                    else:
                        input_tobe_list.append(0)
                else:
                    input_tobe_list.append(0)

                if parts[-1] == 'T': # detected ground truth image
                    cnt_0s = cnt_pp

        count_selected = 0
        for i in range(8):
            gt_path = dng_image_files[cnt_0s]
            if input_tobe_list[i] == 1:
                ratio = time_list[cnt_0s]/time_list[i]
                if ratio > 500:
                    continue
                if count_selected >= 4:
                    continue
                in_path = dng_image_files[i]
                file_listX.append(in_path)
                file_listY.append(gt_path)
                file_listZ.append(ratio)
                file_listL.append(1)
                file_listT.append(time_list[i])
                file_listI.append(iso_list[i])
                count_selected = count_selected + 1
        print('selected:',count_selected)

    for i in range(len(file_listX)):
        print(file_listX[i],"  -->\t",file_listY[i])


    pa.dataset_size = int(len(file_listX)/pa.auto_batch_size)
    print("dataset cnt：",pa.dataset_size)
    return file_listX, file_listY, file_listZ, file_listL,file_listT,file_listI




