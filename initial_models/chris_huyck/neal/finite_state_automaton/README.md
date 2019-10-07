# Neuromorphic Embodied Agents that Learn (NEAL)

## Finite-State Automaton (FSA)
[Finite-state machine or finite-state automaton](https://en.wikipedia.org/wiki/Finite-state_machine) is an abstract machine such that at any given time it can be in one of the finite number of states. In response to an external input it can transition from one state to another.

[Singh et al.](http://www.cwa.mdx.ac.uk/NEAL/code/simpleNeuralRobot.pdf) developed an FSA to control the robotic arm and grip. The FSA is based on cell assemblies of spiking neurons.

The codes here are basically the same as the [original codes](http://www.cwa.mdx.ac.uk/NEAL/code/FSA/FSA.html). The original was coded to run on both NEST and SpiNNaker. However, the code here runs only on SpiNNaker.

### The overall algorithm
![whole algorithm](./images/neal_overall.png)

#### The algorithm to turn on the state
![turn on function algorithm](./images/turn_on_function.png)

#### A generic algorithm to either; make a cell assembly, turn half the cell assemblies on or turn off all the cell assemblies
![rest functions algorithm](./images/rest_functions.png)