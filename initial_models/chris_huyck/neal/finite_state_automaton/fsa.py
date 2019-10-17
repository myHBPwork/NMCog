# fsa.py
from neal import NealFunctions

class FSAFunctions(object):
    def __init__(self):
        self.initial_parameters()
        self.ncf = NealFunctions(self.delay)
    
    def initial_parameters(self):
        self.delay = 1.
        self.ca_size = 5 # only works for this size
        # SpiNNaker specific
        self.input_weight = 0.1
        self.intra_ca_weight = 0.03
        self.halfon_weight = 0.0017
        self.fulloff_weight = -0.3
        self.cell_params = {"v_thresh": -55., "v_reset": -70., "tau_refrac": 2., "tau_syn_E": 5.,
                            "v_rest": -65., "i_offset": 0.}

    # fsa (finite state automata) functions
    def turn_on_state(self, spike_source, start, neurons):
        # ignite a state from spike source using input_weight
        connector = []
        for to_offset in range(0, self.ca_size):
            to_neuron = to_offset + (start*self.ca_size)
            connector = connector + [(0, to_neuron, self.input_weight, self.delay)]
        self.ncf.nealprojection(spike_source, neurons, connector, 'excitatory')
    
    
    def make_ca(self, start, neurons):
        # creates a cell assembly assuming one kind of neuron in same population connected with intra_ca_weight
        connector = []
        for from_offset in range(0, self.ca_size):
            from_neuron = from_offset + (start*self.ca_size)
            for to_offset in range(0, self.ca_size):
                to_neuron = to_offset + (start*self.ca_size)
                if (to_neuron != from_neuron):
                    connector = connector + [(from_neuron, to_neuron,
                                              self.intra_ca_weight, self.delay)]
        self.ncf.nealprojection(neurons, neurons, connector, 'excitatory')
    
    def state_turn_halfon(self, start, finish, neurons):
        # one of the two states that connects one of the inputs to the third state
        # only difference w/ make_ca() is use of parameters: finish, halfon_weight
        connector = []
        for from_offset in range(0, self.ca_size):
            from_neuron = from_offset + (start*self.ca_size)
            for to_offset in range(0, self.ca_size):
                to_neuron = to_offset + (finish*self.ca_size)
                if (to_neuron != from_neuron):
                    connector = connector + [(from_neuron, to_neuron,
                                              self.halfon_weight, self.delay)]
        self.ncf.nealprojection(neurons, neurons, connector, 'excitatory')

    def state_turn_off(self, start, finish, neurons):
        # one of the two states that connects one of the inputs to the third state
        # only difference w/ state_turn_halfon() is use of parameters: fulloff_weight & inhibitory connection
        connector = []
        for from_offset in range(0, self.ca_size):
            from_neuron = from_offset + (start*self.ca_size)
            for to_offset in range(0, self.ca_size):
                to_neuron = to_offset + (finish*self.ca_size)
                if (to_neuron != from_neuron):
                    connector = connector + [(from_neuron, to_neuron,
                                              self.fulloff_weight, self.delay)]
        self.ncf.nealprojection(neurons, neurons, connector, 'inhibitory')
    
