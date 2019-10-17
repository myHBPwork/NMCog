# neal.py
import pyNN.spiNNaker as spinn

class NealFunctions(object):
    """Function to isolate differences between different list synapse constructors.
    """
    def __init__(self, delay):
        self.DELAY = delay
    
    def nealprojection(self, pre_neurons, post_neurons, connector_list, inh_exc):
        #projection method for SpiNNaker
        conn_list = spinn.FromListConnector( connector_list )
        spinn.Projection(pre_neurons, post_neurons, conn_list, inh_exc)
