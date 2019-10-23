# -*- coding: utf-8 -*-
"""Copy of CIFAR 10.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12rcUZEEJD9spZ9YlcL_vWiBBD4eG4N5j
"""

import torch
import matplotlib.pyplot as plt
import numpy as np
import torch.nn.functional as F
from torch import nn
from torchvision import datasets, transforms

!pip3 install torch torchvision # Install torch and torch vision

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
"""
This allows for GPU acceleration if it is available, if not the program will continue to run using the CPU


"""

"""
Here we define the training and validation datasets for the learning process. Compose chains different transformations together
There are two sets, one for training and one for validation
"""
transform_train = transforms.Compose([transforms.Resize((32, 32)),                                                  # Resize the image to 32x32 pixels
                                     transforms.RandomHorizontalFlip(),                                             
                                     transforms.RandomRotation(10), 
                                     transforms.RandomAffine(0, shear=10, scale=(0.8, 1.2))                         # RandomAffine(degrees, translate=None, scale=None, shear=None, resample=False, fillcolor=0)
                                     ,transforms.ColorJitter(brightness = 0.2, contrast = 0.2, saturation = 0.2),
                                     transforms.ToTensor(),                                                         # Image must be converted to a tensor in order to be processed by the model 
                                     transforms.Normalize((0.5, 0.5, 0.5,), (0.5, 0.5, 0.5))                        # Rescales the image values from 0 to 1 
                                     ])

transform = transforms.Compose([transforms.Resize((32,32)),
                               transforms.ToTensor(),
                               transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
                               ])
training_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform_train)
validation_dataset = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)

training_loader = torch.utils.data.DataLoader(training_dataset, batch_size=200, shuffle=True)
validation_loader = torch.utils.data.DataLoader(validation_dataset, batch_size=200, shuffle=False)

"""
This function will perform the necessary transformations to the image to make it readable by the neural network
"""
def im_convert(tensor):
  image = tensor.cpu().clone().numpy()
  image = image.transpose(1, 2, 0)
  image = image * np.array((0.5, 0.5, 0.5)) + np.array((0.5, 0.5, 0.5))
  image = image.clip(0, 1)
  return image

classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

"""
Display some of the images 
"""
dataiter = iter(training_loader)
images, labels = dataiter.next()
fig = plt.figure(figsize=(25,4))

for idx in np.arange(20):
  ax = fig.add_subplot(2, 10, idx+1, xticks=[], yticks=[])
  plt.imshow(im_convert(images[idx]))
  ax.set_title(classes[labels[idx].item()])

"""
This is the basic class structure for the neural network. It has 3 convolutional layers and 2 fully connected layers for image classification 
"""
class LeNet(nn.Module):
  def __init__(self):
    super().__init__()                                      # super used for inheritance 
    self.conv1 = nn.Conv2d(3, 16, 3, 1, padding=1)          # torch.nn.functional.conv2d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1, padding_mode='zeros')
    self.conv2 = nn.Conv2d(16, 32, 3, 1, padding=1)             # input tensor of shape, filters of shape, optional bias tensor of shape, stride, padding 
    self.conv3 = nn.Conv2d(32, 64, 3, 1, padding=1)
    self.fc1 = nn.Linear(4*4*64, 500)                       # .Linear applies a linear transformation to any incoming data   ->  (in_features, out_features)
    self.dropout1 = nn.Dropout(0.5)                         # Dropout Method with Bernoulli distribution
    self.fc2 = nn.Linear(500,10)
  def forward(self, x):
    x = F.relu(self.conv1(x))
    x = F.max_pool2d(x, 2, 2)
    x = F.relu(self.conv2(x))
    x = F.max_pool2d(x, 2, 2)
    x = F.relu(self.conv3(x))
    x = F.max_pool2d(x, 2, 2)
    x= x.view(-1, 4*4*64)
    x = F.relu(self.fc1(x))
    x = self.dropout1(x)
    x = self.fc2(x)
    return x

"""
Instruct the model to use a CUDA (nvidia) GPU if available then print the structure 
"""
model  = LeNet().to(device)
model

"""
Set the criterion and optimizer functions
"""
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = 0.001)

"""
This is the basic training loop. It will make 15 epochs (training iterations, forwards and backwards) with the image batch
While the tests are being run, some basic statistics are updated including loss, corrects etc. 
"""
epochs = 15
running_loss_history = []
running_corrects_history = []
val_running_loss_history = []
val_running_corrects_history = []

for e in range(epochs):
  running_loss = 0.0
  running_corrects = 0.0
  val_running_loss = 0.0
  val_running_corrects = 0.0
  
  for inputs, labels in training_loader:
    inputs = inputs.to(device) # .to(device) passes the computations to the specified variable 'device'
    labels = labels.to(device)
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    _, preds = torch.max(outputs, 1)
    running_loss += loss.item()
    running_corrects += torch.sum(preds == labels.data)
    
  else:
    with torch.no_grad():
      for val_inputs, val_labels in validation_loader:
        val_inputs = val_inputs.to(device)
        val_labels = val_labels.to(device)
        val_outputs = model(val_inputs)
        val_loss = criterion(val_outputs, val_labels)
        
        _, val_preds = torch.max(val_outputs, 1)
        val_running_loss += val_loss.item()
        val_running_corrects += torch.sum(val_preds == val_labels.data)
        
      epoch_loss = running_loss/len(training_loader)
      epoch_acc = running_corrects.float() / len(training_loader)
      running_loss_history.append(epoch_loss)
      running_corrects_history.append(epoch_acc)
      
      val_epoch_loss = val_running_loss/len(validation_loader)
      val_epoch_acc = val_running_corrects.float() / len(validation_loader)
      val_running_loss_history.append(val_epoch_loss)
      val_running_corrects_history.append(val_epoch_acc)
      
      print('epoch: ', (e+1))
      print('training loss: {:4f}, acc{:4f} '.format(epoch_loss, epoch_acc.item()))
      print('validation loss: {:4f}, validation acc {:.4f} '.format(val_epoch_loss, val_epoch_acc.item()))

plt.plot(running_corrects_history, label='training accuracy')
plt.plot(val_running_corrects_history, label='validation accuracy')
plt.legend()

plt.plot(running_loss_history, label='training loss')
plt.plot(val_running_loss_history, label='validation loss')
plt.legend()

!pip3 install pillow==4.3.0

import PIL.ImageOps

import requests
from PIL import Image
# 'https://static.photocrowd.com/upl/eZ/cms.x3YEucSW-wg3j3ticEZA-collection_cover.jpeg'
url ='https://s.hdnux.com/photos/75/50/00/16154647/5/920x920.jpg'
response = requests.get(url, stream = True)
img = Image.open(response.raw)
plt.imshow(img)

img = transform(img)
plt.imshow(im_convert(img))

image = img.to(device).unsqueeze(0)
output = model(image)
_, pred = torch.max(output, 1)
print(classes[pred.item()])

"""
Display the network's performance on some new test data 
"""
dataiter = iter(validation_loader)
images, labels = dataiter.next()
images = images.to(device)
labels = labels.to(device)
output = model(images)
_, preds = torch.max(output, 1)

fig = plt.figure(figsize=(25,4))

for idx in np.arange(20):
  ax = fig.add_subplot(2,10, idx+1, xticks=[], yticks=[])
  plt.imshow(im_convert(images[idx]))
  ax.set_title("{} {}".format(str(classes[preds[idx].item()]), str(classes[labels[idx].item()])), color=("green" if preds[idx] ==labels[idx] else "red"))

