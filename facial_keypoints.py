# FACIAL KEYPOINT DETECTION
# The libraries
from numpy import zeros, array
from os.path import join
from skimage.color import gray2rgb
from skimage.io import imread
from skimage.transform import resize
import pandas as pd
import numpy as np
import os

# Load the images
# Scale the images to 100*100
# scale the cordinates in range [-0.5,0.5]

def load_imgs_and_keypoints(dirname='data'):
    imgs = []
    heights = []
    widths = []
    for filename in os.listdir(join(dirname, 'images')):
        img = imread(join(dirname, 'images', filename))
        img = gray2rgb(img)
        heights.append(img.shape[0])
        widths.append(img.shape[1])
        img = resize(img, [100, 100], mode='constant')
        imgs.append(img)
        
    df = pd.read_csv(join(dirname, 'gt.csv'))
    df = df.iloc[:, 1:]
    for i in range(df.shape[1]):
        if i&1:
            df.iloc[:, i] /= heights
        else:
            df.iloc[:, i] /= widths
    
    points = df.values
    points -= 0.5
    return np.asarray(imgs), points

# Load the images and points
imgs, points = load_imgs_and_keypoints()

#Exaample image
from skimage.io import imshow
imshow(imgs[0])

#check the normalised cordinates
print(points[0])

## Function to visualise the data. Fn obtains two arguments : image, vector of points cordinates and drwas point on the image
import matplotlib.pyplot as plt
# circle for drawing points on face

from matplotlib.patches import Circle
def visualize_points(img, points):
    fig, ax = plt.subplots()
    ax.imshow(img)
    for i in range(len(points) // 2):
        plt.plot((points[i*2] + 0.5)*100, (points[i*2 + 1] + 0.5)*100, 'o', color='r')
        
# train/val split
from sklearn.model_selection import train_test_split
imgs_train, imgs_val, points_train, points_val = train_test_split(imgs, points, test_size=0.1)

imgs_train.shape

# Data Augmentation, flips image and points
f_img, f_points = flip_img(imgs[1], points[1])
visualize_points(f_img, f_points)

def augmentSample(imgs_train, points_train):
    aug_imgs = []
    aug_points = []
    for img, points in zip(imgs_train, points_train):
        f_img, f_points = flip_img(img, points)
        aug_imgs.append(img)
        aug_imgs.append(f_img)
        aug_points.append(points)
        aug_points.append(f_points)
    return np.asarray(aug_imgs), np.asarray(aug_points)

aug_imgs_train, aug_points_train = augmentSample(imgs_train, points_train)

visualize_points(aug_imgs_train[2], aug_points_train[2])

visualize_points(aug_imgs_train[3], aug_points_train[3])

aug_imgs_train.shape

aug_points_train.shape
    ####### ***************************************************** ################
    
### NETWORK ARCHITECTURE STARTS FROM HERE

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

model = Sequential()
model.add(Conv2D(32, kernel_size = (3,3), activation= 'relu', input_shape= aug_imgs_train[0].shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(aug_points_train.shape[1], activation='linear'))

# Trainig
# using MSE as training a regressor

# ModelCheckpoint for saving the model
# Saved model will help in fine tuning

from keras.callbacks import ModelCheckpoint
from keras.optimizers import SGD, Adam

# Choose the optimser and compile the model
model.compile(loss ='mse', optimizer='Adam', metrics=['mse'])
model.fit(aug_imgs_train, aug_points_train, batch_size=128, epochs = 10, verbose = 1, validation_data=(imgs_val, points_val))

# Visualise the results
predicted_points = model.predict(imgs_val)
print(predicted_points[0:5, :]) #check that output points are different

# Example of output
for i in range(5):
    idx = np.random.choice(imgs_val.shape[0])
    visualize_points(imgs_val[idx], predicted_points[idx])
