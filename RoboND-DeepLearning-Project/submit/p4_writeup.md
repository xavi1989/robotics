# RoboND-P04-Follow-Me
## Udacity Robotics Nanodegree.

[image0]: ./img/fm1.png
[image1]: ./img/fm2.png
[image2]: ./img/fm3.png
[image3]: ./img/fm4.png


### Network Architecture
#### Encoder
The encoder layer is composed of convolution layer and batch normalization.

```python
def separable_conv2d_batchnorm(input_layer, filters, strides=1):
    output_layer = SeparableConv2DKeras(filters=filters,kernel_size=3, strides=strides,
                             padding='same', activation='relu')(input_layer)

    output_layer = layers.BatchNormalization()(output_layer)
    return output_layer

def encoder_block(input_layer, filters, strides):

    # TODO Create a separable convolution layer using the separable_conv2d_batchnorm() function.
    output_layer = separable_conv2d_batchnorm(input_layer, filters, strides=strides)

    return output_layer
```

#### 1x1 convolution
1 by 1 convolution means that the filter will be of size 1x1 with N depths. The stride will also be 1 on both directions. In this case, both the input and the output tensor will have the same width and height. The only difference is the depth.
```python
conv2d_batchnormed = conv2d_batchnorm(encoder_2, 128, kernel_size=1, strides=1)
```

#### Decoder
Decoder layer will scale up the input tensor. And then concatenates the scaled input tensor with the skip tensor into combined tensor. Then do the 2d convolution on the combined tensor.

```python
def decoder_block(small_ip_layer, large_ip_layer, filters):

    # TODO Upsample the small input layer using the bilinear_upsample() function.
    output_layer = bilinear_upsample(small_ip_layer)

    # TODO Concatenate the upsampled and large input layers using layers.concatenate
    output_layer = layers.concatenate([output_layer, large_ip_layer])

    # TODO Add some number of separable convolution layers    
    output_layer = separable_conv2d_batchnorm(output_layer, filters, strides=1)

    return output_layer
```

#### Fully convolution Network
Fully convolution network means that every layer is convolution layer. It can consists of 1x1 convolution which in same way is equivalent to fully connected layer. The fully convolution layer does not have restrictions on the input tensor size.

#### why do encoding / decoding images
Encode layer can compress the input tensor into feature map while the decoding layer can extract the feature map and restore the original information. With this compress and de-compress method, we can remove some redundant information and focus on the real features.

#### Can this model works well for other object?
Yes this model will be working well for other objects with the proper training data.

#### Network in this experiment
The network we use in this are as follows:
Features Layer (?, 160, 160, 3) - - |
Encoder 1 (?, 80, 80, 32) - - - -|  |
Encoder 2 (?, 40, 40, 64)        |  |  skip
1x1 Conv (?, 20, 20, 128)        |  |  Connections
Decoder 1 (?, 80, 80, 64) - - - -|  |
Decoder 2 (?, 80, 80, 64) - - - - - |
Output Layer (?, 160, 160, 3)

```python
def fcn_model(inputs, num_classes):
    encoder_1 = encoder_block(inputs, 32, strides=2)
    print ('Encoder 1', encoder_1)

    encoder_2 = encoder_block(encoder_1, 64, strides=2)
    print ('Encoder 1', encoder_2)


    # TODO Add 1x1 Convolution layer using conv2d_batchnorm().
    conv2d_batchnormed = conv2d_batchnorm(encoder_2, 128, kernel_size=1, strides=1)

    # TODO: Add the same number of Decoder Blocks as the number of Encoder Blocks
    decoder_1 = decoder_block(conv2d_batchnormed, encoder_1, 64)
    print ('Decoder 1', decoder_1)

    decoder_2 = decoder_block(decoder_1, inputs, 32)
    print ('Decoder 1', decoder_2)    

    # The function returns the output layer of your model. "x" is the final layer obtained from the last decoder_block()
    return layers.Conv2D(num_classes, 1, activation='softmax', padding='same')(decoder_2)
```

### Fully connected layer
In the image classification task, in the last convolution layer, the input tensor will be flattened into shape of (N1, 1). Denote N2 be the shape of output tensor (N2, 1). Then the weight will be of shape (N1, N2).

### Hyper Parameters
#### Epoch
One epoch is one passing through of the training data set. With epoch increased, both training and validation loss will drop. But after some epoch, the decrease the loss will not be obvious and sometimes increase a little bit.
In this experiment, we set the epoch = 60

#### Learning Rate
After each run of batch samples, the network calculate the loss and the back-propagation gradients. The learning rate is used here as the step size for the back-propagation gradients.
Learning rate affects the model accuracy. The tuning of learning rate is important. After several of tries, I set the learning rate to be 0.0015.

#### Batch Size
Batch size is the number of samples to work through before updating the internal model parameters. I set the batch size = 100 in this experiment.

### Get more training data
I use the simulator to generate more training sets.
I generate the data sets for the following scenarios.
1. Following hero in a dense crowds
I use the simulator in the DL training mode. I create a pilot path for the drone and then a path for the hero. I also add a lot of points for people to spawn. Then I start recording to generate training sets.

2. Following here while hero walk in zigzag
I set a two pilot points so that the drone will fly from one path to the other in a line. Then I create a zigzag path for the hero. In this case, the drone will capture hero with different angles.

With these data sets, I am able to increase the model accuracy.


### Results

IoU Scores

#### When Quad is following behind hero

number true positives: 539, number false positives: 0, number false negatives: 0
![alt text][image0]

#### When Quad is on patrol and no target visable

number true positives: 0, number false positives: 128, number false negatives: 0
![alt text][image1]

#### When Quad can detect hero far away
number true positives: 163, number false positives: 4, number false negatives: 138
![alt text][image2]

Weight: 0.7222
Final IoU: 0.5698
Final Score: 0.4115

### Performance on Simulator
By running the simulator, once the drone finds the hero, it will follow the hero and do not lose the target.
![alt text][image3]
