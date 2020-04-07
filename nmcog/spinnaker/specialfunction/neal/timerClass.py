# ~/nmcog/spinnaker/specialfunction/neal/timerClass.py
#
# Documentation by Lungsi 6 April 2020
#
# This makes several different types of timers and provides mechanisms
# for the timers to effect other states and be turned on by other 
# states, spike sources and neurons.
#

# added for nmcog
import spynnaker8 as sim
from .nealCoverClass import NealCoverFunctions
from .stateMachineClass import FSAHelperFunctions

#---- Code
class TimerClass:
    """This is the class for constructing different types of timers. It also provide functions for the timers
    
    * to effect other states
    * to be turned on by other states, spike sources and neurons.
    
    """
    forwardWeight = 0.004
    oneNeuronFullWeight = 0.08
    oneNeuronHalfWeight = 0.05#0.1#0.04

    #def __init__(self, simName,sim,neal,spinnVersion,fsa,numberStates):
    def __init__(self, simName="spinnaker", spinnVersion=8):
        self.simName = simName
        self.sim = sim
        self.neal = NealCoverFunctions()
        self.spinnVersion = spinnVersion
        self.fsa = FSAHelperFunctions()
        #self.numberStates = numberStates # commented out for nmcog
        #self.timerCells = self.createNeurons(numberStates) # commented out for nmcog

    #create the neurons for the words and the states.
    def createNeurons(self,numberStates):
        """For a given number of states (under consideration) the number of timer cells equals
        the number of states times the size of the cell assembly (given by :ref:`FSAHelperFunctions` ``.CA_SIZE``).
        
        By default :ref:`FSAHelperFunctions` ``.CA_SIZE`` = 10. Therefore, if the number of possible states is two
        then there will be twenty timer cells.
        
        **Note:**
        
        * A timer cell is `PyNN's IF_cond_exp <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_
        * The timer cells are collectively the `PyNN's population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        
        """
        # added for nmcog
        self.numberStates = numberStates # self.timerCells are no longer made at instantiation
        #
        numberTimerCells = numberStates * self.fsa.CA_SIZE
        self.timerCells = self.sim.Population(numberTimerCells,self.sim.IF_cond_exp,
                                              self.fsa.CELL_PARAMS)
        self.setupRecording()
        
        return self.timerCells

    #-----start timer functions
    def connectSpikeGenToStart(self,spikeGen):
        """See :ref:`FSAHelperFunctions` ``.turnOnStateFromSpikeSource``"""
        self.fsa.turnOnStateFromSpikeSource(spikeGen,self.timerCells,0) # timercells are components of first (i.e. 0) cell assembly

    def stateStartsTimer(self,stateNeurons,state):
        """See :ref:`FSAHelperFunctions` ``.stateTurnsOnState``"""
        self.fsa.stateTurnsOnState(stateNeurons,state,self.timerCells,0) # timercells are components of first (i.e. 0) cell assembly

    #undone not in test
    def oneNeuronStartsTimer(self,fromNeurons,fromNeuron):
        """See :ref:`FSAHelperFunctions` ``.oneNeuronStimulatesState``
        This differs from :py:meth:`.oneNeuronHalfStartsTimer` because here ``self.oneNeuronFullWeight`` is used.
        """
        self.fsa.oneNeuronStimulatesState(fromNeurons,fromNeuron,
            self.timerCells,0,self.oneNeuronFullWeight)

    def oneNeuronHalfStartsTimer(self,fromNeurons,fromNeuron):
        """See :ref:`FSAHelperFunctions` ``.oneNeuronStimulatesState``
        This differs from :py:meth:`.oneNeuronStartsTimer` because here ``self.oneNeuronHalfWeight`` is used.
        """
        self.fsa.oneNeuronStimulatesState(fromNeurons,fromNeuron,
            self.timerCells,0,self.oneNeuronHalfWeight)

    def stateHalfStartsTimer(self,stateNeurons,state):
        """See :ref:`FSAHelperFunctions` ``.stateHalfTurnsOnState``"""
        self.fsa.stateHalfTurnsOnState(stateNeurons,state,self.timerCells,0) # timercells are components of first (i.e. 0) cell assembly

    #----stop functions
    #undone needs a test and move to timer
    def neuronStopsTimer(self,stopNeurons,stopNeuron):
        """See :ref:`FSAHelperFunctions` ``.oneNeuronTurnsOffState``"""
        for timerCA in range (0,self.numberStates):
            self.fsa.oneNeuronTurnsOffState(stopNeurons,stopNeuron,
                                        self.timerCells,timerCA)

    #undone needs a test
    def stateStopsTimer(self,stateNeurons,state):
        """See :ref:`FSAHelperFunctions` ``.stateTurnsOffState``"""
        for timerCA in range (0,self.numberStates):
            self.fsa.stateTurnsOffState(stateNeurons,state,
                                        self.timerCells,timerCA)

    #---timer output functions
    #The last state of a timer starts a state
    def timerStartsState(self,stateNeurons,state):
        """See :ref:`FSAHelperFunctions` ``.stateStimulatesState``"""
        #stateTurnsOnState can take a couple of steps.
        #self.fsa.stateTurnsOnState(self.timerCells,self.numberStates-1,
        #                           stateNeurons,state)
        self.fsa.stateStimulatesState(self.timerCells,self.numberStates-1,
                                      stateNeurons,state,0.02)

    def timerPreventsState(self,stateNeurons,state):
        """See :ref:`FSAHelperFunctions` ``.stateTurnsOffState``"""
        for CA in range (0,self.numberStates-1):
            self.fsa.stateTurnsOffState(self.timerCells,CA,
                                   stateNeurons,state)

    #undone needs a test
    def timerActivatesState(self,stateNeurons,state,wt):
        """See :ref:`FSAHelperFunctions` ``.stateStimulatesState``"""
        for CA in range (0,self.numberStates-1):
            self.fsa.stateStimulatesState(self.timerCells,CA,stateNeurons,
                                          state,wt)


    #---create timer functions
    #The timer goes from state to state and the last stops on its own
    def makeStopTimerSynapses(self):
        """See :ref:`FSAHelperFunctions` ``.stateStimulatesState`` and :ref:`FSAHelperFunctions` ``.stateTurnsOffState``"""
        for CA in range (0,self.numberStates-1):
            self.fsa.makeCA(self.timerCells,CA)
            self.fsa.stateStimulatesState(self.timerCells,CA,self.timerCells,
                                             CA+1,self.forwardWeight)
            self.fsa.stateTurnsOffState(self.timerCells,CA+1,self.timerCells,CA)
            
    #The timer goes from state to state and the last stops on its own
    #Only one state is on at at time
    def makeOneStateStopTimerSynapses(self):
        """See :ref:`FSAHelperFunctions` ``.makeCA``, :ref:`FSAHelperFunctions` ``.stateStimulatesState``,
        and :ref:`FSAHelperFunctions` ``.stateTurnsOffState``"""
        for CA in range (0,self.numberStates-1):
            self.fsa.makeCA(self.timerCells,CA)
            self.fsa.stateStimulatesState(self.timerCells,CA,self.timerCells,
                                             CA+1,self.forwardWeight)
            self.fsa.stateTurnsOffState(self.timerCells,CA+1,self.timerCells,CA)
        for toCA in range (0,self.numberStates-1):
            for fromCA in range (toCA+2,self.numberStates):
                self.fsa.stateTurnsOffState(self.timerCells,fromCA,
                                            self.timerCells,toCA)

    #The timer goes from state to state and the last stops on its own
    #If the state that turns it on remains on, this timer will not restart
    #until its done
    def makeStopNoRestartTimerSynapses(self):
        """
        Once a timercell is created using :py:meth:`.createNeurons` returning a `neuron population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        composed of :math:`n \\times 10` cells where *n* is its number of possible states.
        
        This function connects all its possible states.
        
        Consider a timercell, *timerX* with five states then        
        
        ::
    
                    sssssssssssssssssssssssssssss
                    s ccccccccc     s ccccccccc s     ccccccccc       ccccccccc
                    s c xxxxx c     s c xxxxx c s     c xxxxx c       c xxxxx c
                    V V x   V c     V V x   V c s     V x   V c       V x   V c
            ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo
            o timerX CA o   o timerX CA o   o timerX CA o   o timerX CA o   o timerX CA o
            o  state-0  o   o  state-1  o   o  state-2  o   o  state-3  o   o  state-4  o
            ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo
                    ^               ^               ^        s
                    ssssssssssssssssssssssssssssssssssssssssss
        
        
        * all the states are numbers 0, 1, ..., 4 (= 5-1)
        * each state is represented by a cell assembly using :ref:`FSAHelperFunctions` ``.makeCA``
        
            - here four cell assemblies one for each of the five states
            
        * starting from the first state, 0 (above, state-0),
        
            - each state (i.e. its cell assembly) stimulates (xxxxxx) its immediate succeeding state using :ref:`FSAHelperFunctions` ``.stateStimulatesState``
            
                - notice that the first state is not simulated
                
            - each state (i.e. its cell assembly) is turned-off (cccccc) by its immediate succeeding state using :ref:`FSAHelperFunctions` ``.stateTurnsOffState``
            
                - notice that the last state is not turned-off using :ref:`FSAHelperFunctions` ``.stateTurnsOffState``
        
        * starting from the third state, 2 (above, state-2)
        
            - each state turns off (ssssss) all the preceeding states
            
                - notice that the last state does not turn-off its preceeding states.
        
        
        **Note:**
        
        * 10 in :math:`n \\times 10` is the default :ref:`FSAHelperFunctions` ``.CA_SIZE`` = 10
        * The timer cells are collectively the `PyNN's population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
        * A timer cell is `PyNN's IF_cond_exp <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_
        
        """
        for CA in range (0,self.numberStates-1):
            self.fsa.makeCA(self.timerCells,CA)
            self.fsa.stateStimulatesState(self.timerCells,CA,self.timerCells,
                                             CA+1,self.forwardWeight)
            self.fsa.stateTurnsOffState(self.timerCells,CA+1,self.timerCells,CA)

        #have the later CAs prevent all the earlier ones
        for fromCA in range (2,self.numberStates-1):
            for toCA in range (0,fromCA-1):
                self.fsa.stateTurnsOffState(self.timerCells,fromCA,
                                            self.timerCells,toCA)

        
    def setupRecording(self):
        """Records spikes and voltages (i.e. analog signals)."""
        self.timerCells.record({'spikes','v'})

    def printResults(self,fileName):
        """Legacy."""
        fileName = fileName + ".pkl"
        self.timerCells.write_data(fileName)
        
#-- Access Functions
    def getTimerCells(self):
        """Returns ``self.timercells"""
        return self.timerCells



