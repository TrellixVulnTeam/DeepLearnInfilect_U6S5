""" Using convolutional net on MNIST dataset of handwritten digit
(http://yann.lecun.com/exdb/mnist/)
"""
from __future__ import print_function

import os
import time 

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

N_CLASSES = 10

# Step 1: Read in data
# using TF Learn's built in function to load MNIST data to the folder data/mnist
mnist = input_data.read_data_sets("/media/royd1990/fd0ff253-17a9-49e9-a4bb-0e4529adb2cb/home/royd1990/Documents/deep_learning_tensorFlow/ml-course1/week1/CNN/train/mnist", one_hot=True)

# Step 2: Define paramaters for the model
LEARNING_RATE = 0.001
BATCH_SIZE = 128
SKIP_STEP = 10
DROPOUT = 0.75
N_EPOCHS = 1

# Step 3: create placeholders for features and labels
# each image in the MNIST data is of shape 28*28 = 784
# therefore, each image is represented with a 1x784 tensor
# We'll be doing dropout for hidden layer so we'll need a placeholder
# for the dropout probability too
# Use None for shape so we can change the batch_size once we've built the graph
with tf.name_scope('data'):
    X = tf.placeholder(tf.float32, [None, 784], name="X_placeholder")
    Y = tf.placeholder(tf.float32, [None, 10], name="Y_placeholder")

dropout = tf.placeholder(tf.float32, name='dropout')

# Step 4 + 5: create weights + do inference
# the model is conv -> relu -> pool -> conv -> relu -> pool -> fully connected -> softmax
global_step = tf.Variable(0, dtype=tf.int32, trainable=False, name='global_step')
with tf.variable_scope('conv1') as scope:
    # first, reshape the image to [BATCH_SIZE, 28, 28, 1] to make it work with tf.nn.conv2d
    # use the dynamic dimension -1
    input_layer = tf.reshape(X, [-1, 28, 28, 1])
    # create kernel variable of dimension [5, 5, 1, 32]
    # use tf.truncated_normal_initializer()
    kernel = tf.get_variable('kernels', [5, 5, 1, 32],
                             initializer=tf.truncated_normal_initializer())
    # create biases variable of dimension [32]
    # use tf.random_normal_initializer()
    bias=tf.get_variable("bias",[32],initializer=tf.random_normal_initializer())
    # apply tf.nn.conv2d. strides [1, 1, 1, 1], padding is 'SAME'
    conv1= tf.nn.conv2d(input_layer,kernel,strides=[1,1,1,1],padding='SAME')
    # apply relu on the sum of convolution output and biases
    y1=tf.nn.relu(conv1+bias)
    # output is of dimension BATCH_SIZE x 28 x 28 x 32

with tf.variable_scope('pool1') as scope:
    # apply max pool with ksize [1, 2, 2, 1], and strides [1, 2, 2, 1], padding 'SAME'
    
    pool1=tf.nn.max_pool(y1,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')
    # output is of dimension BATCH_SIZE x 14 x 14 x 32

with tf.variable_scope('conv2') as scope:
    # similar to conv1, except kernel now is of the size 5 x 5 x 32 x 64
    kernel = tf.get_variable('kernels', [5, 5, 32, 64], 
                        initializer=tf.truncated_normal_initializer())
    biases = tf.get_variable('biases', [64],
                        initializer=tf.random_normal_initializer())
    conv = tf.nn.conv2d(pool1, kernel, strides=[1, 1, 1, 1], padding='SAME')
    conv2 = tf.nn.relu(conv + biases, name=scope.name)

    # output is of dimension BATCH_SIZE x 14 x 14 x 64

with tf.variable_scope('pool2') as scope:
    # similar to pool1
    pool2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
                            padding='SAME')

    # output is of dimension BATCH_SIZE x 7 x 7 x 64

with tf.variable_scope('fc') as scope:
    # use weight of dimension 7 * 7 * 64 x 1024
    input_features = 7 * 7 * 64
    # create weights and biases
    W = tf.Variable(tf.random_normal(shape=[input_features, 1024], stddev=0.01), name='weights')
    B = tf.Variable(tf.zeros([1, 1024]), name="bias")
     # reshape pool2 to 2 dimensional
    pool2 = tf.reshape(pool2, [-1, input_features])
    # apply relu on matmul of pool2 and w + b
    fc=tf.nn.relu(tf.matmul(pool2,W) + B)
    # apply dropout
    fc = tf.nn.dropout(fc, dropout, name='relu_dropout')

with tf.variable_scope('softmax_linear') as scope:
    # this you should know. get logits without softmax
    # you need to create weights and biases
    w = tf.Variable(tf.random_normal(shape=[1024,N_CLASSES], stddev=0.01), name='weights2')
    b=tf.Variable(tf.zeros([1, 10]), name="bias2")
    logits=tf.matmul(fc,w) + b
# Step 6: define loss function
# use softmax cross entropy with logits as the loss function
# compute mean cross entropy, softmax is applied internally
with tf.name_scope('loss'):
    # you should know how to do this too
    entropy = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y, name='loss')
    loss = tf.reduce_mean(entropy)
    preds=tf.nn.softmax(logits=logits,name='pred')
    correct_preds = tf.equal(tf.argmax(preds, 1), tf.argmax(Y, 1))
    accuracy = tf.reduce_sum(tf.cast(correct_preds, tf.float32))
# Step 7: define training op
# using gradient descent with learning rate of LEARNING_RATE to minimize cost
# don't forgot to pass in global_step
    optimizer=tf.train.AdamOptimizer(name='optimizer',learning_rate=LEARNING_RATE).minimize(loss)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    # to visualize using TensorBoard
    writer = tf.summary.FileWriter('./my_graph/mnist', sess.graph)
    ##### You have to create folders to store checkpoints
    ckpt = tf.train.get_checkpoint_state(os.path.dirname('/media/royd1990/fd0ff253-17a9-49e9-a4bb-0e4529adb2cb/home/royd1990/Documents/deep_learning_tensorFlow/ml-course1/week1/CNN/train/checkpoints/convnet_mnist/checkpoint'))
    # if that checkpoint exists, restore from checkpoint
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess, ckpt.model_checkpoint_path)
    
    initial_step = global_step.eval()

    start_time = time.time()
    n_batches = int(mnist.train.num_examples / BATCH_SIZE)

    total_loss = 0.0
    for index in range(initial_step, n_batches * N_EPOCHS): # train the model n_epochs times
        X_batch, Y_batch = mnist.train.next_batch(BATCH_SIZE)
        _, loss_batch = sess.run([optimizer, loss], 
                                feed_dict={X: X_batch, Y:Y_batch, dropout: DROPOUT}) 
        total_loss += loss_batch
        if (index + 1) % SKIP_STEP == 0:
            print('Average loss at step {}: {:5.1f}'.format(index + 1, total_loss / SKIP_STEP))
            total_loss = 0.0

    
    print("Optimization Finished!") # should be around 0.35 after 25 epochs
    print("Total time: {0} seconds".format(time.time() - start_time))
    saver.save(sess,
               '/media/royd1990/fd0ff253-17a9-49e9-a4bb-0e4529adb2cb/home/royd1990/Documents/deep_learning_tensorFlow/ml-course1/week1/CNN/train/checkpoints/convnet_mnist/mnist-convnet.chkp',
               index)
    # test the model
    n_batches = int(mnist.test.num_examples/BATCH_SIZE)
    total_correct_preds = 0
    for i in range(n_batches):
        X_batch, Y_batch = mnist.test.next_batch(BATCH_SIZE)
        #_, loss_batch,pred,logits_batch = sess.run([optimizer,loss,preds,logits],
        #                                feed_dict={X: X_batch, Y:Y_batch, dropout: DROPOUT})
        #_,pred = sess.run([loss,preds],
                      #  feed_dict={X: X_batch,Y:Y_batch,dropout: DROPOUT})
      #  preds = tf.nn.softmax(logits_batch)
        #correct_preds = tf.equal(tf.argmax(pred, 1), tf.argmax(Y_batch, 1))
        #accuracy = tf.reduce_sum(tf.cast(correct_preds, tf.float32))
        acc=sess.run(accuracy,feed_dict={X: X_batch, Y:Y_batch, dropout: DROPOUT})
        total_correct_preds += acc
    
    print("Accuracy {0}".format(total_correct_preds/mnist.test.num_examples))