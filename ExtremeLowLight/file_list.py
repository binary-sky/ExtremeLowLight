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
def get_XYZL_file_list():
    
    input_dir = pa.SID_path+'/short/'
    gt_dir = pa.SID_path+'/long/'

    file_listX = []
    file_listY = []
    file_listZ = []
    file_listL = []
    file_listT = []
    file_listI = []
    # get train IDs
    train_fns = glob.glob(gt_dir + '0*.ARW')
    train_ids = [int(os.path.basename(train_fn)[0:5])
                 for train_fn in train_fns]
    for id in train_ids:
        in_files = glob.glob(input_dir + '%05d_00*.ARW' % id)
        gt_files = glob.glob(gt_dir + '%05d_00*.ARW' % id)
        for in_path in in_files:
            gt_path = gt_files[0]
            in_fn = os.path.basename(in_path)
            gt_fn = os.path.basename(gt_path)
            in_exposure = float(in_fn[9:-5])
            gt_exposure = float(gt_fn[9:-5])
            ratio = gt_exposure / in_exposure
            iso = float(get_iso(in_fn))
            #print(iso)
            #ratio = gt_exposure / in_exposure
            file_listX.append(in_path)
            file_listY.append(gt_path)
            file_listZ.append(ratio)
            file_listL.append(0)
            file_listT.append(in_exposure)
            file_listI.append(iso)
            
 

    for i in range(len(file_listX)):
        print(file_listX[i],"  -->\t",file_listY[i])


    pa.dataset_size = int(len(file_listX)/pa.auto_batch_size)
    print("数据集数量总计：",pa.dataset_size)
    return file_listX, file_listY, file_listZ, file_listL,file_listT,file_listI


def get_XYZL_file_list_mydatasets():


    file_listX = []
    file_listY = []
    file_listZ = []
    file_listL = []
    file_listT = []
    file_listI = []
    # load dataset from my dataset
    dir_father = pa.path_father
    dir_children = hp.get_immediate_subdirectories(dir_father)

    for dir_child in dir_children:
        if dir_child == 'TFRECORD':
            continue
        dng_image_files = glob.glob(dir_father + dir_child + '/*.dng')
        dng_image_files = sorted(dng_image_files)
        list_txt = glob.glob(dir_father + dir_child + '/list.txt')
        list_txt_path = list_txt[0]
        cnt_0s = -1  # 哪一个图是ground truth

        time_list = []  # 每个图的time
        iso_list = []  # 每个图的time
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
                    print("oooooooooooooooooOOOOOh NO")

                if 'iso_speed' in parts[-1]:
                    str = parts[-1]
                    iso = float(str.split(':')[-1])
                    iso_list.append(iso)
                elif 'iso_speed' in parts[-2]:
                    str = parts[-2]
                    iso = float(str.split(':')[-1])
                    iso_list.append(iso)
                else:
                    print("oooooooooooooooooOOOOOh NO")

                if cnt_0s != -1:
                    if parts[-1]!='X':
                        input_tobe_list.append(1)
                    else:
                        input_tobe_list.append(0)
                else:
                    input_tobe_list.append(0)
                    

                if parts[-1] == 'T':
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
    print("数据集数量总计：",pa.dataset_size)
    return file_listX, file_listY, file_listZ, file_listL,file_listT,file_listI





def get_XYZL_file_list_test():
    
    input_dir = pa.SID_path+'/short/'
    gt_dir = pa.SID_path+'/long/'

    file_listX = []
    file_listY = []
    file_listZ = []
    file_listL = []
    file_listT = []
    file_listI = []
    # get train IDs
    train_fns = glob.glob(gt_dir + '1*.ARW')
    train_ids = [int(os.path.basename(train_fn)[0:5])
                 for train_fn in train_fns]
    for id in train_ids:
        in_files = glob.glob(input_dir + '%05d_00*.ARW' % id)
        gt_files = glob.glob(gt_dir + '%05d_00*.ARW' % id)
        for in_path in in_files:
            gt_path = gt_files[0]
            in_fn = os.path.basename(in_path)
            gt_fn = os.path.basename(gt_path)
            in_exposure = float(in_fn[9:-5])
            gt_exposure = float(gt_fn[9:-5])
            ratio = gt_exposure / in_exposure
            iso = get_iso_for_test(in_fn)
            #print(iso)
            #ratio = gt_exposure / in_exposure
            file_listX.append(in_path)
            file_listY.append(gt_path)
            file_listZ.append(ratio)
            file_listL.append(0)
            file_listT.append(in_exposure)
            file_listI.append(iso)
            
    # loaded dataset from SID

    if pa.enable_my_datasets:
        # load dataset from my dataset
        dir_father = pa.path_father
        dir_children = hp.get_immediate_subdirectories(dir_father)

        for dir_child in dir_children:
            if dir_child == 'TFRECORD':
                continue
            dng_image_files = glob.glob(dir_father + dir_child + '/*.dng')
            dng_image_files = sorted(dng_image_files)
            list_txt = glob.glob(dir_father + dir_child + '/list.txt')
            list_txt_path = list_txt[0]
            cnt_0s = -1  # 哪一个图是ground truth

            time_list = []  # 每个图的time
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
                        print("oooooooooooooooooOOOOOh NO")

                    if cnt_0s != -1:
                        if parts[-1]!='X':
                            input_tobe_list.append(1)
                        else:
                            input_tobe_list.append(0)
                    else:
                        input_tobe_list.append(0)
                        

                    if parts[-1] == 'T':
                        cnt_0s = cnt_pp

            for i in range(8):
                gt_path = dng_image_files[cnt_0s]
                if input_tobe_list[i] == 1:
                    ratio = time_list[cnt_0s]/time_list[i]
                    if ratio > 500:
                        continue
                    in_path = dng_image_files[i]
                    file_listX.append(in_path)
                    file_listY.append(gt_path)
                    file_listZ.append(ratio)
                    file_listL.append(1)

    f = open ('list.txt','a')
    for i in range(len(file_listX)):
       #raw_FILE = rawpy.imread(file_listX[i])
       #print("max:",raw_FILE.raw_image_visible.max(),"\tmin:",raw_FILE.raw_image_visible.min())
       #WB_vec = raw_FILE.camera_whitebalance
       #raw_pattern = raw_FILE.raw_pattern.flatten().astype(np.int32)#运用raw文件白平衡信息
       #WB_vec[3]=WB_vec[1] #RGBG ---> WB_G2 = WB_G1
       #WB_vec = np.array([ WB_vec[raw_pattern[0]], \
       #                WB_vec[raw_pattern[1]], \
       #                WB_vec[raw_pattern[2]], \
       #                WB_vec[raw_pattern[3]] ])
       #WB_vec = WB_vec/WB_vec[1]
       #print(file_listX[i],"  -->\t",file_listY[i],"\nR-->\t",float('%.2f' % file_listZ[i]),"  G-->\t",file_listL[i],"\tWB_vec:",WB_vec,"\traw_pattern:",raw_pattern,file = f)
        print(file_listX[i],"  -->\t",file_listY[i],file = f)

    f.close()
    pa.dataset_size = int(len(file_listX)/pa.auto_batch_size)
    print("数据集数量总计：",pa.dataset_size)
    return file_listX, file_listY, file_listZ, file_listL,file_listT,file_listI
#get_XYZL_file_list()
