import random
import numpy as np
from copy import deepcopy


class Network:
    def __init__(self, topology, learning_rate=0.1):
        self.topology = topology
        self.weights = []
        self.activations = []
        self.errors = []
        self.learning_rate = learning_rate

        for layer_index in range(len(topology.layers) - 1):
            self.weights.append([])
            for k_neuron in range(topology.layers[layer_index + 1][1]):
                self.weights[layer_index].append([])
                self.weights[layer_index][k_neuron].append(random.uniform(-1.0, 1.0))
                for j_neuron in range(topology.layers[layer_index][1]):
                    self.weights[layer_index][k_neuron].append(random.uniform(-1.0, 1.0))
        self.weights_copy = deepcopy(self.weights)  # enables us to avoid altering the weights until after all neuron
                                                    # errors are calculated

    def predict(self, row):
        self.activations = [[-1] + row]
        next_layer_input = np.array(row)
        for index in range(len(self.topology.layers)-1):
            next_layer_input = np.concatenate(([-1], next_layer_input))
            next_layer_input = np.array(self.weights[index]).dot(next_layer_input)
            next_layer_input = self.topology.layers[index+1][0](next_layer_input)
            if index == len(self.topology.layers)-2:
                self.activations.append(next_layer_input)
            else:
                self.activations.append(np.concatenate(([-1], next_layer_input)))

        return next_layer_input

    def fit(self, data, targets, test_data, test_targets, num_epochs=100, method="backprop", crossover_rate=0.02, mutation_rate = 0.02, population_size=100, fitness_callback=None):
        plot_details = [[],[],[]]
        if method == "backprop":
            for i in range(num_epochs):
                #if i % int(num_epochs / 10) == 0:
                print("Epoch " + str(i))
                for index, row in enumerate(data):
                    if len(data) > 5000 and index % (len(data) // 1000) == 0:
                        print("Beginning row " + str(index) + " of " + str(len(data)))
                    self.errors = []
                    self.predict(row)
                    output_layer_calculated = False
                    for neuron_layer_index in range(len(self.activations)-1, -1, -1):
                        if not output_layer_calculated:
                            self.calc_errors_and_update_weights(neuron_layer_index, targets[index])
                            output_layer_calculated = True
                        else:
                            self.calc_errors_and_update_weights(neuron_layer_index)
                self.weights = deepcopy(self.weights_copy)

                train_error = 0
                test_error = 0
                for j in range(len(data)):
                    train_error += (self.predict(data[j]) - targets[j]) ** 2
                train_error = np.sum(train_error) / len(data)
                for j in range(len(test_data)):
                    test_error += (self.predict(test_data[j]) - test_targets[j]) ** 2
                test_error = np.sum(test_error) / len(test_data)

                plot_details[0].append(i)
                plot_details[1].append(train_error)
                plot_details[2].append(test_error)
            return plot_details
        elif method == "genetic":
            print("Beginning genetic fitting. Creating population 0...")
            network_population = [deepcopy(self) for _ in range(population_size)]
            for network_index, network in enumerate(network_population):
                for layer_index, layer in enumerate(network.weights):
                    for k_neuron_index, k_neuron in enumerate(layer):
                        for j_neuron_index in range(len(k_neuron)):
                            network_population[network_index].weights[layer_index][k_neuron_index][j_neuron_index] = random.uniform(-1.0, 1.0)
            print("Beginning the circle of life...")
            for i in range(num_epochs):
                print("Determining fitness of population " + str(i) + " which has size " + str(len(network_population)))
                fitnesses = {}
                min_fitness = None
                max_fitness = None
                best_network = None
                for network_index in range(len(network_population)):
                    fitness = fitness_callback(network_population[network_index], test_data, test_targets)
                    if min_fitness is None:
                        min_fitness = fitness
                        max_fitness = fitness
                        best_network = network_population[network_index]
                    else:
                        if fitness < min_fitness:
                            min_fitness = fitness
                        if fitness > max_fitness:
                            max_fitness = fitness
                            best_network = network_population[network_index]
                    fitnesses[network_population[network_index]] = fitness


                self.weights = deepcopy(best_network.weights)
                train_error = 0
                test_error = 0
                for j in range(len(data)):
                    train_error += (self.predict(data[j]) - targets[j]) ** 2
                train_error = np.sum(train_error) / len(data)
                for j in range(len(test_data)):
                    test_error += (self.predict(test_data[j]) - test_targets[j]) ** 2
                test_error = np.sum(test_error) / len(test_data)

                plot_details[0].append(i)
                plot_details[1].append(train_error)
                plot_details[2].append(test_error)


                print("Deciding which networks should survive to breed.")
                networks_list = []
                for network_index in range(len(network_population)):
                    fitnesses[network_population[network_index]] = int(((fitnesses[network_population[network_index]] - min_fitness) / (max_fitness - min_fitness)) * 1000)
                    for j in range(int(fitnesses[network_population[network_index]])):
                        networks_list.append(network_population[network_index])
                print("Performing crossover and mutation...")
                network_population = []
                for _ in range(population_size // 4):
                    net1 = networks_list[random.randint(0, len(networks_list) - 1)]
                    while net1 in networks_list:
                        networks_list.remove(net1)
                    net2 = networks_list[random.randint(0, len(networks_list) - 1)]
                    while net2 in networks_list:
                        networks_list.remove(net2)
                    new_net1 = deepcopy(net1)
                    new_net2 = deepcopy(net2)
                    for layer_index in range(len(net1.weights)):
                        for k_neuron_index in range(len(net1.weights[layer_index])):
                            for j_neuron_index in range(len(net1.weights[layer_index][k_neuron_index])):
                                if random.uniform(0,1) <= crossover_rate:
                                    temp = new_net1.weights[layer_index][k_neuron_index][j_neuron_index]
                                    new_net1.weights[layer_index][k_neuron_index][j_neuron_index] = new_net2.weights[layer_index][k_neuron_index][j_neuron_index]
                                    new_net2.weights[layer_index][k_neuron_index][j_neuron_index] = temp
                                if random.uniform(0,1) <= mutation_rate:
                                    neg_modifier = (int(random.uniform(0,1) <= .5)-.5) * 2
                                    new_net1.weights[layer_index][k_neuron_index][j_neuron_index] *= (1 + .01 * neg_modifier)
                                if random.uniform(0,1) <= mutation_rate:
                                    neg_modifier = (int(random.uniform(0,1) <= .5)-.5) * 2
                                    new_net2.weights[layer_index][k_neuron_index][j_neuron_index] *= (1 + .01 * neg_modifier)
                    network_population.append(net1)
                    network_population.append(net2)
                    network_population.append(new_net1)
                    network_population.append(new_net2)
            return plot_details





    def calc_errors_and_update_weights(self, neuron_layer_index, targets=[]):
        """Update weights feeding into the referenced layer of neurons."""
        if neuron_layer_index == 0:
            return
        if len(targets) > 0: #if neuron_layer_index is the output layer
            neuron_layer_errors = []
            for j_neuron_index in range(len(self.activations[neuron_layer_index])):
                activation = self.activations[neuron_layer_index][j_neuron_index]
                error = activation * (1 - activation) * (activation - targets[j_neuron_index])
                neuron_layer_errors.append(error)
                for i_neuron_index in range(len(self.activations[neuron_layer_index - 1])):
                    i_neuron_activation = self.activations[neuron_layer_index - 1][i_neuron_index]
                    amount_to_change_weight = self.learning_rate * error * i_neuron_activation
                    self.weights_copy[neuron_layer_index - 1][j_neuron_index][i_neuron_index] -= amount_to_change_weight
            self.errors = [neuron_layer_errors] + self.errors
        else:
            neuron_layer_errors = []
            for j_neuron_index in range(1, len(self.activations[neuron_layer_index])):
                activation = self.activations[neuron_layer_index][j_neuron_index]
                weighted_sum_of_previous_errors = 0
                k_offset_for_bias = 1
                if neuron_layer_index == len(self.activations)-2:
                    k_offset_for_bias = 0
                for k_neuron_index in range(k_offset_for_bias, len(self.activations[neuron_layer_index + 1])):
                    weighted_sum_of_previous_errors += self.errors[0][k_neuron_index-1]*self.weights[neuron_layer_index][k_neuron_index-1][j_neuron_index]
                error = activation * (1 - activation) * weighted_sum_of_previous_errors
                neuron_layer_errors.append(error)
                for i_neuron_index in range(len(self.activations[neuron_layer_index - 1])):
                    i_neuron_activation = self.activations[neuron_layer_index - 1][i_neuron_index]
                    amount_to_change_weight = self.learning_rate * error * i_neuron_activation
                    self.weights_copy[neuron_layer_index - 1][j_neuron_index-1][i_neuron_index] -= amount_to_change_weight
            self.errors = [neuron_layer_errors] + self.errors

