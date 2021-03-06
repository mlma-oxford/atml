from abc import ABC, abstractmethod

import torch
import torch.nn as nn
import torch.nn.functional as F

from typing import Dict

class _BaseFlow(nn.Module, ABC):

    def __init__(self, config: Dict):

        nn.Module.__init__(self)

        self.initialisation = config.get(["flow", "weight_initialisation"])
        if self.initialisation == "normal":
            self.initialisation_std = config.get(["flow", "weight_initialisation_std"])

        self._construct_layers()

        self.activation_function = config.get(["flow", "nonlinearity"])
        if self.activation_function == 'elu':
            self.activation = F.elu
            self.activation_derivative = self.elu_derivative
        elif self.activation_function == 'tanh':
            self.activation = torch.tanh
            self.activation_derivative = self.tanh_derivative

    @abstractmethod
    def _construct_layers(self) -> None:
        """
        """
        raise NotImplementedError("Base class method")

    def _initialise_weights(self, layer: torch.Tensor) -> torch.Tensor:
        """
        Weight initialisation method for given layer
        """
        if self.initialisation == "xavier_uniform":
            nn.init.xavier_uniform_(layer.weight)
            nn.init.constant_(layer.bias, 0)
        elif self.initialisation == "xavier_normal":
            nn.init.xavier_normal_(layer.weight)
            nn.init.constant_(layer.bias, 0)
        elif self.initialisation == "normal":
            nn.init.normal_(layer.weight, std=self.initialisation_std)
            nn.init.normal_(layer.bias, std=self.initialisation_std)
        elif self.initialisation == "default":
            pass
        else:
            raise ValueError("Initialisation {} not recognised".format(self.initialisation))

        return layer

    def tanh_derivative(self, x: torch.Tensor) -> torch.Tensor:
        return 1 - self.activation(x) ** 2

    def elu_derivative(self, x):
        raise NotImplementedError("Derivative for elu nonlinearity not implemented")

    @abstractmethod
    def forward(self, z0: torch.Tensor):
        raise NotImplementedError("Base class method")

