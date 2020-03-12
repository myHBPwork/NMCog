"""
This is driven by an FSA that manages the binding and the retrievals.
Initially, (startState) it waits for a binding event.  It then
tryToBind, which uses a timer since it takes time to bind.  If it
succeeds it goes to bindOnState
bindOn turns on the bindingTimer
the bindingTimer turns on bindDone state
bindDone -> start via bindDoneTimer.

Fail states occurs with bindFailState twoPlacesFact, twoObjectsFact,
and notEnoughPlaceObjectsFact.

retrievePlaceState is turned on externally by a query.
It turns off start.  It allows the binding nets to fire, and when a place
fires, it turns on the placeRetrievedFact (extra neurons in the automaton net).
Together these turn on retrievePlaceDone, which then goes back to startState

A similar mechanism is used for retrieveObject.
"""
from nmcog.spinnaker.specialfunction.neal.nealCoverClass import NealCoverFunctions
from nmcog.spinnaker.specialfunction.neal.timerClass import TimerClass

# added for nmcog
import spynnaker8 as sim
from nmcog.spinnaker.specialfunction.neal.stateMachineClass import FSAHelperFunctions

class CogmapBaseClass:
    numberAutomatonStates = 15
    numberObjects = -1
    numberPlaces = -1
    
    #def __init__(self,simName,sim,neal,spinnVersion,fsa):
    def __init__(self,simName="spinnaker",spinnVersion=8):
        self.simName = simName
        self.sim = sim
        self.neal = NealCoverFunctions()
        self.spinnVersion = spinnVersion
        self.fsa = FSAHelperFunctions()
        # added for nmcog
        self.tryToBindTimer = TimerClass(self.simName,self.sim,self.neal,
                                         self.spinnVersion,self.fsa)
        self.bindingTimer = TimerClass(self.simName,self.sim,self.neal,
                                       self.spinnVersion,self.fsa)
        self.bindDoneTimer = TimerClass(self.simName,self.sim,self.neal,
                                        self.spinnVersion,self.fsa)
        # this instantiates the three timers but the timercells are not created here
        # they are created in self.createTimers where default values are used for the
        # number of states but user can pass custom values.
        # however, self.creteTimers is called by self.createAutomaton therefore
        # these custom values must be passed into this function which takes effect on
        # the self.createTimers function.
        #
        #self.automatonCells = self.createAutomaton() # commented out for nmcog

    #-----FSA functions and constants
    #state names
    startState = 0
    tryBindState = 1
    bindOnState = 2
    bindFailState = 3
    bindDoneState = 4
    retrieveObjectState = 5
    retrievePlaceState = 6
    retrieveObjectDoneState = 7
    retrievePlaceDoneState = 8
    lastState = 8
    onePlaceOneObjectFact = lastState+1 #one placeBindOn and one objectBindOn on
    twoPlacesFact = lastState+2 #two or more placeBindOn
    twoObjectsFact = lastState+3 #two or more objectBindOn
    notEnoughPlaceObjectsFact = lastState+4 #0 or 1 objects place in total
    placeRetrievedFact = lastState+5
    objectRetrievedFact = lastState+6

    #Each object and place half connects to the onePlaceOneObjectFact
    #Note that 2 of either will turn it on as will more than one of each.
    #These are handled elsewhere to convert to the bindFailState
    def setupObjectPlaceFacts(self):
        print(self.numberObjects)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.objectBindOnCells,objectNumber,
                            self.automatonCells,self.onePlaceOneObjectFact)
            self.fsa.stateHalfTurnsOnState(self.objectBindOnCells,objectNumber,
                            self.automatonCells,self.twoObjectsFact)

        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.placeBindOnCells,placeNumber,
                            self.automatonCells,self.onePlaceOneObjectFact)
            self.fsa.stateHalfTurnsOnState(self.placeBindOnCells,placeNumber,
                            self.automatonCells,self.twoPlacesFact)

    #---Make the fsa that governs the map.  
    def stateStopsPlaceDone(self,stateNumber):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.placeBindDoneCells,placeNumber)

    def stateStopsObjectDone(self,stateNumber):
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.objectBindDoneCells,objectNumber)

    def stateStopsDone(self,stateNumber):
        self. stateStopsPlaceDone(stateNumber)
        self. stateStopsObjectDone(stateNumber)

    def connectStartState(self):
        #the bind signal moves from start to tryBind
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.startState,
                                       self.automatonCells,self.tryBindState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.tryBindState,
                                       self.automatonCells,self.startState)
        self.tryToBindTimer.stateStartsTimer(self.automatonCells,
                                                 self.tryBindState)

        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                                       self.automatonCells,self.bindDoneState)

        self.stateStopsDone(self.startState)

        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                            self.automatonCells,self.retrieveObjectDoneState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                            self.automatonCells,self.retrievePlaceDoneState)

        self.statePreventsOutput(self.startState)


    def statePreventsPlaceOutput(self,stateNumber):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.answerPlaceCells,placeNumber)

    def statePreventsObjectOutput(self,stateNumber):
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.answerObjectCells,objectNumber)

    def statePreventsOutput(self,stateNumber):
        self. statePreventsPlaceOutput(stateNumber)
        self. statePreventsObjectOutput(stateNumber)

    #-----Connect States----
    def connectBindOnState(self):
        #1p1o fact moves from tryBind to bindOn
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.tryBindState,
                                       self.automatonCells,self.bindOnState)
        self.setupObjectPlaceFacts()
        #Half_on is 0.0012, here we go slower so that it comes up slower
        #if two places is on
        #funnyWt = 0.001
        #if ((self.neal.simulator == 'spinnaker') and (self.neal.spinnVersion == 8)):
        #    funnyWt = 0.0011
        funnyWt = 0.0011

        self.fsa.stateStimulatesState(self.automatonCells,
                        self.onePlaceOneObjectFact,self.automatonCells,
                                      self.bindOnState,funnyWt)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindOnState,
                                       self.automatonCells,self.tryBindState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindOnState,
                                self.automatonCells,self.onePlaceOneObjectFact)
        #stop tryBindTimer
        self.tryToBindTimer.stateStopsTimer(self.automatonCells,
                                            self.bindOnState)

        self.statePreventsOutput(self.bindOnState)
        
    def connectBindFailState(self):
        #2p, 2o, or timer goes to bindFail 
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.tryBindState,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.twoPlacesFact,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.twoObjectsFact,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.notEnoughPlaceObjectsFact,self.automatonCells,
                                       self.bindFailState)
        self.tryToBindTimer.timerStartsState(self.automatonCells, #timeout fail
                                            self.notEnoughPlaceObjectsFact)

        #fail prevents on
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.bindOnState)

        #turn states and timers off
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.tryBindState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.twoPlacesFact)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.twoObjectsFact)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.automatonCells,self.onePlaceOneObjectFact)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.automatonCells,self.notEnoughPlaceObjectsFact)
        self.tryToBindTimer.stateStopsTimer(self.automatonCells,
                                            self.bindFailState)

        #fail goes right back to start
        self.fsa.stateTurnsOnState(self.automatonCells,self.bindFailState,
                            self.automatonCells,self.startState)

    def bindFailStopsPlaceObjectOn(self):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.placeBindOnCells,placeNumber)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.objectBindOnCells,objectNumber)

    def bindOnPrimesPlaceAndObjectBind(self):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,self.bindOnState,
                            self.placeBindCells,placeNumber)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,self.bindOnState,
                            self.objectBindCells,objectNumber)

    def stopPlaceAndObjectBind(self,stateNumber):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.placeBindCells,placeNumber)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.objectBindCells,objectNumber)
packages calling internal function
    def connectBindDoneState(self):
        #timer moves to binddone
        self.bindingTimer.stateStartsTimer(self.automatonCells, 
                                            self.bindOnState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.bindOnState,
                                       self.automatonCells,self.bindDoneState)
        self.bindingTimer.timerStartsState(self.automatonCells, 
                                            self.bindDoneState)

        self.bindOnPrimesPlaceAndObjectBind()

        self.fsa.stateTurnsOffState(self.automatonCells,self.bindDoneState,
                            self.automatonCells,self.bindOnState)
        self.stopPlaceAndObjectBind(self.bindDoneState)

        #binding done returns to start via timer
        self.bindDoneTimer.stateStartsTimer(self.automatonCells, 
                                            self.bindDoneState)
        self.bindDoneTimer.timerStartsState(self.automatonCells, 
                                            self.startState)

        self.statePreventsOutput(self.bindDoneState)


    def retrieveObjectPrimesPlaceBind(self):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,
                    self.retrieveObjectState,self.placeBindCells,placeNumber)

    def answerPlaceStartsPlaceRetrievedFact(self):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOnState(self.answerPlaceCells,placeNumber,
                    self.automatonCells,self.placeRetrievedFact)

    def connectRetrieveObjectState(self):
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.startState,
                        self.automatonCells,self.retrieveObjectState)
        self.retrieveObjectPrimesPlaceBind()
        self.statePreventsPlaceOutput(self.retrieveObjectState)
        self.answerPlaceStartsPlaceRetrievedFact()
        self.fsa.stateTurnsOffState(self.automatonCells,
                self.retrieveObjectState,self.automatonCells,self.startState)

    def connectRetrieveObjectDoneState(self):
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.retrieveObjectState,self.automatonCells,
                                       self.retrieveObjectDoneState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.objectRetrievedFact,self.automatonCells,
                                       self.retrieveObjectDoneState)
        self.fsa.stateTurnsOffState(self.automatonCells,
            self.retrieveObjectDoneState,self.automatonCells,
                                       self.retrieveObjectState)
        #don't need the output on anymore
        self.statePreventsObjectOutput(self.retrieveObjectDoneState)
        self.stopPlaceAndObjectBind(self.retrieveObjectDoneState)

        self.fsa.stateTurnsOnState(self.automatonCells,
            self.retrieveObjectDoneState,self.automatonCells,
                                       self.startState)

    def retrievePlacePrimesObjectBind(self):
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,
                    self.retrievePlaceState,self.objectBindCells,objectNumber)

    def answerObjectStartsObjectRetrievedFact(self):
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOnState(self.answerObjectCells,objectNumber,
                    self.automatonCells,self.objectRetrievedFact)

    def connectRetrievePlaceState(self):
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.startState,
                        self.automatonCells,self.retrievePlaceState)
        self.retrievePlacePrimesObjectBind()
        self.statePreventsObjectOutput(self.retrievePlaceState)
        self.answerObjectStartsObjectRetrievedFact()
        self.fsa.stateTurnsOffState(self.automatonCells,
                self.retrievePlaceState,self.automatonCells,self.startState)

    def connectRetrievePlaceDoneState(self):
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.retrievePlaceState,self.automatonCells,
                                       self.retrievePlaceDoneState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.placeRetrievedFact,self.automatonCells,
                                       self.retrievePlaceDoneState)
        self.fsa.stateTurnsOffState(self.automatonCells,
            self.retrievePlaceDoneState,self.automatonCells,
                                       self.retrievePlaceState)
        #don't need the output on anymore
        self.statePreventsPlaceOutput(self.retrievePlaceDoneState)
        self.stopPlaceAndObjectBind(self.retrievePlaceDoneState)

        self.fsa.stateTurnsOnState(self.automatonCells,
            self.retrievePlaceDoneState,self.automatonCells,
                                       self.startState)

    def connectAutomaton(self):
        self.connectStartState()
        self.connectBindOnState()
        self.connectBindFailState()
        self.bindFailStopsPlaceObjectOn()
        self.connectBindDoneState()
        self.connectRetrieveObjectState()
        self.connectRetrievePlaceState()
        self.connectRetrieveObjectDoneState()
        self.connectRetrievePlaceDoneState()

    #def createTimers(self):
        #self.tryToBindTimer = TimerClass(self.simName,self.sim,self.neal,
        #                                 self.spinnVersion,self.fsa,10)
        #self.bindingTimer = TimerClass(self.simName,self.sim,self.neal,
        #                               self.spinnVersion,self.fsa,10)
        #self.bindDoneTimer = TimerClass(self.simName,self.sim,self.neal,
        #                                self.spinnVersion,self.fsa,6)
    def createTimers(self, tryToBindStates=10, bindingStates=10, bindDoneStates=6):
        # modified for nmcog
        self.tryToBindTimer.createNeurons( tryToBindStates ) # although default values are set
        self.bindingTimer.createNeurons( bindingStates )     # user can pass custom number of states
        self.bindDoneTimer.createNeurons( bindDoneStates )
        #the timerClass sets recording
        self.tryToBindTimer.makeStopNoRestartTimerSynapses()
        self.bindingTimer.makeStopNoRestartTimerSynapses()
        self.bindDoneTimer.makeStopNoRestartTimerSynapses()

    #def createAutomaton(self): # commented out for nmcog
    def createAutomaton(self, tryToBindStates=10, bindingStates=10, bindDoneStates=6):
        numNeurons = self.fsa.CA_SIZE * self.numberAutomatonStates
        
        cells=self.sim.Population(numNeurons,self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        for stateNumber in range (0,self.numberAutomatonStates):
            self.fsa.makeCA(cells,stateNumber)

        #self.createTimers() # commented out for nmcog
        self.createTimers(tryToBindStates=tryToBindStates, bindingStates=bindingStates,
                          bindDoneStates=bindDoneStates)
        return cells

    def createObjects(self, numberObjects):
        self.numberObjects = numberObjects
        #print 'objects',numberObjects
        numberObjectCells = self.numberObjects*self.fsa.CA_SIZE
        self.objectBindCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.objectBindOnCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.objectBindDoneCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.queryOnObjectCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.answerObjectCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)

        for objectNumber in range (0,self.numberObjects):
            self.fsa.makeCA(self.objectBindCells,objectNumber)
            self.fsa.makeCA(self.objectBindOnCells,objectNumber)
            self.fsa.makeCA(self.objectBindDoneCells,objectNumber)
            self.fsa.makeCA(self.queryOnObjectCells,objectNumber)
            self.fsa.makeCA(self.answerObjectCells,objectNumber)

    def connectObjects(self):
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.objectBindOnCells,objectNumber,
                                       self.objectBindCells,objectNumber)
            self.fsa.stateTurnsOnState(self.objectBindCells,objectNumber,
                                       self.objectBindDoneCells,objectNumber)
            self.fsa.stateTurnsOffState(self.objectBindDoneCells,objectNumber,
                                       self.objectBindOnCells,objectNumber)
            self.fsa.stateHalfTurnsOnState(self.queryOnObjectCells,objectNumber,
                                       self.objectBindCells,objectNumber)
            self.fsa.stateTurnsOnState(self.objectBindCells,objectNumber,
                                       self.answerObjectCells,objectNumber)

    #Create neurons for each place and make them CAs.
    def createPlaces(self, numberPlaces):
        self.numberPlaces = numberPlaces
        print('places',numberPlaces)
        numberPlaceCells = self.numberPlaces*self.fsa.CA_SIZE
        self.placeBindCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.placeBindOnCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.placeBindDoneCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.queryOnPlaceCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.answerPlaceCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)

        for placeNumber in range (0,self.numberPlaces):
            self.fsa.makeCA(self.placeBindCells,placeNumber)
            self.fsa.makeCA(self.placeBindOnCells,placeNumber)
            self.fsa.makeCA(self.placeBindDoneCells,placeNumber)
            self.fsa.makeCA(self.queryOnPlaceCells,placeNumber)
            self.fsa.makeCA(self.answerPlaceCells,placeNumber)

    def connectPlaces(self):
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.placeBindOnCells,placeNumber,
                                       self.placeBindCells,placeNumber)
            self.fsa.stateTurnsOnState(self.placeBindCells,placeNumber,
                                       self.placeBindDoneCells,placeNumber)
            self.fsa.stateTurnsOffState(self.placeBindDoneCells,placeNumber,
                                       self.placeBindOnCells,placeNumber)
            self.fsa.stateHalfTurnsOnState(self.queryOnPlaceCells,placeNumber,
                                       self.placeBindCells,placeNumber)
            self.fsa.stateTurnsOnState(self.placeBindCells,placeNumber,
                                       self.answerPlaceCells,placeNumber)

    def setupCogMapRecording(self):
        self.placeBindCells.record({'spikes'})
        self.objectBindCells.record({'spikes'})
        self.automatonCells.record({'spikes'})
        self.placeBindOnCells.record({'spikes'})
        self.objectBindOnCells.record({'spikes'})
        self.placeBindDoneCells.record({'spikes'})
        self.objectBindDoneCells.record({'spikes'})
        self.queryOnPlaceCells.record({'spikes'})
        self.queryOnObjectCells.record({'spikes'})
        self.answerPlaceCells.record({'spikes'})
        self.answerObjectCells.record({'spikes'})

    def getWellConnectedConn(self,fromSize,toSize,weight):
        connector = []
        for fromNeuron in range (0,fromSize):
            for toNeuron in range (0, toSize):
                connector=connector+[(fromNeuron,toNeuron,weight,
                                      self.neal.DELAY)]
        return connector

    def makeLearningSynapses(self):
        numberPlaceBindCells = self.numberPlaces*self.fsa.CA_SIZE
        numberObjectBindCells = self.numberObjects*self.fsa.CA_SIZE
        synWeight = 0.0

        placeToObjectConnector = self.getWellConnectedConn(
            numberPlaceBindCells,numberObjectBindCells,synWeight)
        placeToObjectConnList = self.sim.FromListConnector(
            placeToObjectConnector)

        objectToPlaceConnector = self.getWellConnectedConn(
            numberObjectBindCells,numberPlaceBindCells,synWeight)
        objectToPlaceConnList = self.sim.FromListConnector(
            objectToPlaceConnector)
        stdp_model = self.sim.STDPMechanism(
                timing_dependence = self.sim.SpikePairRule(tau_plus=16.0, 
                                tau_minus=3.0,A_plus=0.002, A_minus=0.0),
                #timing_dependence = self.sim.SpikePairRule(tau_plus=16.7, 
                #                tau_minus=3.7,A_plus=0.002, A_minus=0.0),
                                #tau_minus=3.7,A_plus=0.005, A_minus=0.0),#works
                                #tau_minus=3.7,A_plus=0.001, A_minus=0.0002),
                                #tau_minus=0.01,A_plus=0.005, A_minus=0.002),
                weight_dependence = self.sim.AdditiveWeightDependence(
                    w_min=0.0, w_max=0.004) 
                    #w_min=0.0, w_max=0.015) #.015 .004 .0015
                    #w_min=0.0, w_max=0.02) 
            )

        self.sim.Projection(self.placeBindCells,self.objectBindCells,
                            self.sim.AllToAllConnector(),
                            #placeToObjectConnList,
                            synapse_type=stdp_model)

        self.sim.Projection(self.objectBindCells,self.placeBindCells,
                            #objectToPlaceConnList,
                            self.sim.AllToAllConnector(),
                            synapse_type=stdp_model)
        #print 'bob', placeToObjectConnector
        #print objectToPlaceConnector

    #---Defs for turning things on and off with spike sources.
    def sourceTurnsOnPlace(self, placeNumber, source):
        self.fsa.turnOnStateFromSpikeSource(source,self.placeBindCells,
                                            placeNumber)
    def sourceTurnsOffPlace(self, placeNumber, source):
        self.fsa.turnOffStateFromSpikeSource(source,self.placeBindCells,
                                            placeNumber)

    def sourceTurnsOnObject(self, objectNumber, source):
        self.fsa.turnOnStateFromSpikeSource(source,self.objectBindCells,
                                            objectNumber)
    def sourceTurnsOffObject(self, objectNumber, source):
        self.fsa.turnOffStateFromSpikeSource(source,self.objectBindCells,
                                            objectNumber)

    def sourceTurnsOnBind(self, source):
        self.fsa.halfTurnOnStateFromSpikeSource(source,self.automatonCells,
                                                self.tryBindState)

    def sourceTurnsOnObjectOn(self, objectNumber, source):
        self.fsa.turnOnStateFromSpikeSource(source,self.objectBindOnCells,
                                            objectNumber)

    def sourceTurnsOnPlaceOn(self, placeNumber, source):
        self.fsa.turnOnStateFromSpikeSource(source,self.placeBindOnCells,
                                            placeNumber)

    def sourceStartsAutomaton(self, source):
        self.fsa.turnOnStateFromSpikeSource(source,self.automatonCells,
                                             self.startState)

    def sourceTurnOnRetrieveObjectFromPlace(self, source):
        self.fsa.halfTurnOnStateFromSpikeSource(source,self.automatonCells,
                                                self.retrieveObjectState)

    def sourceTurnOnRetrievePlaceFromObject(self, source):
        self.fsa.halfTurnOnStateFromSpikeSource(source,self.automatonCells,
                                                self.retrievePlaceState)

    def sourceTurnsOnPlaceQuery(self, source,placeNumber):
        self.fsa.turnOnStateFromSpikeSource(source,self.queryOnPlaceCells,
                                            placeNumber)

    def sourceTurnsOnObjectQuery(self, source,objectNumber):
        self.fsa.turnOnStateFromSpikeSource(source,self.queryOnObjectCells,
                                            objectNumber)

    def printCogMapNets(self):
        suffix = '.pkl'
        self.placeBindCells.write_data('results/cmPlaceBind'+suffix)
        self.objectBindCells.write_data('results/cmObjectBind'+suffix)
        self.automatonCells.write_data('results/cmAutomaton'+suffix)
        self.placeBindOnCells.write_data('results/cmPlaceBindOn'+suffix)
        self.objectBindOnCells.write_data('results/cmObjectBindOn'+suffix)
        self.placeBindDoneCells.write_data('results/cmPlaceBindDone'+suffix)
        self.objectBindDoneCells.write_data('results/cmObjectBindDone'+suffix)
        self.queryOnPlaceCells.write_data('results/cmQueryOnPlace'+suffix)
        self.queryOnObjectCells.write_data('results/cmQueryOnObject'+suffix)
        self.answerPlaceCells.write_data('results/cmAnswerPlace'+suffix)
        self.answerObjectCells.write_data('results/cmAnswerObject'+suffix)
        self.tryToBindTimer.printResults('results/cmTryToBindTimer')
        self.bindingTimer.printResults('results/cmBindingTimer')
        self.bindDoneTimer.printResults('results/cmBindDoneTimer')
