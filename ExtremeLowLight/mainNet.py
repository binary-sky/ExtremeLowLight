#-*- coding:utf-8 -*-
import tensorflow as tf
import parameters as pa
import tensorflow.contrib.slim as slim
from tensorflow.contrib.layers import conv2d as convolution
from tensorflow.contrib.layers import max_pool2d as pool2d
import numpy as np
size_of_patch = pa.ps



def quality_pri_net(inp_img,inp_wb,inp_iso,inp_t,gt_t):

    h = tf.shape(inp_img)[1]
    w = tf.shape(inp_img)[2]
    inp_img_normed = normalize_var(inp_img,0,0.00018782060752181462)
    #inp_img_normed = tf.Print(inp_img_normed,['inp_img_normed:',tf.shape(inp_img)])
    
    layer_inp_wb  = tf.ones([1,h,w,4])* normalize_var( inp_wb, 1.5084804 , 0.6111772 * 0.6111772 )
    layer_inp_iso = tf.ones([1,h,w,1])* normalize_var( inp_iso , 471.72858 , 264.23517 * 264.23517 )
    layer_inp_t   = tf.ones([1,h,w,1])* normalize_var( inp_t , 0.08489772 , 0.1368367 * 0.1368367 )
    layer_gt_t   =  tf.ones([1,h,w,1])* normalize_var( gt_t, 0.42407602 , 0.37255558 * 0.37255558 )

    inp_concated = tf.concat([  inp_img_normed, \
                                layer_inp_wb,   \
                                layer_inp_iso,  \
                                layer_inp_t,    \
                                layer_gt_t],3)

    inp_concated.set_shape(shape=(pa.bs,None,None, 4+4+3))

    with tf.variable_scope('prefix_net'):
        conv0 = convolution(inp_concated, 16, [3, 3], activation_fn=lrelu, trainable = pa.train_prefix, scope='g_conv0_1')
        conv0 = convolution(conv0, 16, [3, 3], activation_fn=lrelu,trainable = pa.train_prefix, scope='g_conv0_2')
        conv0 = convolution(conv0, 32, [3, 3], activation_fn=lrelu,trainable = pa.train_prefix, scope='g_conv0_3')
        conv0 = convolution(conv0, 32, [3, 3], activation_fn=lrelu,trainable = pa.train_prefix, scope='g_conv0_4')
        convp1 = convolution(conv0,32, [3, 3], activation_fn=lrelu,trainable = pa.train_prefix, scope='g_conv0_5')
    with tf.variable_scope('quality_pri_net'):

        conv1 = convolution(convp1, 32, [3, 3], activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv1_4')
        conv1 = convolution(conv1, 32, [3, 3], activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv1_5')
        pool1 = pool2d(conv1, [2, 2], padding='SAME')

        conv2 = convolution(pool1, 64, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv2_1')
        conv2 = convolution(conv2, 64, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv2_2')
        pool2 = pool2d(conv2, [2, 2], padding='SAME')

        conv3 = convolution(pool2, 128, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv3_1')
        conv3 = convolution(conv3, 128, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv3_2')
        pool3 = pool2d(conv3, [2, 2], padding='SAME')

        conv4 = convolution(pool3, 256, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv4_1')
        conv4 = convolution(conv4, 256, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv4_2')
        pool4 = pool2d(conv4, [2, 2], padding='SAME')

        conv5 = convolution(pool4, 512, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv5_1')
        conv5 = convolution(conv5, 512, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv5_2')

        up6 = upsample_and_concat(conv5, conv4, 256, 512)
        conv6 = convolution(up6, 256, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv6_1')
        conv6 = convolution(conv6, 256, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv6_2')

        up7 = upsample_and_concat(conv6, conv3, 128, 256)
        conv7 = convolution(up7, 128, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv7_1')
        conv7 = convolution(conv7, 128, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv7_2')

        up8 = upsample_and_concat(conv7, conv2, 64, 128)
        conv8 = convolution(up8, 64, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv8_1')
        conv8 = convolution(conv8, 64, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv8_2')

        up9 = upsample_and_concat(conv8, conv1, 32, 64)
        conv9 = convolution(up9, 32, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv9_1')
        conv9 = convolution(conv9, 32, [3, 3], rate=1, activation_fn=lrelu,trainable = pa.train_u_net, scope='g_conv9_2')
        conv10 = convolution(conv9, 12, [1, 1], rate=1, activation_fn=None,trainable = pa.train_u_net, scope='g_conv10')
        out = tf.depth_to_space(conv10, 2)

        return out,convp1



def brightness_predict_net(inp_img,inp_wb,inp_iso,inp_t):

    h = tf.shape(inp_img)[1]
    w = tf.shape(inp_img)[2]
    inp_img_normed = normalize_var(inp_img,0,0.00018782060752181462)
    

    layer_inp_wb  = tf.ones([1,h,w,4])* normalize_var( inp_wb, 1.5084804 , 0.6111772 * 0.6111772 )
    layer_inp_iso = tf.ones([1,h,w,1])* normalize_var( inp_iso , 471.72858 , 264.23517 * 264.23517 )
    layer_inp_t   = tf.ones([1,h,w,1])* normalize_var( inp_t , 0.08489772 , 0.1368367 * 0.1368367 )


    inp_concated = tf.concat([  inp_img_normed, \
                                layer_inp_wb,   \
                                layer_inp_iso,  \
                                layer_inp_t],3)

    inp_concated.set_shape(shape=(pa.bs,None,None, 4+4+2))

    with tf.variable_scope('brightness_predict_net'):

        if pa.ps != 512:
            input_BatchRS = tf.image.resize_nearest_neighbor(inp_concated,(512,512))
        else:
            input_BatchRS = inp_concated

        c1 = convolution(input_BatchRS, 16, [3, 3], stride=4, \
                        activation_fn=lrelu,trainable = pa.train_brightness_net)       #128*128*3
        c2 = convolution(c1, 16, [3, 3], stride=4, \
                        activation_fn=lrelu,trainable = pa.train_brightness_net)       #32*32*8
        c3 = convolution(c2, 32, [3, 3], stride=2, \
                        activation_fn=lrelu,trainable = pa.train_brightness_net)       #16*16*16
        c4 = convolution(c3, 32,  [3, 3], stride=2, \
                        activation_fn=lrelu,trainable = pa.train_brightness_net)       #8*8*32
        c5 = convolution(c4, 4, [3, 3], stride=2, \
                        activation_fn=lrelu,trainable = pa.train_brightness_net)       #4*4*4
        c5_vec = tf.reshape(c5,shape=[tf.shape(c5)[0],-1])
        c6_vec  = layer_fc(c5_vec, 4*4*4 , 32, relu_free=False,name='dense1',trainable = pa.train_brightness_net)
        gt_time  = layer_fc(c6_vec, 32 , 1, relu_free=True,name='dense2',trainable = pa.train_brightness_net)

        return gt_time

def normalize_var(inp,mean,var):
    return (inp-mean)/tf.sqrt(var)


cap = 700
id_list = {}
id_list_f = {}


def auto_norm_(var,id):
    if not id in id_list:
        id_list[id] = []
        id_list_f[id] = [None]*2
    if len(id_list[id]) < cap:
        id_list[id].append(var)
        #print(id_list[id])

        id_list_f[id][0] = np.mean(id_list[id])
        id_list_f[id][1] = np.sqrt(np.var( id_list[id]))
    elif len(id_list[id]) == cap:
        id_list[id].append(var)
        normalization = open('normalization.txt','a')
        print(id,'is stable,mean:   ',id_list_f[id][0],'   s_var   ',id_list_f[id][1],file = normalization )
        print('normalize_var(',id ,',', id_list_f[id][0], ',' , id_list_f[id][1],'*',id_list_f[id][1],')',file = normalization)
    if len(id_list[id])<10:
        #print(var)
        return np.zeros_like(var,dtype=np.float32)

    else:
        return (var-id_list_f[id][0])/id_list_f[id][1]
def auto_norm(var,id):
    var_N = tf.py_func(auto_norm_, [var,id],
                          tf.float32)
    return var_N
    

#是否加norm
batch_norm_params = {
    'fused': True,
    'is_training': True
}
def layer_fc(input,in_notes,out_nodes,relu_free=False,name="default",trainable = True):
    initializer_ = tf.contrib.layers.xavier_initializer()
    w1 = tf.get_variable(name + "weight" , shape=[in_notes,out_nodes], initializer=initializer_,trainable = True)
    b1 = tf.get_variable(name + "bias", shape=[out_nodes], initializer=tf.keras.initializers.zeros(),trainable = True)
    out = tf.matmul(input,w1)+b1
    if not relu_free:
        out = lrelu(out)
    return out


def get_core(core_vector):
    m1  = layer_fc(core_vector,  3,  32, relu_free=False,name='m1')
    m2  = layer_fc(m1,  32,  128, relu_free=False,name='m2')
    m3  = layer_fc(m2,  128, 128, relu_free=False,name='m3')

    m41 = layer_fc(m3,  128,  16, relu_free=False,name='m41')
    m42 = layer_fc(m3,  128,  16, relu_free=False,name='m42')
    m43 = layer_fc(m3,  128,  16, relu_free=False,name='m43')

    core_01 = tf.reshape(m41,shape=[1,1,4,4])
    core_02 = tf.reshape(m42,shape=[1,1,4,4])
    core_03 = tf.reshape(m43,shape=[1,1,4,4])
    return core_01,core_02,core_03


def lrelu(x):
    return tf.maximum(x * 0.2, x)

def tanhpp(x):  #ranging -2~2  0~4   0~1200
    return ( (tf.nn.tanh(x) + 1 )*10) 

def upsample_and_concat(x1, x2, output_channels, in_channels):
    pool_size = 2
    deconv_filter = tf.Variable(tf.truncated_normal([pool_size, pool_size, output_channels, in_channels], stddev=0.02),trainable = pa.train_u_net)
    deconv = tf.nn.conv2d_transpose(x1, deconv_filter, tf.shape(x2), strides=[1, pool_size, pool_size, 1])

    deconv_output = tf.concat([deconv, x2], 3)
    deconv_output.set_shape([None, None, None, output_channels * 2])

    return deconv_output




def Hat(input_batch):
    input_batch_1 = resnet_convolutional_block_BottleNeck(input_batch  , 2,  8, "in1")
    input_batch_2 = resnet_convolutional_block_BottleNeck(input_batch_1, 4, 16, "in2")
    input_batch_3 = resnet_convolutional_block_BottleNeck(input_batch_2, 8, 32, "in3")
    u_net_out = u_net(input_batch_3)
    out2 = resNetBlock(u_net_out,32, "out1")
    out3 = resNetBlock(out2,32, "out2")
    out4 = resNetBlock(out3,32, "out3")
    out5 = resNetBlock(out4,32, "out4")
    out6 = resNetBlock(out5,32, "out4")
    out7 = slim.conv2d(out6, 3, [1, 1], rate=1, activation_fn=None, scope='final')
    return out7



    
def resNetBlock(input,channels,block_name):
    with tf.variable_scope(block_name):
        X_shortcut = input
        conv1 = slim.conv2d(input, channels, \
                            [3, 3], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=lrelu,\
                            scope='resNetBlock_1')
        conv2 = slim.conv2d(conv1, channels, \
                            [3, 3], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=None,\
                            scope='resNetBlock_2')
        out = tf.add(conv2, X_shortcut)
        out_final = lrelu(out)
        return out_final

def resNetBottleNeckBlock(input,channels,bottleNeckChannels,block_name):
    with tf.variable_scope(block_name):
        X_shortcut = input
        conv1 = slim.conv2d(input, bottleNeckChannels, \
                            [1, 1], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=lrelu,\
                            scope='resNetBottleNeckBlock_1')

        conv2 = slim.conv2d(conv1, bottleNeckChannels, \
                            [3, 3], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=lrelu,\
                            scope='resNetBottleNeckBlock_2')

        conv3 = slim.conv2d(conv2, channels, \
                            [1, 1], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=None,\
                            scope='resNetBottleNeckBlock_3')

        out = tf.add(conv3, X_shortcut)
        out_final = lrelu(out)
        return out_final

def resnet_convolutional_block_BottleNeck(input,bottleNeckChannels,output_channels,block_name):
    with tf.variable_scope(block_name):
        x_shortcut = input
        #first
        conv1 = slim.conv2d(input, bottleNeckChannels, \
                            [1, 1], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=lrelu,\
                            scope='convResNetBottleNeckBlock_1')        
        #second
        conv2 = slim.conv2d(conv1, bottleNeckChannels, \
                            [3, 3], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=lrelu,\
                            scope='convResNetBottleNeckBlock_2')
        #third
        conv3 = slim.conv2d(conv2, output_channels, \
                            [1, 1], rate=1, \
                            normalizer_fn=tf.contrib.layers.batch_norm,\
                            normalizer_params=batch_norm_params, \
                            activation_fn=None,\
                            scope='convResNetBottleNeckBlock_3')
        #shortcut path
        x_shortcut = slim.conv2d(x_shortcut, output_channels, \
                            [1, 1], rate=1, \
                            normalizer_fn=None,\
                            normalizer_params=None, \
                            activation_fn=None,\
                            scope='convResNetBottleNeckBlock_shortcut')
        #final
        add = tf.add(x_shortcut, conv3)
        add_result = tf.nn.relu(add)
        return add_result


















def my_conv(input_tensor,input_channels,output_channels,kernel_size,name):
    with tf.name_scope(name) as scope:

        weight = tf.Variable(tf.truncated_normal(shape = [kernel_size, kernel_size, input_channels, output_channels] ,
                                                 mean = 0,
                                                 stddev=1, 
                                                 dtype=tf.float32),
                             trainable=True,
                             name = name+"_weight" )
        bias =   tf.Variable(tf.constant(0.0, 
                                        shape=[output_channels],#一个输出通道一个bias
                                        dtype=tf.float32),
                          
                             name = name+"_bias")
        return tf.nn.relu(
            tf.nn.conv2d(input_tensor, weight, (1,1,1,1),padding='SAME',name = name+"_conv" ) + bias, 
            name = name+"_relu")
         

def my_conv_special_init(input_tensor,input_channels,output_channels,kernel_size,name):
    with tf.name_scope(name) as scope:
        R = 1.0
        G = 1.0
        B = 1.0
        weight = tf.Variable(initial_value = tf.constant(value = [ [[   [0,0,B],[0,0.5*G,0],[0,0.5*G,0],[R,0,0]   ]] ]  ),
                             trainable=True,
                             name = name+"_weight" )
        bias =   tf.Variable(tf.constant(0.0, 
                                        shape=[output_channels],#一个输出通道一个bias
                                        dtype=tf.float32),
                          
                             name = name+"_bias")

        return tf.nn.relu(
            tf.nn.conv2d(input_tensor, weight, (1,1,1,1),padding='SAME',name = name+"_conv" ) + bias, 
            name = name+"_relu")


#def MAIN_NETWORK(input_Batch):
    
#    with tf.name_scope('S_NET'):
#        conv1 = slim.conv2d(input_Batch,        4, kernel_size = 3, activation_fn=tf.nn.leaky_relu,scope='S_NET/1')         #size p*p
#        conv2 = slim.conv2d(conv1,              16,kernel_size = 3, activation_fn=tf.nn.leaky_relu,scope='S_NET/2')         #size p*p
#        conv3 = slim.conv2d(conv2,              16,kernel_size = 3, activation_fn=tf.nn.leaky_relu,scope='S_NET/3')         #size p*p
#        conv4 = slim.conv2d(conv3,              16,kernel_size = 3, activation_fn=tf.nn.leaky_relu,scope='S_NET/4')         #size p*p
#    with tf.name_scope('S_NET_OUT'):
#        conv4o1 = slim.conv2d(conv4,            3, kernel_size = 3, activation_fn=tf.nn.leaky_relu,scope='S_NET_OUT/1')         #size p*p
#        conv4o2 = slim.conv2d(conv4o1,          3, kernel_size = 1, activation_fn=None,scope='S_NET_OUT/2')         #size p*p
    
#    return conv4o2


