# =============================================================================
# ~/spinnaker/discriminate/BuonomanoMerzenich.py
#
# created November 2019 Lungsi
#
# =============================================================================

import copy
import spynnaker8 as sim
import numpy as np
import quantities as pq
# for plotting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec
#from mpl_toolkits.axes_grid1.inset_locator import inset_axes
#import matplotlib.image as mpimg

class BuoMerz(object):
    """`SpiNNaker (sPyNNaker) <https://spinnakermanchester.github.io/>`_ implementation of Temporal Information Processing.
    
    **Architecture:**
    
    * Stimulus is sent to a network representing Douglas and Martin's `(1989) <https://doi.org/10.1162/neco.1989.1.4.480>`_ cortical IV and III layers.
    * Keeping with experimental observations the excitatory:inhibitory element is approximately 4:1.
    * The constituent excitatory and inhibitory elements are randomly connected (Buonomano &amp; Merzenich, 1997).
    * The elements are based on Integrate-and-fire current units (Buonomano &amp; Merzenich, 1995).
    
    The connection is based on Buonomano & Merzenich 1997 (Fig 3, p135)
        
    +----------------------+------------------+-----------------+------------------+-----------------+
    | Populations          | excitatory (III) | excitatory (IV) | inhibitory (III) | inhibitory (IV) |
    +======================+==================+=================+==================+=================+
    | **excitatory (III)** | 18/200 = 0.09    | -               | 12/200 = 0.06    | -               |
    +----------------------+------------------+-----------------+------------------+-----------------+
    | **excitatory (IV)**  | 18/120 = 0.15    | 15/120 = 0.125  | 12/120 = 0.1     | 10/120 = 0.083  |
    +----------------------+------------------+-----------------+------------------+-----------------+
    | **inhibitory (III)** | 8/50 = 0.16      | -               | 6/50 = 0.12      | -               |
    +----------------------+------------------+-----------------+------------------+-----------------+
    | **inhibitory (IV)**  | -                | 6/30 = 0.2      | -                | 4/30 = 0.133    |
    +----------------------+------------------+-----------------+------------------+-----------------+
    | **Input**            | -                | 15/100 = 0.15   | -                | 10/100 = 0.1    |
    +----------------------+------------------+-----------------+------------------+-----------------+
        
    **Note:**
        
    * The numerator correspond to the number of units (elements) within the recieving population.
    * The denominator is the convergence number of presynaptic inputs for each unit.
    * The decimal fraction are the probability values for the `FixedProbabilityConnector <http://neuralensemble.org/docs/PyNN/reference/connectors.html#built-in-connectors>`_ function.
        
    **Comments on connection with output layer:**
        
    The excitatory (III) population connects to the output layer `(1995) <https://doi.org/10.1126/science.7863330>`_ such that it proxies adaptation. The output layer populations recieves signal only at the end of the stimulus, i.e. during second pulse.
        
    Due to limitations with `SpNNaker8 <http://spinnakermanchester.github.io/>`_ here the connection is implemented such that it is made from the start of the simulation. However, only responses from the populations in the output layer at the end of the stimulus is returned.
    
    **References:**

    * Buonomano, D. V., &amp; Merzenich, M. M. (1995). *Temporal information transformed into a spatial code by a neural network with realistic properties*. Science: 1028-1030. DOI: `10.1126/science.7863330 <https://doi.org/10.1126/science.7863330>`_
    * Buonomano, D. V., &amp; Merzenich, M. M. (1997). Temporal Information Processing: A Computational Role for Paired-Pulse Facilitation and Slow Inhibition. In J. W. Donahoe &amp; V. Packard Dorsel (Eds.), *Neural-Networks Models of Cognition* (pp. 129-139). Netherlands, Amsterdam: Elsevier Science B. V.
    
    """
    # Network parameters (see Buonomano & Merzenich 1997, Fig 3, p 135)
    n_input = 100 # number of unit in input layer
    n_ex4 = 120   # number of excitatory units in layer-4
    n_inh4 = 30   # number of inhibitory units in layer-4
    n_ex3 = 200   # number of excitatory units in layer-3
    n_inh3 = 50   # number of inhibitory units in layer-3
    #w_ex3_out = 0 # initial weight
    #d_ex3_out = 0.1 # delay
    n_out = 100
    # Wiring of network components are done in __connect()
    # Unit (cell) parameters (see Buonomano & Merzenich 1995)
    ex_cell_parameters = {
            'v_rest':   -65.0,  # Resting membrane potential in mV.
            'cm':         1.5,  # Capacity of the membrane in 1.0 nF (default)
            'tau_m':     20.0,  # Membrane time constant in 20 ms (default)
            'tau_refrac': 0.1,  # Duration of refractory period in ms.
            'tau_syn_E':  4.0,  # Rise time of the excitatory synaptic alpha function in 0.5 ms (default)
            'tau_syn_I':  80.0,  # Rise time of the inhibitory synaptic alpha function in 0.5 ms (default)
            'i_offset':   0.0,  # Offset current in nA
            'v_reset':  -65.0,  # Reset potential after a spike in mV.
            'v_thresh': -40.0,  # Spike threshold in -50.0 mV (default)
            }
    inh_cell_parameters = copy.deepcopy(ex_cell_parameters)
    inh_cell_parameters["v_thresh"] = -50.
    # output-layer receives input from excitatory population of layer 3
    # Buonomano and Merzenich tested the network for intervals between 30 and 330 ms with 10 ms steps
    #dual_pulse_intervals = np.linspace(30, 330, num=31) # 30ms : 10ms : 330ms => 300/10 + 1 = 31 ms

    def __init__(self, intervals):
        self.dual_pulse_intervals = intervals # [80, 130, 180, 230, 280]
        self.str_dual_pulse_intervals = [ str(stimulus) for stimulus in self.dual_pulse_intervals]  # ["80", "130", "180", "230", "280"] for plotting
        self.data_for_all_intervals = {}
        for self.inter_pulse_interval in intervals:
            sim.setup(1)
            self.setup_inputchannel( [ self.inter_pulse_interval ] )
            self.input_src = self.__gen_input_src()
            [self.popIn, self.layer4, self.layer3, self.output] = self.__create_layers()
            self.__connect()
            self.__record()
            sim.run( self.runtime )
            [neo_popIn, neo_ex4, neo_inh4, neo_ex3, neo_inh3, neo_out] = self.__getdata()
            #sim.reset() # mod line
            sim.end()
            self.data_for_all_intervals.update(
                    { str(self.inter_pulse_interval): { "origin": self.stim_origin,
                                                        "end": self.stim_end,
                                                        "popIn": neo_popIn, "out": neo_out,
                                                        "ex4": neo_ex4, "inh4": neo_inh4,
                                                        "ex3": neo_ex3, "inh3": neo_inh3 }
                                                        } )
            
    def get_results(self):
        """
        Gets the recorded `Neo <https://neo.readthedocs.io/en/latest/>`_ objects.
        The only exception is for the output layer.
        Because of the reasons given above, for the output layer rather than a Neo object its `SpikeTrain <https://neo.readthedocs.io/en/latest/api_reference.html#neo.core.SpikeTrain>`_ are returned.
        They are the responses at the end of the stimulus.
        To help visualizing them along with `SpikeTrain <https://neo.readthedocs.io/en/latest/api_reference.html#neo.core.SpikeTrain>`_ from other layers a padding is also returned.
        
        Returns data as a dictionary such that
        
        +----------+---------------------------------------------------------------------------------------------+
        | Key      | Value                                                                                       |
        +==========+=============================================================================================+
        | "popIn"  | Neo object for input layer; contains ``SpikeTrain`` and ``Analogsignal``                    |
        +----------+---------------------------------------------------------------------------------------------+
        | "ex4"    | Neo object for excitatory population LayerIV; contains ``SpikeTrain`` and ``Analogsignal``  |
        +----------+---------------------------------------------------------------------------------------------+
        | "inh4"   | Neo object for inhibitory population LayerIV; contains ``SpikeTrain`` and ``Analogsignal``  |
        +----------+---------------------------------------------------------------------------------------------+
        | "ex3"    | Neo object for excitatory population LayerIII; contains ``SpikeTrain`` and ``Analogsignal`` |
        +----------+---------------------------------------------------------------------------------------------+
        | "inh3"   | Neo object for inhibitory population LayerIII; contains ``SpikeTrain`` and ``Analogsignal`` |
        +----------+---------------------------------------------------------------------------------------------+
        | "out"    | Dictionary for output layer with populations under the keys "out"+stimuli, say "out80"      |
        +----------+---------------------------------------------------------------------------------------------+
        | "origin" | float type representing start of the runtime                                                |
        +----------+---------------------------------------------------------------------------------------------+
        | "end"    | float type representing end of the runtime                                                  |
        +----------+---------------------------------------------------------------------------------------------+
        
        **Note:**
        
        Each population in the output layer (value of "out") is also a dictionary with keys "spiketrains" and "placeholder_axes".
        
        * The value for "placeholder_axes" is a list containing two lists.
        
            - The first represent t-axis from zero to start of second pulse of the stimuli.
            - The second is an array of zeros whose size is the same as the first.
        
        * The value for "spiketrains" is the `SpikeTrain` for *all* the populations 
        
        """
        return self.data_for_all_intervals


    def setup_inputchannel(self, all_intervals):
        """Given a stimulus, i.e. interval values this function creates an input channel for it.
        
        The input channel is such that
        
        ::
        
                         ___|-interval/stimulus-|___
                        |   |                   |   |
          origin________|   |___________________|   |________end
               |---t0---|-T-|                   |-T-|---t0---|
               |------------------runtime--------------------|
        
        
        Note that the above dual-pulse train represented in ``self.input_channel`` is used to create a spiking version using the private function ``__gen_input_src()``.
        
        In addition to the ``self.input_channel`` this function also sets the attributes: ``self.stim_origin``, ``self.stim_end``, and ``self.runtime``.
        
        **Note:**
        
        * Interval value or the inter-pulse interval is the temporal information carried by the stimulus.
        * The interval value represents the stimulus; if it is a list of values it is a list of stimuli.
        
        It should be pointed out that
        
        * Regardless of one or more stimulus it is here repesented in a list for the sake of not breaking previous code.
        * So this is a practical choice and does not contradict the above mentioned assumptions.
        
        """
        # Input population of size 100
        self.period = 5
        kHz_tone = lambda t0: list( np.linspace(t0, t0+self.period, 3) )
        self.t0 = 20
        origin = 0
        joinpulses = lambda headlist, taillist: [ headlist.append(i) for i in taillist ]
        joinInchnl = lambda origin, oldInchnl, pulse1: pulse1 if origin==0 else oldInchnl+pulse1
        self.input_channel = []
        self.stim_origin = [] # guide for plotting
        self.stim_end = []    # guide for plotting
        #all_intervals = [80, 130] #, 130, 180 #ms number of stimuli
        self.runtime = 0
        for an_interval in all_intervals:
            pulse1_t0 = origin + self.t0
            pulse2_t0 = pulse1_t0 + self.period + an_interval
            pulse1 = kHz_tone(pulse1_t0)
            pulse2 = kHz_tone(pulse2_t0)
            joinpulses(pulse1, pulse2)
            self.input_channel = joinInchnl(origin, self.input_channel, pulse1)
            self.stim_origin.append(origin)
            self.stim_end.append( pulse1[-1] )
            # update for next
            origin = pulse1[-1] + self.t0
            self.runtime = self.runtime + ( self.t0 + self.period + an_interval + self.period + self.t0 )

    # Generate input source
    def __gen_input_src(self):
        """The above created `self.input_channel` is used to create a spiking version of it.
        """
        spike_times = []
        for i in range( BuoMerz.n_input ):
            spike_times.append( self.input_channel )
        return sim.Population( BuoMerz.n_input, sim.SpikeSourceArray, {'spike_times': spike_times}, label="input" )

    # Private function for setting up the layers
    def __create_layers(self):
        """Creates layers: input, IV, III, and output.
        
        * The input layer is represented as a population of `self.n_input`.
        * Layer IV is represented as a dictionary with "exc" and "inh" for excitatory and inhibitory populations.
        * Similarly, for layer III.
        * The output layer is represented as a dictionary with keys of the form "out"+interval value, each representing a population.
        
        **Note:**
        
        * Interval value or the inter-pulse interval is the temporal information carried by the stimulus.
        * The interval value represents the stimulus; if it is a list of values it is a list of stimuli.
        
        """
        # input population
        popIn = sim.Population( BuoMerz.n_input, sim.IF_curr_alpha(), label="input" )
        
        # layer-4 receives input_src containing the PPF (paired-pulse facilitation)
        layer4 = { "exc": sim.Population( BuoMerz.n_ex4, sim.IF_curr_alpha(**BuoMerz.ex_cell_parameters), label="ex4" ),
                   "inh": sim.Population( BuoMerz.n_inh4, sim.IF_curr_alpha(**BuoMerz.inh_cell_parameters), label="inh4" ) }
        
        # layer-3 receives input from layer 4
        layer3 = { "exc": sim.Population( BuoMerz.n_ex3, sim.IF_curr_alpha(**BuoMerz.ex_cell_parameters), label="ex3" ),
                   "inh": sim.Population( BuoMerz.n_inh3, sim.IF_curr_alpha(**BuoMerz.inh_cell_parameters), label="inh3" ) }

        # output-layer receives input from excitatory population of layer 3
        output = {}
        #for i in np.nditer(BuoMerz.dual_pulse_intervals): # Buonomano and Merzenich tested the network for intervals between 30 and 330 ms with 10 ms steps
        for i in self.dual_pulse_intervals:
            unit_label = "output_for_"+str(i)
            unit_key = "out"+str(i)
            unit_val = sim.Population( BuoMerz.n_out, sim.IF_curr_alpha(**BuoMerz.ex_cell_parameters), label= unit_label )
            output.update( {unit_key: unit_val} )
        return [popIn, layer4, layer3, output]

    # Private function for setting up the wiring and connections
    def __connect(self):
        """ Based on Buonomano & Merzenich 1997 (Fig 3, p135)
        
        +----------------------+------------------+-----------------+------------------+-----------------+
        | Populations          | excitatory (III) | excitatory (IV) | inhibitory (III) | inhibitory (IV) |
        +======================+==================+=================+==================+=================+
        | **excitatory (III)** | 18/200 = 0.09    | -               | 12/200 = 0.06    | -               |
        +----------------------+------------------+-----------------+------------------+-----------------+
        | **excitatory (IV)**  | 18/120 = 0.15    | 15/120 = 0.125  | 12/120 = 0.1     | 10/120 = 0.083  |
        +----------------------+------------------+-----------------+------------------+-----------------+
        | **inhibitory (III)** | 8/50 = 0.16      | -               | 6/50 = 0.12      | -               |
        +----------------------+------------------+-----------------+------------------+-----------------+
        | **inhibitory (IV)**  | -                | 6/30 = 0.2      | -                | 4/30 = 0.133    |
        +----------------------+------------------+-----------------+------------------+-----------------+
        | **Input**            | -                | 15/100 = 0.15   | -                | 10/100 = 0.1    |
        +----------------------+------------------+-----------------+------------------+-----------------+
        
        **Note:**
        
        * The numerator correspond to the number of units (elements) within the recieving population.
        * The denominator is the convergence number of presynaptic inputs for each unit.
        * The decimal fraction are the probability values for the `sim.FixedProbabilityConnector` function.
        
        **Comments on connection with output layer:**
        
        The excitatory (III) population connects to the output layer `(1995) <https://doi.org/10.1126/science.7863330>`_ such that it proxies adaptation. The output layer populations recieves signal only at the end of the stimulus, i.e. during second pulse.
        
        Due to limitations with `SpNNaker8 <http://spinnakermanchester.github.io/>`_ here the connection is implemented such that it is made from the start of the simulation. However, only responses from the populations in the output layer at the end of the stimulus is returned.
        
        """
        wire_ex3ex3 = sim.FixedProbabilityConnector(0.09, allow_self_connections=True)
        wire_ex3inh3 = sim.FixedProbabilityConnector(0.06, allow_self_connections=False)
        wire_ex4ex3 = sim.FixedProbabilityConnector(0.15, allow_self_connections=False)
        wire_ex4ex4 = sim.FixedProbabilityConnector(0.125, allow_self_connections=True)
        wire_ex4inh3 = sim.FixedProbabilityConnector(0.1, allow_self_connections=False)
        wire_ex4inh4 = sim.FixedProbabilityConnector(0.083, allow_self_connections=False)
        wire_inh3ex3 = sim.FixedProbabilityConnector(0.16, allow_self_connections=False)
        wire_inh3inh3 = sim.FixedProbabilityConnector(0.12, allow_self_connections=True)
        wire_inh4ex4 = sim.FixedProbabilityConnector(0.2, allow_self_connections=False)
        wire_inh4inh4 = sim.FixedProbabilityConnector(0.133, allow_self_connections=True)
        wire_popInex4 = sim.FixedProbabilityConnector(0.15, allow_self_connections=False)
        wire_popIninh4 = sim.FixedProbabilityConnector(0.1, allow_self_connections=False)
        wire_inputpopIn = sim.FixedProbabilityConnector(0.25, allow_self_connections=False)
        # Below is custom made and not given by Buonomano & Merzenich
        wire_ex3output = sim.FixedProbabilityConnector(0.15, allow_self_connections=False)
        ### NOW CONNECT
        connect_ex3ex3 = sim.Projection( self.layer3["exc"], self.layer3["exc"], wire_ex3ex3,
                                         sim.StaticSynapse(weight=5.), receptor_type="excitatory" )
        connect_ex3inh3 = sim.Projection( self.layer3["exc"], self.layer3["inh"], wire_ex3inh3,
                                          sim.StaticSynapse(weight=5.), receptor_type="excitatory" )
        connect_ex4ex3 = sim.Projection( self.layer4["exc"], self.layer3["exc"], wire_ex4ex3,
                                         sim.StaticSynapse(weight=5.), receptor_type="excitatory" )
        connect_ex4ex4 = sim.Projection( self.layer4["exc"], self.layer4["exc"], wire_ex4ex4,
                                         sim.StaticSynapse(weight=2.5), receptor_type="excitatory" )
        connect_ex4inh3 = sim.Projection( self.layer4["exc"], self.layer3["inh"], wire_ex4inh3,
                                          sim.StaticSynapse(weight=5.), receptor_type="excitatory" )
        connect_ex4inh4 = sim.Projection( self.layer4["exc"], self.layer4["inh"], wire_ex4inh4,
                                          sim.StaticSynapse(weight=2.5), receptor_type="excitatory" )
        connect_inh3ex3 = sim.Projection( self.layer3["inh"], self.layer3["exc"], wire_inh3ex3,
                                          sim.StaticSynapse(weight=5.), receptor_type="inhibitory" )
        connect_inh3inh3 = sim.Projection( self.layer3["inh"], self.layer3["inh"], wire_inh3inh3,
                                           sim.StaticSynapse(weight=5.), receptor_type="inhibitory" )
        connect_inh4ex4 = sim.Projection( self.layer4["inh"], self.layer4["exc"], wire_inh4ex4,
                                          sim.StaticSynapse(weight=2.5), receptor_type="inhibitory" )
        connect_inh4inh4 = sim.Projection( self.layer4["inh"], self.layer4["inh"], wire_inh4inh4,
                                           sim.StaticSynapse(weight=2.5), receptor_type="inhibitory" )
        connect_popInex4 = sim.Projection( self.popIn, self.layer4["exc"], wire_popInex4,
                                           sim.StaticSynapse(weight=5.0), receptor_type="excitatory" )
        connect_popIninh4 = sim.Projection( self.popIn, self.layer4["inh"], wire_popIninh4,
                                            sim.StaticSynapse(weight=5.0), receptor_type="excitatory" )
        connect_inputpopIn = sim.Projection( self.input_src, self.popIn, wire_inputpopIn,
                                             sim.StaticSynapse(weight=1.0), receptor_type="excitatory" )
        # connect the exc3 unit with output layer
        #for i in np.nditer(BuoMerz.dual_pulse_intervals): # Buonomano and Merzenich tested the network for intervals between 30 and 330 ms with 10 ms steps
        for i in self.dual_pulse_intervals:
            if i == self.inter_pulse_interval:
                unit_key = "out"+str(i)
                prj = [ sim.Projection( self.layer3["exc"], self.output[unit_key], wire_ex3output,
                                        sim.StaticSynapse(weight=100.0), receptor_type="excitatory" )
                       for k in self.output.keys() if k==unit_key ]
                        
    # Private function for recording
    def __record(self):
        """Records into `Neo <https://neo.readthedocs.io/en/latest/>`_ object for the four layers: input, IV, III, and output.
        """
        self.input_src.record("all")
        self.popIn.record("all")
        rec = lambda pop: [ subpop.record("all") for subpop in pop.values() ]
        rec( self.layer4 )
        rec( self.layer3 )
        rec( self.output )

    # Private function for extracting recorded data
    def __getdata(self):
        """
        Gets the recorded `Neo <https://neo.readthedocs.io/en/latest/>`_ objects.
        The only exception is for the output layer. Because of the reasons given above, for the output layer rather than a Neo object its `SpikeTrains` are returned. They are the responses at the end of the stimulus. To help visualizing them along with `SpikeTrains` from other layers a padding is also returned.
        """
        #spikes_input_src = self.input_src.get_data("spikes")
        neo_popIn = self.popIn.get_data(variables=["spikes", "v"])
        neo_ex4 = self.layer4["exc"].get_data(variables=["spikes", "v"])
        neo_inh4 = self.layer4["inh"].get_data(variables=["spikes", "v"])
        neo_ex3 = self.layer3["exc"].get_data(variables=["spikes", "v"])
        neo_inh3 = self.layer3["inh"].get_data(variables=["spikes", "v"])
        # For the proxy output layer get just the spikes corresponding to the second pulse
        neo_out = {}
        for key in self.output.keys():
            #neo_out.update( { key: self.output[key].get_data( variables=["spikes", "v"] ) } )
            for_all_neurons = self.output[key].get_data( variables=["spikes"] )
            spktrains_all = []
            for spktrain in for_all_neurons.segments[0].spiketrains:
                spktrains_all.append( spktrain[ spktrain > self.stim_end[0]*pq.ms] ) # spikes for 2nd pulse only
            neo_out.update( { key: {"spiketrains": spktrains_all,
                                    "placeholder_axes": self.__placeholder_x_y(neo_ex3) } } )
        return [neo_popIn, neo_ex4, neo_inh4, neo_ex3, neo_inh3, neo_out]

    # Private function for dummy time and y-axis for output layer
    def __placeholder_x_y(self, neo_ex3):
        """
        Returns a list containing two lists. The first represent t-axis from zero to start of second pulse of the stimuli. The second is an array of zeros whose size is the same as the first.
        """
        spks = neo_ex3.segments[0].spiketrains[0] # other neo_xyz objects should also work
        # tstart = spks.t_start or tstart = spks.t_start + self.t0 + self.period
        tstart = spks.t_start #+ self.t0*pq.ms + self.period*pq.ms
        ndata = spks.sampling_rate * ( spks.t_stop - tstart )
        taxis = np.linspace( tstart, spks.t_stop, num=ndata.magnitude )
        return [ taxis, np.zeros( taxis.shape ) ]
    
    # Private function for checking and getting the interval for plotting all the layers
    def __get_interval_of_interest(self, variable_argument_intv_tuple):
        """."""
        if len(variable_argument_intv_tuple)==0 and len(self.str_dual_pulse_intervals)==1:
            return self.str_dual_pulse_intervals()[0]
        elif (len(variable_argument_intv_tuple)==0 and len(self.str_dual_pulse_intervals)>1) or (len(variable_argument_intv_tuple)>1):
            raise ValueError("Argument must be a string representing single interval (stimulus).")
        else:
            if type( variable_argument_intv_tuple[0] ) is str:
                return variable_argument_intv_tuple[0]
            else:
                return str( variable_argument_intv_tuple[0] )
        
    # Plotting functions
    def plot_all_layers(self, *intv):
        """Visualize spikes for populations in all layers; starting from below: input, excitatory in LayerIV, inhibitory in LayerIV, excitatory in LayerIII, inhibitory in LayerIII and lastly **a** population in the output layer at the top.
        y-axis are labelled with respective population and x-axis is the time in milliseconds.
        """
        y = self.data_for_all_intervals
        #z = "80"
        z = self.__get_interval_of_interest(intv)
        #
        fig, ( (sp1),
               (sp2),
               (sp3),
               (sp4),
               (sp5),
               (sp6) ) = plt.subplots(6,1,sharex=True)
        fig.suptitle("Temporal Info. Processing for S = "+z+" ms")

        [ sp1.plot(y[z]["out"]["out"+z]["placeholder_axes"], alpha=0.0) if i==0 else
          sp1.eventplot( y[z]["out"]["out"+z]["spiketrains"] ) for i in range(2) ]
        sp1.set(ylabel="output")

        sp2.eventplot( y[z]["inh3"].segments[0].spiketrains )
        sp2.set(ylabel="inh3")

        sp3.eventplot( y[z]["ex3"].segments[0].spiketrains )
        sp3.set(ylabel="ex3")

        sp4.eventplot( y[z]["inh4"].segments[0].spiketrains )
        sp4.set(ylabel="inh4")

        sp5.eventplot( y[z]["ex4"].segments[0].spiketrains )
        sp5.set(ylabel="ex4")

        sp6.eventplot( y[z]["popIn"].segments[0].spiketrains )
        sp6.set(ylabel="popIn")
        sp6.set(xlabel="time (ms)")

        plt.show()
    
    def plot_output_layer_timeseries(self):
        """Visualize spikes from each population in the output layer as a time-series.
        y-axis represent each unit in a population and x-axis is time in milliseconds.
        """
        y = self.data_for_all_intervals
        intvs = self.str_dual_pulse_intervals #["80", "130", "180", "230", "280"]
        clrs = ['C{}'.format(i) for i in range(len(intvs))] # colors for respective interval
        legpatches = []
        fig, ( (sp) ) = plt.subplots(1,1,sharex=True)
        fig.suptitle("Populations (output layer) triggered by respective stimulus")
        for j in range( len(intvs) ):
            [ sp.plot(y[intvs[j]]["out"]["out"+intvs[j]]["placeholder_axes"], alpha=0.0) if i==0 else
              sp.eventplot( y[intvs[j]]["out"]["out"+intvs[j]]["spiketrains"], colors=clrs[j] ) for i in range(2) ]
            legpatches.append( mpatches.Patch(color=clrs[j], label=intvs[j]) )
        sp.set(ylabel="unit in population")
        sp.set(xlabel="time (ms)")
        sp.legend( handles=legpatches, shadow=True )
    
    def plot_output_layer_vertical(self):
        """Visualize spikes from each population in the output layer as one-above-eachother.
        Left y-axis represent the population and right y-axis the stimulus.
        """
        y = self.data_for_all_intervals
        intvs = self.str_dual_pulse_intervals #["80", "130", "180", "230", "280"]
        #
        mrows = len(intvs) # mrows of subplots
        clrs = ['C{}'.format(i) for i in range(mrows)] # mrows of colors
        poplabels = self.__population_labels(mrows)
        #
        fig, splist = plt.subplots( mrows, 1 )
        fig.suptitle("Populations (output layer) triggered by respective stimulus")
        for i in range(mrows):
            z = intvs[i]
            # plot
            splist[i].eventplot( y[z]["out"]["out"+z]["spiketrains"],
                                 colors=clrs[i] )
            splist[i].margins(10, 0.5) # zoom-out
            # legend
            z_patch = mpatches.Patch( color=clrs[i], label=z )
            splist[i].legend( handles=[z_patch], shadow=True )
            # left yticks and ylabel
            splist[i].set_yticks( [] )
            splist[i].set( ylabel="output\npop-"+poplabels[i] )
            # right yticks and ylabel
            rightside = splist[i].twinx()
            rightside.set_yticks( [] )
            rightside.set_ylabel( "stimulus\n"+z, multialignment='center' )
        # remove vertical gap between subplots
        plt.subplots_adjust( hspace=.0 )
        plt.xticks( [] ) # remove xticks
        plt.show()
    
    # Private function for generating labels for neuron populations
    def __population_labels(self, mrows):
        """Generates ``mrows`` of English letters from "a" to ...
        This is the naive method shown in https://www.geeksforgeeks.org/python-ways-to-initialize-list-with-alphabets/
        """
        labellist = []
        alpha = "a"
        for i in range(0, mrows):
            labellist.append( alpha )
            alpha = chr( ord(alpha) + 1 )
        return labellist
    
    def plot_output_layer_timeseries_vertical(self):
        """Visualize spikes from each population in the output layer as a time-series.
        But unlike :py:meth:`plot_output_layer_timeseries` this one plots one-above-eachother.
        Left y-axis represent units in a population and right y-axis the respective population.
        """
        y = self.data_for_all_intervals
        intvs = self.str_dual_pulse_intervals #["80", "130", "180", "230", "280"]
        #
        mrows = len(intvs) # mrows of subplots
        clrs = ['C{}'.format(i) for i in range(mrows)] # mrows of colors
        poplabels = self.__population_labels(mrows)
        #
        fig, splist = plt.subplots( mrows, 1, sharex=True )
        fig.suptitle("Populations (output layer) triggered by respective stimulus")
        for j in range(mrows):
            z = intvs[j]   # a stimulus
            sp = splist[j] # a subplot
            # plot
            [ sp.plot(y[z]["out"]["out"+z]["placeholder_axes"], alpha=0.0) if i==0 else
              sp.eventplot( y[z]["out"]["out"+z]["spiketrains"], colors=clrs[j] ) for i in range(2) ]
            # legend
            z_patch = mpatches.Patch(color=clrs[j], label=z)
            sp.legend( handles=[z_patch], shadow=True )
            # xticks and xlabel only for bottom subplot
            if j==(mrows-1):
                sp.set(xlabel="time (ms)")
            #else:
            #    sp.set_xticks( [] )
            # left ylabel
            sp.set(ylabel='units in\npop')
            # right yticks and ylabel
            rightside = sp.twinx()
            rightside.set_yticks( [] )
            rightside.set_ylabel( "pop-"+poplabels[j] )
        plt.subplots_adjust( hspace=.0 )
        plt.show()