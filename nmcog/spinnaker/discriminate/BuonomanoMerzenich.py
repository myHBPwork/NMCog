# ../spinnaker/discriminate/BuonomanoMerzenich.py

"""
SpiNNaker implementation of Temporal Information Processing.

Buonomano, D. V., & Merzenich, M. M. (1997). Temporal Information Processing: A Computational Role For Paired-Pulse Facilitation and Slow Inhibition. In J. W. Donahoe & V. Packard Dorsel (Eds) Neural-Networks Models of Cognition. Amsterdam: North-Holland, Elsevier Science B. V. ISBN: 0444819312
"""

import copy
import spynnaker8 as sim
import numpy as np
import quantities as pq

class BuoMerz(object):
    """
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
        self.dual_pulse_intervals = intervals
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
            sim.end()
            self.data_for_all_intervals.update(
                    { str(self.inter_pulse_interval): { "origin": self.stim_origin,
                                                        "end": self.stim_end,
                                                        "popIn": neo_popIn, "out": neo_out,
                                                        "ex4": neo_ex4, "inh4": neo_inh4,
                                                        "ex3": neo_ex3, "inh3": neo_inh3 }
                                                        } )
    def get_results(self):
        return self.data_for_all_intervals


    def setup_inputchannel(self, all_intervals):
        """
        """
        # Input population of size 100
        T = 5
        kHz_tone = lambda t0: list( np.linspace(t0, t0+T, 3) )
        t0 = 20
        origin = 0
        joinpulses = lambda headlist, taillist: [ headlist.append(i) for i in taillist ]
        joinInchnl = lambda origin, oldInchnl, pulse1: pulse1 if origin==0 else oldInchnl+pulse1
        self.input_channel = []
        self.stim_origin = [] # guide for plotting
        self.stim_end = []    # guide for plotting
        #all_intervals = [80, 130] #, 130, 180 #ms number of stimuli
        self.runtime = 0
        for an_interval in all_intervals:
            pulse1_t0 = origin + t0
            pulse2_t0 = pulse1_t0 + T + an_interval
            pulse1 = kHz_tone(pulse1_t0)
            pulse2 = kHz_tone(pulse2_t0)
            joinpulses(pulse1, pulse2)
            self.input_channel = joinInchnl(origin, self.input_channel, pulse1)
            self.stim_origin.append(origin)
            self.stim_end.append( pulse1[-1] )
            # update for next
            origin = pulse1[-1] + t0
            self.runtime = self.runtime + ( 20 + T + an_interval + T + 20 )

    # Generate input source
    def __gen_input_src(self):
        spike_times = []
        for i in range( BuoMerz.n_input ):
            spike_times.append( self.input_channel )
        return sim.Population( BuoMerz.n_input, sim.SpikeSourceArray, {'spike_times': spike_times}, label="input" )

    # Private function for setting up the layers
    def __create_layers(self):
        """
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
                ex3       ex4       inh3       inh4
        ex3   18/200       -       12/200       -
        ex4   18/120     15/120    12/120     10/120
        inh3   8/50        -        6/50        -
        inh4    -         6/30       -         4/30
        input   -        15/100      -        10/100

        Alternatively, above as probability values

                ex3       ex4       inh3       inh4
        ex3    0.09        -        0.06        -
        ex4    0.15      0.125      0.1        0.083
        inh3   0.16        -        0.12        -
        inh4    -        0.2         -         0.133
        input   -        0.15        -         0.1
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
                                        sim.StaticSynapse(weight=10.0), receptor_type="excitatory" ) if k==unit_key else
                        sim.Projection( self.layer3["exc"], self.output[unit_key], wire_ex3output,
                                        sim.StaticSynapse(weight=0.0), receptor_type="inhibitory" ) for k in self.output.keys() ]
        return prj

    # Private function for recording
    def __record(self):
        self.input_src.record("all")
        self.popIn.record("all")
        rec = lambda pop: [ subpop.record("all") for subpop in pop.values() ]
        rec( self.layer4 )
        rec( self.layer3 )
        rec( self.output )

    # Private function for extracting recorded data
    def __getdata(self):
        #spikes_input_src = self.input_src.get_data("spikes")
        neo_popIn = self.popIn.get_data(variables=["spikes", "v"])
        neo_ex4 = self.layer4["exc"].get_data(variables=["spikes", "v"])
        neo_inh4 = self.layer4["inh"].get_data(variables=["spikes", "v"])
        neo_ex3 = self.layer3["exc"].get_data(variables=["spikes", "v"])
        neo_inh3 = self.layer3["inh"].get_data(variables=["spikes", "v"])
        #neo_out = []
        #for values in self.output.values():
        #    neo_out.append( values.get_data(variables=["spikes", "v"]) )
        neo_out = {}
        for key in self.output.keys():
            neo_out.update( { key: self.output[key].get_data( variables=["spikes", "v"] ) } )
        return [neo_popIn, neo_ex4, neo_inh4, neo_ex3, neo_inh3, neo_out]

    # Private function
    def __adapted_output(self):
        sim.setup(1)
        t_initial = self.data_for_all_intervals[self.inter_pulse_interval]["end"][0] - 5
        t_final = self.data_for_all_intervals[self.inter_pulse_interval]["end"][0] + 20
        # get spikes from ex3 corresponding to last pulse
        overall_spiketrains = self.data_for_all_intervals[self.inter_pulse_interval]["ex3"].segments[0].time_slice(
                                                t_start = t_initial * pq.ms, t_stop = t_final * pq.ms ).spiketrains )
        # self.inter_pulse_interval
        learn_output = self.__create_output()
        self.__connect_to_learn(laststim_ex3, learn_output)
        # Record
        [ subpop.record("all") for subpop in learn_output.values() ]
        sim.run( runtime? )
        neo_out = {}
        [ neo_out.update( {key: learn_output[key].get_data( variables=["spikes"] )} ) for key in learn_output.keys() ]
        sim.end()
        # Finally append the above recorded spike train to appropriate position in self.data_for_all_intervals


