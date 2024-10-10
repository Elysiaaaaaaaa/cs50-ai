import logging
import cv2
import numpy as np
import os
import sys
import tensorflow as tf
from sklearn.model_selection import train_test_split

EPOCHS = 1000
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4
logging.basicConfig(level=logging.INFO)

def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")
        # pass
    logging.info('begin_load')
    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[2])
    logging.info('finish_load')

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()
    logging.info('begin_train')

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)
    logging.info('finish_train')

    logging.info('begin_predic')
    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    file_dir = os.listdir(data_dir)

    images = []
    labels = []

    for i in range(NUM_CATEGORIES):
        for file in os.listdir(os.path.join(data_dir,str(i))):
            img = cv2.imread(os.path.join(data_dir,str(i),file))
            img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
            img = img.astype("float32") / 255.0
            images.append(img)
            labels.append(i)
    return images, labels



def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)))
    model.add(tf.keras.layers.MaxPooling2D((2, 2)))
    model.add(tf.keras.layers.AlphaDropout(0.2))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(43, activation='relu'))

    model.compile(loss=tf.keras.losses.CategoricalFocalCrossentropy(),
                  optimizer=tf.keras.optimizers.Adam(),
                  metrics=['accuracy'])

    return model

if __name__ == "__main__":
    main()
