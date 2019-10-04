# neal.py
import pyNN.spiNNaker as spinn

class NealFunctions(object):
    """Function to isolate differences between different list synapse constructors.
    """
    
    @staticmethod    
    def neal_projection(pre_neurons, post_neurons, connector_list, inh_exc):
        #projection method for SpiNNaker
        conn_list = spinn.FromListConnector( connector_list )
        spinn.Projection(pre_neurons, post_neurons, conn_list, target= inh_exc)