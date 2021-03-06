# -*- coding: utf-8 -*-

import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D,MaxPool2D,Dropout,Flatten,Dense,BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

from google.colab import drive
drive.mount('/content/drive')

"""## Load Data"""

x = np.load('/content/drive/My Drive/Cells.npy')
y = np.load('/content/drive/My Drive/Labels.npy')

"""## Split into train, validation, test dataset"""

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=0) #隨機種子，確保每次切割出來都一樣，才能調參數
x_train, x_validation, y_train, y_validation = train_test_split(x_train, y_train, test_size=0.2, random_state=0)

train_generator = ImageDataGenerator()
val_generator = ImageDataGenerator()

train_generator = train_generator.flow(x_train,
                                       y_train,
                                       batch_size = 64, #一次會用64個
                                       shuffle = False)

val_generator = val_generator.flow(x_validation,
                                   y_validation,
                                   batch_size = 64,
                                   shuffle = False)

test_generator = ImageDataGenerator()
test_generator = test_generator.flow(x_test,
                                     y_test,
                                     batch_size = 64,
                                     shuffle = False)

"""## Train model"""

def create_model():
  model = tf.keras.models.Sequential([tf.keras.layers.Conv2D(10,(3,3), activation = "relu", input_shape=(50,50,3)), #filter(kenal map)=16, stride=(3,3)
                                     tf.keras.layers.MaxPool2D((2,2)), #在(2,2)的格子裡挑出最大值
                                     tf.keras.layers.Flatten(),
                                     tf.keras.layers.Dense(1, activation = "sigmoid")
                                     ])
  model.compile(loss="binary_crossentropy",
                optimizer ="adam",
                metrics =['accuracy'])
  return model

model = create_model()
model.summary()

history = model.fit_generator(train_generator,
                              steps_per_epoch = 1000,
                              epochs = 20,
                              shuffle = False,
                              validation_data=val_generator, 
                              validation_steps=len(val_generator)
                              )

"""## Model evaluaion"""

loss_train = history.history['loss']
loss_val = history.history['val_loss']
epochs = range(1,21)
plt.plot(epochs, loss_train, 'g', label='Training loss')
plt.plot(epochs, loss_val, 'b', label='validation loss')
plt.title('Training and Validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

loss_train = history.history['accuracy']
loss_val = history.history['val_accuracy']
epochs = range(1,21)
plt.plot(epochs, loss_train, 'g', label='Training accuracy')
plt.plot(epochs, loss_val, 'b', label='validation accuracy')
plt.title('Training and Validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

def plot_metrics(history):
  metrics = ['loss', 'accuracy', 'precision', 'recall']
  for n, metric in enumerate(metrics):
    name = metric.replace("_"," ").capitalize()
    plt.subplot(2,2,n+1)
    plt.plot(history.epoch, history.history[metric], color=colors[0], label='Train')
    #plt.plot(history.epoch, history.history['val_'+metric],
             #color=colors[0], linestyle="--", label='Val')
    plt.xlabel('Epoch')
    plt.ylabel(name)
    if metric == 'loss':
      plt.ylim([0, plt.ylim()[1]])
    elif metric == 'accuracy':
      plt.ylim([0.8,1])
    else:
      plt.ylim([0,1])

    plt.legend()

train_predictions_baseline = model.predict(train_generator, batch_size=1)
test_predictions_baseline = model.predict(test_generator, batch_size=1)

def plot_cm(labels, predictions, p=0.5):
  cm = confusion_matrix(labels, predictions > p)
  plt.figure(figsize=(5,5))
  sns.heatmap(cm, annot=True, fmt="d")
  plt.title('Confusion matrix @{:.2f}'.format(p))
  plt.ylabel('Actual label')
  plt.xlabel('Predicted label')

  print('Legitimate Transactions Detected (True Negatives): ', cm[0][0])
  print('Legitimate Transactions Incorrectly Detected (False Positives): ', cm[0][1])
  print('Fraudulent Transactions Missed (False Negatives): ', cm[1][0])
  print('Fraudulent Transactions Detected (True Positives): ', cm[1][1])
  print('Total Fraudulent Transactions: ', np.sum(cm[1]))

baseline_results = model.evaluate(test_generator)
for name, value in zip(model.metrics_names, baseline_results):
  print(name, ': ', value)
print()

plot_cm(y_test, test_predictions_baseline)
