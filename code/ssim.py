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

def cal_ssim_loss(img1,img2):
    img1 = tf.maximum(img1,0)
    img1 = tf.minimum(img1,1)
    loss_SSIM_Graph = 1 - tf.image.ssim_multiscale(img1,img2,max_val=1.0)
    loss_SSIM_Graph = tf.reduce_mean(loss_SSIM_Graph)
    return loss_SSIM_Graph