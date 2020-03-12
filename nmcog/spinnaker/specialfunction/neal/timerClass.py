"""
This makes several different types of timers and provides mechanisms
for the timers to effect other states and be turned on by other 
states, spike sources and neurons.
"""

# added for nmcog
import spynnaker8 as sim
from .nealCoverClass import NealCoverFunctions
from .stateMachineClass import FSAHelperFunctions

#---- Code
class TimerClass:
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
        self.fsa.turnOnStateFromSpikeSource(spikeGen,self.timerCells,0)

    def stateStartsTimer(self,stateNeurons,state):
        self.fsa.stateTurnsOnState(stateNeurons,state,self.timerCells,0)

    #undone not in test
    def oneNeuronStartsTimer(self,fromNeurons,fromNeuron):
        self.fsa.oneNeuronStimulatesState(fromNeurons,fromNeuron,
            self.timerCells,0,self.oneNeuronFullWeight)

    def oneNeuronHalfStartsTimer(self,fromNeurons,fromNeuron):
        self.fsa.oneNeuronStimulatesState(fromNeurons,fromNeuron,
            self.timerCells,0,self.oneNeuronHalfWeight)

    def stateHalfStartsTimer(self,stateNeurons,state):
        self.fsa.stateHalfTurnsOnState(stateNeurons,state,self.timerCells,0)

    #----stop functions
    #undone needs a test and move to timer
    def neuronStopsTimer(self,stopNeurons,stopNeuron):
        for timerCA in range (0,self.numberStates):
            self.fsa.oneNeuronTurnsOffState(stopNeurons,stopNeuron,
                                        self.timerCells,timerCA)

    #undone needs a test
    def stateStopsTimer(self,stateNeurons,state):
        for timerCA in range (0,self.numberStates):
            self.fsa.stateTurnsOffState(stateNeurons,state,
                                        self.timerCells,timerCA)

    #---timer output functions
    #The last state of a timer starts a state
    def timerStartsState(self,stateNeurons,state):
        #stateTurnsOnState can take a couple of steps.
        #self.fsa.stateTurnsOnState(self.timerCells,self.numberStates-1,
        #                           stateNeurons,state)
        self.fsa.stateStimulatesState(self.timerCells,self.numberStates-1,
                                      stateNeurons,state,0.02)

    def timerPreventsState(self,stateNeurons,state):
        for CA in range (0,self.numberStates-1):
            self.fsa.stateTurnsOffState(self.timerCells,CA,
                                   stateNeurons,state)

    #undone needs a test
    def timerActivatesState(self,stateNeurons,state,wt):
        for CA in range (0,self.numberStates-1):
            self.fsa.stateStimulatesState(self.timerCells,CA,stateNeurons,
                                          state,wt)


    #---create timer functions
    #The timer goes from state to state and the last stops on its own
    def makeStopTimerSynapses(self):
        for CA in range (0,self.numberStates-1):
            self.fsa.makeCA(self.timerCells,CA)
            self.fsa.stateStimulatesState(self.timerCells,CA,self.timerCells,
                                             CA+1,self.forwardWeight)
            self.fsa.stateTurnsOffState(self.timerCells,CA+1,self.timerCells,CA)
            
    #The timer goes from state to state and the last stops on its own
    #Only one state is on at at time
    def makeOneStateStopTimerSynapses(self):
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
        self.timerCells.record({'spikes','v'})

    def printResults(self,fileName):
        fileName = fileName + ".pkl"
        self.timerCells.write_data(fileName)
#-- Access Functions
    def getTimerCells(self):
        return self.timerCells



