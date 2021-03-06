import torch
import torchvision

from .custom_torch_transforms import TensorFlatten
import os
import numpy as np
def mnist_dataloader(data_path: str, batch_size: int, train:bool=True):
    """
    Load mnist image data from specified, convert to grayscaled (then binarised) tensors, flatten, return dataloader

    :param data_path: full path to data directory
    :param batch_size: batch size for dataloader
    :param train: whether to load train or test data
    :return dataloader: pytorch dataloader for mnist training dataset
    """
    # transforms to add to data
    transform = torchvision.transforms.Compose([
                                                torchvision.transforms.Grayscale(),
                                                torchvision.transforms.ToTensor(),
                                                lambda x: x>=0.5,
                                                lambda x: x.float(),
                                                TensorFlatten()
                                                ])

    mnist_data = torchvision.datasets.MNIST(data_path, transform=transform, train=train)
    dataloader = torch.utils.data.DataLoader(mnist_data, batch_size=batch_size, shuffle=True)

    return dataloader

def binarised_mnist_dataloader(data_path: str, batch_size: int, train=True, balanced=False):
    """
    Load binarised mnist image data from specified, convert to  tensors, flatten, return dataloader
    
    :param data_path: full path to data directory
    :param batch_size: batch size for dataloader
    :param train: whether to load train or test data
    :param balanced: whether to load balanced training data (if |train| is True).
    :return dataloader: pytorch dataloader for mnist training dataset
    """
    def read_file_to_numpy(file_name):
        mynumbers = []
        with open(file_name) as f:
            for line in f:
                mynumbers.append(np.array([float(n) for n in line.strip().split()]))
        return mynumbers

    train_file, valid_file, test_file, local_file = [os.path.join(data_path, 'binarizedMNIST/binarized_mnist_' + ds + '.amat') for ds in ['train', 'valid', 'test', 'local']]

    if train:
        if balanced:
            local_ar = read_file_to_numpy(local_file)
            tensorData = torch.Tensor(local_ar)
        else:
            train_ar, valid_ar = [read_file_to_numpy(f) for f in [train_file, valid_file]]
            train_ar = np.concatenate((train_ar, valid_ar), axis=0) # merge train and val into larger train set
            tensorData = torch.Tensor(train_ar)
    else:
        test_ar = read_file_to_numpy(test_file)
        tensorData = torch.Tensor(test_ar)

    # Do not shuffle the balanced training dataset.
    shuffle = not (train and balanced)

    targets = torch.Tensor([-1 for _ in range(len(tensorData))]).view(len(tensorData), -1) # these are dummy targets to match API

    tensorDataset = torch.utils.data.TensorDataset(tensorData, targets)
    dataloader = torch.utils.data.DataLoader(tensorDataset, batch_size=batch_size, shuffle=shuffle)

    return dataloader

def fashion_mnist_dataloader(data_path: str, batch_size: int, train:bool=True):
    """
        Load fashion_mnist image data from specified location, convert to tensors, binarise, flatten, and return dataloader
        Note: fashion_mnist already grayscaled in each channel.
        :param data_path: full path to data directory
        :param batch_size: batch size for dataloader
        :param train: whether to load train or test data
        :return dataloader: pytorch dataloader for mnist training dataset
        """
    # transforms to add to data
    transform = torchvision.transforms.Compose([
                                                torchvision.transforms.ToTensor(),
                                                lambda x: x>=0.5,
                                                lambda x: x.float(),
                                                TensorFlatten()
                                                ])
        
    fashion_mnist_data = torchvision.datasets.FashionMNIST(data_path, transform=transform, train=train)
    dataloader = torch.utils.data.DataLoader(fashion_mnist_data, batch_size=batch_size, shuffle=True)
                                                
    return dataloader

def cifar_dataloader(data_path: str, batch_size: int, train:bool=True, balanced=False):
    """
        Load CIFAR image data from specified location, convert to  tensors, binarise, and return dataloader
        Note: CIFAR already grayscaled in each channel.
        
        :param data_path: full path to data directory
        :param batch_size: batch size for dataloader
        :param train: whether to load train or test data
        :param balanced: whether to load balanced training data (if |train| is True).
        :return dataloader: pytorch dataloader for CIFAR training dataset
        """
    # transforms to add to data
    transform = torchvision.transforms.Compose([
                                                torchvision.transforms.ToTensor(),
                                                lambda x: x>=0.5,
                                                lambda x: x.float(),
                                                ])
        
    CIFAR10_data = torchvision.datasets.CIFAR10(data_path, transform=transform, train=train)

    if train and balanced:
        label_indices = [[] for i in range(10)]
        index = 0
        # Find at least 10 indices corresponding to each label.
        while any(len(indices) < 10 for indices in label_indices):
            _, label = CIFAR10_data[index]
            label_indices[label].append(index)
            index += 1
        # Extract the first 10 indices of each label.
        balanced_indices = [index for indices in label_indices for index in indices[:10]]
        # Form a balanced (unshuffled) datset from the extracted indices.
        CIFAR10_subset = torch.utils.data.Subset(CIFAR10_data, balanced_indices)
        dataloader = torch.utils.data.DataLoader(CIFAR10_subset, batch_size=batch_size, shuffle=False)
    else:
        dataloader = torch.utils.data.DataLoader(CIFAR10_data, batch_size=batch_size, shuffle=True)

    return dataloader
