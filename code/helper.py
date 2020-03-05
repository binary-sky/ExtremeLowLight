#-*- coding:utf-8 -*-
from termcolor import colored
import os,configparser
import colorama
from PIL import Image
from PIL.ExifTags import TAGS

colorama.init()
def printc(content,color):
    print(colored(content, color),end='')


config = configparser.ConfigParser()        #读取上次训练位置
def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]
def read_epoch():
    config.readfp(open('epoch.ini'))            #读取上次训练位置
    epoch_pickup = config.get("Train","epoch")  #读取上次训练位置
    return epoch_pickup

def update_epoch(epoch):
    config.set("Train", "epoch",str(epoch))
    config.write(open('epoch.ini', "w"))

def get_exif_data(fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        print('IOERROR ' + fname)
    return ret