# ~/nmcog/spinnaker/specialfunction/neal/stateMachineClass.py
#
# Documentation by Lungsi 25 March 2020
#
#This is the class for construcing State Machines.  The individual CAs 
#(both inputs and states) run at 5 ms.  See the notes for running faster or 
#slower. 
#There are test functions at the end. 
#Note that to externally activate a CA State, you should only send
#excitatory connections to the first 8 neurons.
#Using the nealNRPCover so no nealParams
#
import numpy as np
import pickle

from .nealCoverClass import NealCoverFunctions

# added for nmcog
import spynnaker8 as sim

class FSAHelperFunctions:
    """This is the class for constructing State Machines.  The individual CAs  (both inputs and states) run at 5 ms. 
    
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | Methods                                     |  Parameters Used                                                                                   |
    +=============================================+====================================================================================================+
    | :py:meth:`.turnOnStateFromSpikeSource`      | - ``CA_SIZE``, ``CA_INHIBS``, ``INPUT_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``               |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.halfTurnOnStateFromSpikeSource`  | - ``CA_SIZE``, ``CA_INHIBS``, ``HALF_INPUT_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``          |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.turnOffStateFromSpikeSource`     | - ``CA_SIZE``, ``CA_INHIBS``, ``ONE_NEURON_STOPS_CA_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY`` |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stimulateStateFromSpikeSource`   | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.inhibitStateFromSpikeSource`     | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.turnOnOneNeuronFromSpikeSource`  | - ``INPUT_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``                                           |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.turnOffOneNeuronFromSpikeSource` | - ``CA_STOPS_CA_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``                                     |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.inhibitOneNeuronFromSpikeSource` | - :ref:`NealCoverFunctions` ``.DELAY``                                                             |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronTurnsOnState`           | - ``CA_SIZE``, ``CA_INHIBS``, ``INPUT_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``               |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronHalfTurnsOnState`       | - ``CA_SIZE``, ``CA_INHIBS``, ``ONE_HALF_ON_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``         |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronTurnsOffState`          | - ``CA_SIZE``, ``CA_INHIBS``, ``ONE_NEURON_STOPS_CA_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY`` |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronHalfTurnsOffState`      | - ``CA_SIZE``, ``CA_INHIBS``, ``ONE_HALF_ON_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``         |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronStimulatesState`        | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronStimulatesOneNeuron`    | - :ref:`NealCoverFunctions` ``.DELAY``                                                             |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronTurnsOnOneNeuron`       | - ``INPUT_WEIGHT``                                                                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronInhibitsOneNeuron`      | - :ref:`NealCoverFunctions` ``.DELAY``                                                             |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronHalfTurnsOnOneNeuron`   | - ``ONE_HALF_ON_ONE_WEIGHT``                                                                       |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.oneNeuronInhibitsState`          | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateTurnsOnOneNeuron`           | - ``CA_SIZE``, ``CA_INHIBS``, ``STATE_TO_ONE_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``        |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateTurnsOnOneRBSNeuron`        | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateHalfTurnsOnOneNueron`       | - ``CA_SIZE``, ``CA_INHIBS``, ``HALF_ON_ONE_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``         |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateStimulatesOneNeuron`        | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateInhibitsOneNeuron`          | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateTurnsOnState`               | - ``CA_SIZE``, ``CA_INHIBS``, ``FULL_ON_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``             |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateTurnsOnStateSlow`           | - ``CA_SIZE``, ``CA_INHIBS``, ``FULL_ON_WEIGHT_SLOW``, :ref:`NealCoverFunctions` ``.DELAY``        |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateTurnsOffState`              | - ``CA_SIZE``, ``CA_INHIBS``, ``CA_STOPS_CA_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``         |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateHalfTurnsOnState`           | - ``CA_SIZE``, ``CA_INHIBS``, ``HALF_ON_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``             |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateHalfTurnsOffState`          | - ``CA_SIZE``, ``CA_INHIBS``, ``HALF_ON_WEIGHT``, :ref:`NealCoverFunctions` ``.DELAY``             |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateStimulatesState`            | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.stateInhibitsState`              | - ``CA_SIZE``, :ref:`NealCoverFunctions` ``.DELAY``                                                |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    | :py:meth:`.getCAConnectors`                 | - ``CA_SIZE``, ``CA_INHIBS``, :ref:`NealCoverFunctions` ``.DELAY``                                 |
    |                                             | - ``INTRA_CA_WEIGHT``, ``INTRA_CA_TO_INHIB_WEIGHT``, ``INTRA_CA_FROM_INHIB_WEIGHT``                |
    +---------------------------------------------+----------------------------------------------------------------------------------------------------+
    
    
    """
    
    #def __init__(self, simName, sim, neal,spinnVersion = None):
    def __init__(self, simName="spinnaker", spinnVersion = 8): # modified for nmcog
        self.simName = simName
        self.sim = sim
        self.neal = NealCoverFunctions()
        if spinnVersion is None:
            self.spinnVersion = -1
        else:
            self.spinnVersion = spinnVersion
        self.initParams()
        

    #FSA Parmaeters
    def initParams(self):
        """
    
        +--------------------------------+------------+--------------------------------------------------------------------+
        | Constants                      | values     | comments                                                           |
        +================================+============+====================================================================+
        | ``CA_SIZE``                    | 10         | - This will (almost certainly) not work with a different sized CA. |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``CA_INHIBS``                  | 2          | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``INPUT_WEIGHT``               | 0.12       | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``HALF_INPUT_WEIGHT``          | 0.008      | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``INTRA_CA_TO_INHIB_WEIGHT``   | 0.002      | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``INTRA_CA_FROM_INHIB_WEIGHT`` | 0.15       | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``CA_STOPS_CA_WEIGHT``         | 0.15       | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``ONE_NEURON_STOPS_CA_WEIGHT`` | 1.0        | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``ONE_NEURON_HALF_CA_WEIGHT``  | 0.02       | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``INTRA_CA_WEIGHT``            | 0.025      | - for `sPyNNaker <https://spinnakermanchester.github.io/>`_        |
        |                                | 0.022      | - for `NEST <https://www.nest-simulator.org/>`_                    |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``FULL_ON_WEIGHT``             | 0.01       | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``FULL_ON_WEIGHT_SLOW``        | 0.0022     | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``HALF_ON_WEIGHT``             | 0.0012     | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``HALF_ON_ONE_WEIGHT``         | 0.002      | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``STATE_TO_ONE_WEIGHT``        | 0.01       | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``ONE_HALF_ON_WEIGHT``         | 0.016      | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``ONE_HALF_ON_ONE_WEIGHT``     | 0.08       | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        | ``CELL_PARAMS``                | dictionary | -                                                                  |
        |                                |            |                                                                    |
        | 'v_thresh'                     | -48.0      | -                                                                  |
        |                                |            |                                                                    |
        | 'v_reset'                      | -70.0      | -                                                                  |
        |                                |            |                                                                    |
        | 'tau_refrac'                   | 2.0        | -                                                                  |
        |                                |            |                                                                    |
        | 'tau_syn_E'                    | 5.0        | -                                                                  |
        |                                |            |                                                                    |
        | 'tau_syn_I'                    | 5.0        | -                                                                  |
        |                                |            |                                                                    |
        | 'v_rest'                       | -65.0      | -                                                                  |
        |                                |            |                                                                    |
        | 'i_offset'                     | 0.0        | -                                                                  |
        +--------------------------------+------------+--------------------------------------------------------------------+
        
        """
        self.CA_SIZE = 10  #This will (almost certainly) not work with a 
                     #different sized CA.
        self.CA_INHIBS = 2

        #normal weights
        self.INPUT_WEIGHT = 0.12
        self.HALF_INPUT_WEIGHT = 0.08
        self.INTRA_CA_TO_INHIB_WEIGHT = 0.002
        #if you over inhib on my spinnaker, it fires.
        self.INTRA_CA_FROM_INHIB_WEIGHT = 0.15 
        self.CA_STOPS_CA_WEIGHT = 0.15
        self.ONE_NEURON_STOPS_CA_WEIGHT = 1.0 

        self.ONE_NEURON_HALF_CA_WEIGHT = 0.02

        if (self.simName =="spinnaker"):
            self.INTRA_CA_WEIGHT = 0.025
        elif (self.simName == "nest"):
            self.INTRA_CA_WEIGHT = 0.022 
        else:
            self.INTRA_CA_WEIGHT = 0.022 

        self.FULL_ON_WEIGHT = 0.01 
        self.FULL_ON_WEIGHT_SLOW = 0.0022
        self.HALF_ON_WEIGHT = 0.0012
        self.HALF_ON_ONE_WEIGHT = 0.002
        #undone rbs self.STATE_TO_ONE_WEIGHT = .015
        self.STATE_TO_ONE_WEIGHT = .01

        self.ONE_HALF_ON_WEIGHT = 0.016
        self.ONE_HALF_ON_ONE_WEIGHT = 0.08
        #self.ONE_NEURON_STARTS_CA_WEIGHT = self.INPUT_WEIGHT


        self.CELL_PARAMS = {'v_thresh':-48.0, 'v_reset' : -70.0, 
                                'tau_refrac': 2.0 , 'tau_syn_E': 5.0,  
                                'tau_syn_I' : 5.0, 
                                'v_rest' : -65.0,'i_offset':0.0}

    #--------Finite State Automata Functions ------------
    #states can be turned and off by a spikeSource, and can be stimulate or
                   #inhibited by one.
    #states can be turned on and off by a neuron, and can stimulate or inhibit
                    #one
    #states can stimulate or inhibit neurons

    #states can be turned on and off by a state, and can stimulate or inhibit
                    #them.  States can also slow turn on other states, and
                    #half turn them on


    #---Functions that turn on states by one item
    #-- Function to ignite a state from a spike source
    #-- Uses INPUT_WEIGHT
    #use this when your using a spikesource
    def turnOnStateFromSpikeSource(self,spikeSource, toNeurons, toCA):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method turns **ON** the state of the desired cell assembly.
        ``toNeurons`` specifies the type of `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within the cell assembly.
        
        +-----------------+-------------+---------------+------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``INPUT_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+------------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(0,toNeuron,self.INPUT_WEIGHT,
                                      self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'excitatory')

    def halfTurnOnStateFromSpikeSource(self,spikeSource, toNeurons, toCA):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method turns **1/2 ON** the state of the desired cell assembly.
        ``toNeurons`` specifies the type of `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within the cell assembly.
        
        +-----------------+-------------+---------------+-----------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``HALF_INPUT_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+-----------------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(0,toNeuron,self.HALF_INPUT_WEIGHT,
                                      self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'excitatory')

    def turnOffStateFromSpikeSource(self,spikeSource, toNeurons, toCA):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method turns **OFF** the state of the desired cell assembly.
        ``toNeurons`` specifies the type of `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within the cell assembly.
        
        +-----------------+-------------+---------------+--------------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``ONE_NEURON_STOPS_CA_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(0,toNeuron,
                        self.ONE_NEURON_STOPS_CA_WEIGHT,self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'inhibitory')

    def stimulateStateFromSpikeSource(self,spikeSource, toNeurons, toCA, weight):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method stimulates the state of the desired cell assembly with the given weight value.
        ``toNeurons`` specifies the type of `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within the cell assembly.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(0,toNeuron,weight,
                                      self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'excitatory')

    def inhibitStateFromSpikeSource(self,spikeSource, toNeurons, toCA, weight):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method inhibits the state of the desired cell assembly.
        ``toNeurons`` specifies the type of `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within the cell assembly.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(0,toNeuron,weight,
                                      self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'inhibitory')

    def turnOnOneNeuronFromSpikeSource(self,spikeSource, toNeurons, toNeuron):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method turns **ON** the state of a desired `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        within a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_.
        
        +-----------------+------------------+--------------------------------------+
        | Parameters used | ``INPUT_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+------------------+--------------------------------------+
        
        """
        connector = []
        connector = connector + [(0,toNeuron,self.INPUT_WEIGHT,self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'excitatory')

    #undone needs a test
    def turnOffOneNeuronFromSpikeSource(self,spikeSource, toNeurons, toNeuron):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method turns **OFF** the state of a desired `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        within a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_.
        
        +-----------------+------------------------+--------------------------------------+
        | Parameters used | ``CA_STOPS_CA_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+------------------------+--------------------------------------+
        
        """
        connector = []
        connector = connector + [(0,toNeuron,self.CA_STOPS_CA_WEIGHT,self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'inhibitory')

    #undone
    def inhibitOneNeuronFromSpikeSource(self,spikeSource, toNeurons, toNeuron,
                                        weight):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method inhibits the state of a desired `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        within a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ with the given weight value.
        
        +-----------------+--------------------------------------+
        | Parameters used | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+--------------------------------------+
        
        """
        connector = []
        connector = connector + [(0,toNeuron,weight,self.neal.DELAY)]
        self.neal.nealProjection(spikeSource, toNeurons, connector,'inhibitory')

    #---states can be turned on and off by a neuron, can stimulate or 
    #inhibit one, and can half turn on one.
    def oneNeuronTurnsOnState(self,fromNeurons,fromNeuron, toNeurons, toCA):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method turns **ON** the state
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly.
        
        +-----------------+-------------+---------------+------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``INPUT_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+------------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(fromNeuron,toNeuron,self.INPUT_WEIGHT,
                                      self.neal.DELAY)]
        self.neal.nealProjection(fromNeurons, toNeurons, connector,'excitatory')

    def oneNeuronHalfTurnsOnState(self,fromNeurons,fromNeuron, toNeurons, toCA):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method turns **1/2 ON** the state
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly.
        
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``ONE_HALF_ON_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(fromNeuron,toNeuron,self.ONE_HALF_ON_WEIGHT,
                                      self.neal.DELAY)]
        self.neal.nealProjection(fromNeurons, toNeurons, connector,'excitatory')

    def oneNeuronTurnsOffState(self,fromNeurons, fromNeuron, toNeurons, toCA):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method turns **OFF** the state
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly.
        
        +-----------------+-------------+---------------+--------------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``ONE_NEURON_STOPS_CA_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(fromNeuron,toNeuron,
                                      self.ONE_NEURON_STOPS_CA_WEIGHT,
                                      self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'inhibitory')

    def oneNeuronHalfTurnsOffState(self,fromNeurons,fromNeuron, toNeurons, toCA):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method turns **1/2 OFF** the state
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly.
        
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``ONE_HALF_ON_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(fromNeuron,toNeuron,self.ONE_HALF_ON_WEIGHT,
                                      self.neal.DELAY)]
        self.neal.nealProjection(fromNeurons, toNeurons, connector,'inhibitory')

    def oneNeuronStimulatesState(self,fromNeurons,fromNeuron, toNeurons, toCA, 
                                weight):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method stimulates the state
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly
        with the given weight value.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(fromNeuron,toNeuron,weight,
                                      self.neal.DELAY)]
        self.neal.nealProjection(fromNeurons, toNeurons, connector,'excitatory')


    #the rbs has these, but they're not accurate weights for what they
    #say they do.  So, leave them out for now.
    #def oneNeuronHalfTurnsOnState(self,fromNeurons,fromNeuron,toNeurons,toCA):
    #def oneNeuronHalfTurnsOnOneNeuron(self,fromNeurons,fromCA,toNeurons,toCA):
    #def stateHalfTurnsOnOneNeuron(self,fromNeurons,fromCA,toNeurons,toNeuron):

    #Neurons can also directly interact with each other.
    def oneNeuronStimulatesOneNeuron(self,fromNeurons,fromNeuron, toNeurons, 
                                     toNeuron,weight):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method stimulates the state
        of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_ of a
        desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ with the given weight value.
        
        +-----------------+--------------------------------------+
        | Parameters used | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+--------------------------------------+
        
        """
        connector = []
        connector = connector + [(fromNeuron,toNeuron,weight,self.neal.DELAY)]
        self.neal.nealProjection(fromNeurons, toNeurons, connector,'excitatory')

    def oneNeuronTurnsOnOneNeuron(self,fromNeurons,fromCA,toNeurons,toCA):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method turns **ON** the state
        of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_ of a
        `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a desired cell assembly.
        
        +-----------------+------------------+
        | Parameters used | ``INPUT_WEIGHT`` |
        +-----------------+------------------+
        
        """
        self.oneNeuronStimulatesOneNeuron(fromNeurons,fromCA,toNeurons,toCA, 
                                       self.INPUT_WEIGHT)

    def oneNeuronInhibitsOneNeuron(self,fromNeurons,fromNeuron, 
                                   toNeurons,toNeuron, weight):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method inhibits the state
        of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_ of a
        desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ with the given weight value.
        
        +-----------------+--------------------------------------+
        | Parameters used | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+--------------------------------------+
        
        """
        connector = []
        connector = connector + [(fromNeuron,toNeuron,weight,
                                      self.neal.DELAY)]
        self.neal.nealProjection(fromNeurons, toNeurons, connector,'inhibitory')

    def oneNeuronHalfTurnsOnOneNeuron(self,fromNeurons,fromCA,toNeurons,toCA):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method turns **1/2 ON** the state
        of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_ of a
        `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a desired cell assembly.
        
        +-----------------+----------------------------+
        | Parameters used | ``ONE_HALF_ON_ONE_WEIGHT`` |
        +-----------------+----------------------------+
        
        """
        self.oneNeuronStimulatesOneNeuron(fromNeurons,fromCA,toNeurons,toCA, 
                                       self.ONE_HALF_ON_ONE_WEIGHT)

    def oneNeuronInhibitsState(self,fromNeurons,fromNeuron, toNeurons, toCA, 
                               weight):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, this method inhibits the state
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a desired cell assembly
        with the given weight value.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        """
        connector = []
        for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            toNeuron = toOffset + (toCA*self.CA_SIZE)
            connector = connector + [(fromNeuron,toNeuron,weight,
                                      self.neal.DELAY)]
        self.neal.nealProjection(fromNeurons, toNeurons, connector,'inhibitory')


    #states can stimulate or inhibit neurons
    def stateTurnsOnOneNeuron(self,fromNeurons,fromCA,toNeurons,toNeuron):
        """From a given a `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method turns **ON** the state of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_.
        
        +-----------------+-------------+---------------+-------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``STATE_TO_ONE_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+-------------------------+--------------------------------------+
        
        Connection between the cell assemblies is as shown
        
        ::
        
                    fromCA
            ooooooooooooooooooooooo
            o                     o
            o                     o                         toNeuron
            o (0) (2) (4) (6) (8) o                          ( x )
            o      +              o  STATE_TO_ONE_WEIGHT       ^
            o      +++++++++++++++o+++++++++++++++++++++++++++++
            o                     o
            o (1) (3) (5) (7) (9) o
            o                     o
            o                     o
            ooooooooooooooooooooooo
        
        
        **Note:**
        
        * A cell assembly is composed of CA_SIZE number of `neuron units <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_ such that each unit is of same kind.
        * Therefore, the arguments ``fromNeurons`` and ``toNeurons`` (plural) refers to the kind of neuron population in the from- and to-assemblies.
        * That is, ``fromNeurons`` and ``toNeurons`` do not indicate some specific neuron population within respective assemblies.
        * The specificiation of a unit (from and to) a cell assembly is done by the connector list of tuples.
        * This specification is such that the ``fromNeuron`` and ``toNeuron`` are only in reference to units with excitatory connections.
        
            - Referring to illustration in :py:meth:`.getCAConnectors` then in the above illustration ``fromNeuron`` and ``toNeuron`` (singular) will be <<0>> to <<7>>
            - <<8>> and <<9>> are not the source for the connection.
            - In theory ``toNeuron`` can be in the same cell assembly as those of ``fromNeuron``.
        
        """
        connector = []
        #uses STATE_TO_ONE_WEIGHT
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            connector=connector+[(fromNeuron,toNeuron,
                                  self.STATE_TO_ONE_WEIGHT,
                                  self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')

    #states can stimulate or inhibit neurons
    def stateTurnsOnOneRBSNeuron(self,fromNeurons,fromCA,toNeurons,toNeuron):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method turns **ON** the state of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ with the given weight value 0.015.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateTurnsOnOneNeuron`.
        
        """
        connector = []
        #uses STATE_TO_ONE_WEIGHT
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            connector=connector+[(fromNeuron,toNeuron,
                                  0.015,
                                  self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')

    def stateHalfTurnsOnOneNueron(self,fromNeurons,fromCA,toNeurons,toNeuron):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method turns **1/2 ON** the state of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_.
        
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``HALF_ON_ONE_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateTurnsOnOneNeuron`.
        
        """
        connector = []
        #uses STATE_TO_ONE_WEIGHT
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            connector=connector+[(fromNeuron,toNeuron,
                                  self.HALF_ON_ONE_WEIGHT,
                                  self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')

    def stateStimulatesOneNeuron(self,fromNeurons,fromCA,toNeurons,toNeuron,
                                 weight):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method stimulates the state of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ with the given weight value.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateTurnsOnOneNeuron`.
        
        """
        connector = []
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            connector=connector+[(fromNeuron,toNeuron,weight,
                                  self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')


    def stateInhibitsOneNeuron(self,fromNeurons,fromCA,toNeurons,toNeuron, 
                              weight):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method inhibits the state of another `neuron unit <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ with the given weight value.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateTurnsOnOneNeuron` with the exception that this is "inhibitory".
        
        """
        connector = []
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            connector=connector+[(fromNeuron,toNeuron,weight,
                                  self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'inhibitory')


    #states can be turned on and off by a state, and can stimulate or inhibit
                    #them.  States can also slow turn on other states, and
                    #half turn them on

    #Function to turn on one state from another
    #Call with fromPopulation, fromCA, toPopulation and toCA
    def stateTurnsOnState(self,fromNeurons,fromCA,toNeurons,toCA):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method turns **ON** the state of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within a desired cell assembly.
        
        +-----------------+-------------+---------------+--------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``FULL_ON_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateHalfTurnsOnState`.
        
        """
        connector = []
        #uses FULL_ON_WEIGHT
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
                toNeuron = toOffset + (toCA*self.CA_SIZE)
                connector=connector+[(fromNeuron,toNeuron,
                                          self.FULL_ON_WEIGHT,
                                          self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')

    #When stateTurnsOnState and the preState remains on, the post
    #state runs hot.
    def stateTurnsOnStateSlow(self,fromNeurons,fromCA,toNeurons,toCA):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method slowly turns **ON** the state of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within a desired cell assembly.
        
        +-----------------+-------------+---------------+-------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``FULL_ON_WEIGHT_SLOW`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+-------------------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateHalfTurnsOnState`.
        
        """
        connector = []
        #uses FULL_ON_WEIGHT_SLOW
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
                toNeuron = toOffset + (toCA*self.CA_SIZE)
                connector=connector+[(fromNeuron,toNeuron,
                                          self.FULL_ON_WEIGHT_SLOW,
                                          self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')


    #---- One State or other set of neurons turns off another
    #-- Uses CA_STOPS_CA_WEIGHT
    def stateTurnsOffState(self,fromNeurons, fromCA, toNeurons, toCA):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method turns **OFF** the state of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within a desired cell assembly.
        
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``CA_STOPS_CA_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+------------------------+--------------------------------------+
        
        Connection between the cell assemblies is as shown
        
        ::
        
                    fromCA                                        toCA
            ooooooooooooooooooooooo                      ooooooooooooooooooooooo
            o                     o                      o                     o
            o                     o                      o                     o
            o (0) (2) (4) (6) (8) o                      o (0) (2) (4) (6) (8) o
            o      -              o  CA_STOPS_CA_WEIGHT  o  ^   ^   ^   ^   ^  o
            o      ---------------o----------------------o-------------------  o
            o                     o                      o  v   v   v   v   v  o
            o (1) (3) (5) (7) (9) o                      o (1) (3) (5) (7) (9) o
            o                     o                      o                     o
            o                     o                      o                     o
            ooooooooooooooooooooooo                      ooooooooooooooooooooooo
        
        
        **Note:**
        
        * A cell assembly is composed of CA_SIZE number of `neuron units <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_ such that each unit is of same kind.
        * Therefore, the arguments ``fromNeurons`` and ``toNeurons`` (plural) refers to the kind of neuron population in the from- and to-assemblies.
        * That is, ``fromNeurons`` and ``toNeurons`` do not indicate some specific neuron population within respective assemblies.
        * The specificiation of a unit (from and to) a cell assembly is done by the connector list of tuples.
        * This specification is such that the ``fromNeuron`` and ``toNeuron`` are from every unit within a cell assembly.
        
            - Thus, unlike the illustration in :py:meth:`.stateHalfTurnsOnState` in the above illustration ``fromNeuron`` and ``toNeuron`` (singular) will be <<0>> to <<9>>
            - See the illustration in :py:meth:`.getCAConnectors` for referring to <<0>> to <<9>> 
        
        
        """
        connector = []
        for fromOffset in range (0,self.CA_SIZE):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE):
                toNeuron = toOffset + (toCA*self.CA_SIZE)
                connector = connector + [(fromNeuron,toNeuron,
                                              self.CA_STOPS_CA_WEIGHT,
                                              self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'inhibitory')

    #--Functions when two inputs are needed to turn on a third
    #-- Two states are needed to turn on a third.  
    #-- This connects one of the inputs to the the third.
    #-- Uses HALFs_ON_WEIGHT
    def stateHalfTurnsOnState(self,fromNeurons,fromCA,toNeurons,toCA):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method turns **1/2 ON** the state of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within a desired cell assembly.
        
        +-----------------+-------------+---------------+--------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``HALF_ON_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------+--------------------------------------+
        
        Connection between the cell assemblies is as shown
        
        ::
        
                    fromCA                                    toCA
            ooooooooooooooooooooooo                  ooooooooooooooooooooooo
            o                     o                  o                     o
            o                     o                  o                     o
            o (0) (2) (4) (6) (8) o                  o (0) (2) (4) (6) (8) o
            o      +              o  HALF_ON_WEIGHT  o  ^   ^   ^   ^      o
            o      +++++++++++++++o++++++++++++++++++o+++++++++++++++      o
            o                     o                  o  v   v   v   v      o
            o (1) (3) (5) (7) (9) o                  o (1) (3) (5) (7) (9) o
            o                     o                  o                     o
            o                     o                  o                     o
            ooooooooooooooooooooooo                  ooooooooooooooooooooooo
        
        
        **Note:**
        
        * A cell assembly is composed of CA_SIZE number of `neuron units <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_ such that each unit is of same kind.
        * Therefore, the arguments ``fromNeurons`` and ``toNeurons`` (plural) refers to the kind of neuron population in the from- and to-assemblies.
        * That is, ``fromNeurons`` and ``toNeurons`` do not indicate some specific neuron population within respective assemblies.
        * The specification of a unit (from and to) a cell assembly is done by the connector list of tuples.
        * This specification is such that the ``fromNeuron`` and ``toNeuron`` are only in reference to units with excitatory connections.
        
            - Referring to illustration in :py:meth:`.getCAConnectors` then in the above illustration ``fromNeuron`` and ``toNeuron`` (singular) will be <<0>> to <<7>>
            - <<8>> and <<9>> are neither the source nor the target for the connection.
        
        """
        connector = []
        #uses HALF_ON_WEIGHT
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
                toNeuron = toOffset + (toCA*self.CA_SIZE)
                connector=connector+[(fromNeuron,toNeuron,
                                          self.HALF_ON_WEIGHT,
                                          self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')

    def stateHalfTurnsOffState(self,fromNeurons,fromCA,toNeurons,toCA):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method turns **1/2 OFF** the state of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within a desired cell assembly.
        
        +-----------------+-------------+---------------+--------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``HALF_ON_WEIGHT`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateHalfTurnsOnState`.
        
        """
        connector = []
        #uses HALF_ON_WEIGHT
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
                toNeuron = toOffset + (toCA*self.CA_SIZE)
                connector=connector+[(fromNeuron,toNeuron,
                                          self.HALF_ON_WEIGHT,
                                          self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'inhibitory')

    def stateStimulatesState(self,fromNeurons,fromCA,toNeurons,toCA,weight):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method stimulates the state of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within a desired cell assembly with the given weight value.
        
        +-----------------+-------------+---------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+---------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateHalfTurnsOnState`.
        
        """
        connector = []
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
                toNeuron = toOffset + (toCA*self.CA_SIZE)
                connector=connector+[(fromNeuron,toNeuron,
                    weight, self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'excitatory')

    def stateInhibitsState(self,fromNeurons, fromCA, toNeurons, toCA, wt):
        """From a given `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ in a cell assembly,
        this method inhibits the state of a desired `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        within a desired cell assembly with the given weight value.
        
        +-----------------+-------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | :ref:`NealCoverFunctions` ``.DELAY`` |
        +-----------------+-------------+--------------------------------------+
        
        **Note:**
        
        * For illustration on how the connections are made see :py:meth:`.stateTurnsOffState` with the exception that this is "inhibitory".
        
        """
        connector = []
        for fromOffset in range (0,self.CA_SIZE):
            fromNeuron = fromOffset + (fromCA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE):
                toNeuron = toOffset + (toCA*self.CA_SIZE)
                connector = connector + [(fromNeuron,toNeuron,
                                              wt,self.neal.DELAY)]

        self.neal.nealProjection(fromNeurons,toNeurons,connector,'inhibitory')



    #---Create a CA that will persistently fire.
    #-- Assumes neurons in the same population
    #-- Uses INTRA_CA_WEIGHT
    def getCAConnectors(self, CA):
        """Create excitatory connector list and inhibitory connector list for a given cell assembly.
        The method returns a list such that the first element is the excitatory connector list.
        
        Regardless of excitatory or inhibitory connector lists, the most basic element of a connector list is a
        `PyNN Connector <http://neuralensemble.org/docs/PyNN/reference/connectors.html#pyNN.connectors.FromListConnector>`_ tuple
        of the form *(pre_idx, post_idx, weight, delay)* where *pre_idx* is the index
        (i.e. order in the `Population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_, not the ID) of the presynaptic neuron,
        *post_idx* is the index of the postsynaptic neuron, and *weight*, *delay* are the synaptic parameters.
        
        +-----------------+-------------+---------------+--------------------------------+--------------------------------------+
        | Parameters used | ``CA_SIZE`` | ``CA_INHIBS`` | ``INTRA_CA_WEIGHT``            | :ref:`NealCoverFunctions` ``.DELAY`` |
        |                 |             |               | ``INTRA_CA_TO_INHIB_WEIGHT``   |                                      |
        |                 |             |               | ``INTRA_CA_FROM_INHIB_WEIGHT`` |                                      |
        +-----------------+-------------+---------------+--------------------------------+--------------------------------------+
        
        By default a cell assembly size ``CA_SIZE`` = 10, which is the number of `neuron units <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_ in each assembly.
        
        These ten neuron populations are such that
        
        * eight of them project excitatory connections, lets call them <<0>> to <<7>>
        * two of them project inhibitory connections, lets call them <<8>> and <<9>>
        
        Three kinds of connections are made,
        
        1. Excitatory connection from one neuron unit to another unit that projects excitatory connection (but not itself). Below shows projections from <<0>>.
        
        ::
        
            Connection Weight is INTRA_CA_WEIGHT.
            
             .-.      .-.      .-.      .-.      .-.
            ( 0 )    ( 2 )    ( 4 )    ( 6 )    ( 8 )
             '-'      '-'      '-'      '-'      '-'
              +        ^        ^        ^
              + ++++++++++++++++++++++++++
              v        v        v        v
             .-.      .-.      .-.      .-.      .-.
            ( 1 )    ( 3 )    ( 5 )    ( 7 )    ( 9 )
             '-'      '-'      '-'      '-'      '-'
        
        2. Excitatory connection from neuron unit to another that project inhibitory connection. Below shows projections from <<0>>.
        
        ::
        
            Connection Weight is INTRA_CA_TO_INHIB_WEIGHT.
            
             .-.      .-.      .-.      .-.      .-.
            ( 0 )    ( 2 )    ( 4 )    ( 6 )    ( 8 )
             '-'      '-'      '-'      '-'      '-'
              +                                   ^
              +++++++++++++++++++++++++++++++++++++
                                                  v
             .-.      .-.      .-.      .-.      .-.
            ( 1 )    ( 3 )    ( 5 )    ( 7 )    ( 9 )
             '-'      '-'      '-'      '-'      '-'
        
        3. Inhibitory connection from neuron unit to other unit that project excitatory connection (but not to units that project inhibitory connection including itself). Below shows projections from <<8>>.
        
        ::
        
            Connection Weight is INTRA_CA_FROM_INHIB_WEIGHT.
            
             .-.      .-.      .-.      .-.      .-.
            ( 0 )    ( 2 )    ( 4 )    ( 6 )    ( 8 )
             '-'      '-'      '-'      '-'      '-'
              ^        ^        ^        ^        -
              -------------------------------------
              v        v        v        v
             .-.      .-.      .-.      .-.      .-.
            ( 1 )    ( 3 )    ( 5 )    ( 7 )    ( 9 )
             '-'      '-'      '-'      '-'      '-'
        
        **Note:**
        
        * The two kinds of excitatory connections are collected in one list, the excitatory connector list.
        
        """
        connector = []
        #excitatory turn each other on
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (CA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
                toNeuron = toOffset + (CA*self.CA_SIZE)
                if (toNeuron != fromNeuron):
                    connector = connector + [(fromNeuron,toNeuron,
                        self.INTRA_CA_WEIGHT, self.neal.DELAY)]

        #excitatory turn on inhibitory
        for fromOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
            fromNeuron = fromOffset + (CA*self.CA_SIZE)
            for toOffset in range (self.CA_SIZE-self.CA_INHIBS,self.CA_SIZE):
                toNeuron = toOffset + (CA*self.CA_SIZE)
                connector = connector + [(fromNeuron,toNeuron,
                        self.INTRA_CA_TO_INHIB_WEIGHT, self.neal.DELAY)]


        #inhibitory slows excitatory 
        inhConnector = []
        for fromOffset in range (self.CA_SIZE-self.CA_INHIBS,self.CA_SIZE):
            fromNeuron = fromOffset + (CA*self.CA_SIZE)
            for toOffset in range (0,self.CA_SIZE-self.CA_INHIBS):
                toNeuron = toOffset + (CA*self.CA_SIZE)
                inhConnector = inhConnector + [(fromNeuron,toNeuron,
                        self.INTRA_CA_FROM_INHIB_WEIGHT, self.neal.DELAY)]

        return[connector,inhConnector]

    def makeCA(self,neurons, CA):
        """Given a `neuron population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ and cell assembly parameters
        this method gets excitatory and inhibitory connectors (from :py:meth:`.getCAConnectors`) for the presumptive cell assembly.
        
        * Because the default a cell assembly size ``CA_SIZE`` = 10, there are ten `neuron units <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_
        
        ::
        
            oooooooooooooooooooooooooooooooooooooooooooooooo
            o                                              o
            o   .-.      .-.      .-.      .-.      .-.    o
            o  ( 0 )    ( 2 )    ( 4 )    ( 6 )    ( 8 )   o
            o   '-'      '-'      '-'      '-'      '-'    o
            o                                              o
            o        cell assembly of CA_SIZE = 10         o
            o                                              o
            o   .-.      .-.      .-.      .-.      .-.    o
            o  ( 1 )    ( 3 )    ( 5 )    ( 7 )    ( 9 )   o
            o   '-'      '-'      '-'      '-'      '-'    o
            o                                              o
            oooooooooooooooooooooooooooooooooooooooooooooooo
        
        
        * These neuron units are connected using :py:meth:`.getCAConnectors` put together via :ref:`NealCoverFunctions` ``.nealProjection``
        * The source and target `neuron populations <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ are one and the same.
        
        Therefore, a cell assembly here is
        
        * **one** `PyNN neuron population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ 
        * with ten `neuron units <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_ within the `population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        * and the ten neuron units are connected (see :py:meth:`.getCAConnectors` for how the connections are made).
        
        """
        connectors = self.getCAConnectors(CA)
        self.neal.nealProjection(neurons,neurons,connectors[0],'excitatory')
        self.neal.nealProjection(neurons,neurons,connectors[1],'inhibitory')

    def nopMakeCA(self,neurons, CA):
        """Legacy."""
        connector = []
        fromNeuron = CA
        toNeuron = CA + 1
        connector = connector + [(fromNeuron,toNeuron, 1.2, self.neal.DELAY)]
        self.neal.nealProjection(neurons,neurons,connector,'excitatory')
        
#------test functions
    #initialize the simulator. 
    def testInit(self):
        """Legacy."""
        #print "spin" or nest
        self.sim.setup(timestep=self.neal.DELAY,
                    min_delay=self.neal.DELAY,
                    max_delay=self.neal.DELAY, debug=0)


    def testCreateTwoInputs(self):
        """Legacy."""
        inputSpikeTimes0 = [10.0]
        inputSpikeTimes1 = [50.0]
        spikeArray0 = {'spike_times': [inputSpikeTimes0]}
        spikeGen0=self.sim.Population(1,self.sim.SpikeSourceArray,spikeArray0,
                                   label='inputSpikes_0')
        spikeArray1 = {'spike_times': [inputSpikeTimes1]}
        spikeGen1=self.sim.Population(1, self.sim.SpikeSourceArray, spikeArray1,
                                   label='inputSpikes_1')

        return [spikeGen0,spikeGen1]

    def testCreateNeurons(self):
        """Legacy."""
        if (self.simName == 'nest'):
            numNeurons = self.CA_SIZE * 3
        elif (self.simName == 'spinnaker'):
            numNeurons = 100
        
        cells=self.sim.Population(numNeurons,self.sim.IF_cond_exp,self.CELL_PARAMS)

        return cells

    def testSetupRecording(self,cells):
        """Legacy."""
        if  ((self.neal.simulator == 'nest') or 
             ((self.neal.simulator == 'spinnaker') and (self.neal.spinnVersion == 8))):
            cells.record({'spikes','v'})
        elif ((self.neal.simulator == 'spinnaker') and (self.neal.spinnVersion == 7)):
            cells.record()

    def test3StateFSA(self, firstSpikeGenerator, secondSpikeGenerator,
                      stateCells):
        """Legacy."""
        #Build the FSA
        self.turnOnStateFromSpikeSource(firstSpikeGenerator,stateCells,0)
        self.turnOnStateFromSpikeSource(secondSpikeGenerator,stateCells,1)
        self.makeCA(stateCells,0)
        self.makeCA(stateCells,1)
        self.makeCA(stateCells,2)
        self.stateHalfTurnsOnState(stateCells,0,stateCells,2)
        self.stateTurnsOffState(stateCells,2,stateCells,0)
        #comment below out to check state 0 alone does not turn on state 2
        self.stateHalfTurnsOnState(stateCells,1,stateCells,2)
        self.stateTurnsOffState(stateCells,2,stateCells,1)

    def testRunFSA(self,duration):
        """Legacy."""
        self.sim.run(duration)

    def testPrintPklSpikes(self,fileName):
        """Legacy."""
        fileHandle = open(fileName)
        neoObj = pickle.load(fileHandle)
        segments = neoObj.segments
        segment = segments[0]
        spikeTrains = segment.spiketrains
        neurons = len(spikeTrains)
        for neuronNum in range (0,neurons):
            if (len(spikeTrains[neuronNum])>0):
                spikes = spikeTrains[neuronNum]
                for spike in range (0,len(spikes)):
                    print( neuronNum, spikes[spike] )
        fileHandle.close()
    

    def testPrintResults(self,simCells):
        """Legacy."""
        simCells.write_data('temp.pkl',['spikes'])