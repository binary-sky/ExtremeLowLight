import tensorflow as tf
from tensorflow.python.ops import image_ops_impl



def contrast(Image):
    Image_Gray = tf.image.rgb_to_grayscale(Image) #BHWC #BHW1
    kernel = tf.constant([  [  [[0]]   ,   [[1]]   ,    [[0]]    ], [  [[1]]   , [[-4]]  , [[1]]   ], [  [[0]]   ,   [[1]]   ,    [[0]] ]    ], \
                        dtype = tf.float32) #[filter_height, filter_width, in_channels, channel_multiplier]
    Laplacian_map = tf.nn.depthwise_conv2d(input=Image_Gray,filter=kernel,strides=[1, 1, 1, 1], padding='SAME')
    Laplacian_map = tf.abs(Laplacian_map)
    return Laplacian_map[:,:,:,0]#BHW


def saturation(Image):
    _,var = tf.nn.moments(x = Image,axes = 3,keep_dims=False)
    svar=tf.sqrt(var)    #BHW
    return svar


def  well_exposedness(Image):
    Image_guass_cu = guass_culve(Image)
    return Image_guass_cu[:,:,:,0]*Image_guass_cu[:,:,:,1]*Image_guass_cu[:,:,:,2]#BHW



def guass_culve(x,mu,sig):
    return  tf.exp(-0.5*(x - mu)*(x - mu)/ (sig*sig)   )

def cal_quality(output_Batch):
    # saturation_ = tf.pow(saturation(output_Batch),0.5)
    # contrast_   = tf.pow(contrast(output_Batch),0.7)
    contrast_   = contrast(output_Batch)
    #saturation_ = tf.pow(saturation(output_Batch),0.5)
    well_exposedness_ = well_exposedness(output_Batch)

    W = well_exposedness(output_Batch)
    quality =tf.reduce_mean(W)
    return quality

def groundTruthImage_calculateWeight(Image):
    Image_Gray = tf.image.rgb_to_grayscale(Image)
    Image_guass_cu = guass_culve(Image_Gray, mu = 0.5 ,sig = 0.10)
    Image_guass_cu = gauss_filter(Image_guass_cu,fsize=9,fsigma=5.0)
    Image_guass_cu = Image_guass_cu/tf.reduce_sum(Image_guass_cu)*100.0   #归一化
    return Image_guass_cu #BHW1

def predictedImage_calculateExposureQuality(Image,groundTruthImageWeight):
    Image_Gray = tf.image.rgb_to_grayscale(Image)
    Image_well_exposedness = guass_culve(Image_Gray, mu = 0.5, sig = 0.2)*groundTruthImageWeight      #mu expected image average
    Image_well_exposedness = tf.reduce_sum(Image_well_exposedness)
    return Image_well_exposedness


def gauss_filter(image,fsize=3,fsigma=1.0):
    kernel = image_ops_impl._fspecial_gauss(size=fsize, sigma=fsigma)
    image_filtered = tf.nn.depthwise_conv2d(input=image,filter=kernel,strides=[1, 1, 1, 1], padding='SAME')
    return image_filtered


