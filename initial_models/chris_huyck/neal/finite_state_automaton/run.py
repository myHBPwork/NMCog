# run.py
import pyNN.spinNNaker as spinn

from fsa import FSAFunctions

class RunFunctions(object):
    def __init__(self):
        self.fsaf = FSAFunctions()
        spinn.setup( timestep = self.fsaf.delay, min_delay = self.fsaf.delay,
                     max_delay = self.fsaf.delay, debug=0 )

    def create_neurons(self):
        # only for SpiNNaker
        cells = Population(100, spinn.IF_cond_exp, self.fsaf.cell_params)
        return cells
    
    def setup_recording(self, cells):
        # only for SpiNNaker
        return cells.record()
    
    def create_inputs(self):
        # two inputs
        spike_array0 = {"spike_times": [ [10.0] ]}
        spike_array1 = {"spike_times": [ [50.0] ]}
        spike_gen0 = spinn.Population( 1, spinn.SpikeSourceArray, spike_array0,
                                       label="inputSpikes_0" )
        spike_gen1 = spinn.Population( 1, spinn.SpikeSourceArray, spike_array1,
                                       label="inputSpikes_1" )
        return [spike_gen0, spike_gen1]
    
    def three_state_fsa(self, first_spike_gen, second_spike_gen, state_cells):
        # build FSA
        self.fsaf.turn_on_state( first_spike_gen, 0, state_cells )
        self.fsaf.turn_on_state( second_spike_gen, 1, state_cells )
        #
        self.fsaf.make_ca(0, state_cells)
        self.fsaf.make_ca(1, state_cells)
        self.fsaf.make_ca(2, state_cells)
        #
        self.fsaf.state_turn_halfon(0, 2, state_cells)
        self.fsaf.state_turn_off(2, 0, state_cells)
        # to check state 0 alone does not turn on state 2
        # comment below
        self.fsaf.state_turn_halfon(1, 2, state_cells)
        self.fsaf.state_turn_off(2, 1, state_cells)
    
    def run_fsa(self, duration):
        # only for SpiNNaker
        spinn.run(duration)
        
    def print_results(self, state_cells):
        state_cells.printSpikes("temp.sp")
