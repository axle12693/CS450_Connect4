import math
import numpy as np

class Topology:
    def __init__(self):
        self.layers = []
        self.last_layer_type = ""
        self.implemented = {"Input": ("Sigmoid",), "Sigmoid": ("Sigmoid",)}  # key = layer j, value = layer k
        self.implementation = {"Sigmoid": Topology.Sigmoid, "Input": Topology.Input}

    def add_layer(self, num_neurons, activation_type="Sigmoid"):
        if len(self.layers) > 0 and activation_type not in self.implemented[self.last_layer_type]:
            raise Exception("Functionality not built yet for transition from " + self.layers[len(self.layers) - 1] + " to " + activation_type)
        self.layers.append((self.implementation[activation_type], num_neurons))
        self.last_layer_type = activation_type

    @staticmethod
    def Sigmoid(inputs):
        return 1 / (1 + np.exp(-1*inputs))

    @staticmethod
    def Input(data_in):
        return data_in
