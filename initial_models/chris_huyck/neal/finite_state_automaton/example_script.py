# script to run two state FSA
from fsa import FSAFunctions
from run import RunFunctions

run_duration = 200

fsaf = FSAFunctions()
runf = RunFunctions()

# setup input
spike_gens = runf.create_inputs()
first_spike_gen = spike_gens[0]
secnd_spike_gen = spike_gens[1]

# setup cells and record
state_cells = runf.create_neurons()
record = runf.setup_recording(state_cells)

# build FSA and run
runf.three_state_fsa(first_spike_gen, secnd_spike_gen, state_cells)
runf.run_fsa(run_duration)

# print results
runf.print_results(state_cells)

