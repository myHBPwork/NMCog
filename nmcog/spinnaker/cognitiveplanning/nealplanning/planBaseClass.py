"""
This is the base plan class.  It has all the functionality needed to make
a proto maes plan. 
Goals, facts, and modules are binary CAs.  
undone continous value CAs can be approximated with timers as shown in undone.

"""
# added for nmcog
import spynnaker8 as sim
from nmcog.spinnaker.specialfunction.neal.nealCoverClass import NealCoverFunctions
from nmcog.spinnaker.specialfunction.neal.stateMachineClass import FSAHelperFunctions


class PlanBaseClass:
    NUMBER_ACTIONS = -1
    NUMBER_FACTS = -1
    NUMBER_GOALS = -1
    NUMBER_MODULES = -1

    #def __init__(self, simName, sim,neal,spinnVersion,fsa):
    def __init__(self,simName="spinnaker",spinnVersion=8):
        self.simName = simName
        self.spinnVersion = spinnVersion
        self.sim = sim
        self.neal = NealCoverFunctions()
        self.fsa = FSAHelperFunctions

    #don't overload this
    def initializeBasePlanner(self):
        planCells = self.createNeurons()
        self.goalCells = planCells[0]
        self.moduleCells =planCells[1]
        self.factCells =planCells[2]
        self.actionCells =planCells[3]
        self.resetCells =planCells[4]
        #timerCells = self.createTimers()
        self.setupRecording()
        self.connectBasePlanner()

    #create the neurons for the goals and actions.
    def createNeurons(self):
        numberGoalCells = self.NUMBER_GOALS * self.fsa.CA_SIZE
        numberModuleCells = self.NUMBER_MODULES * self.fsa.CA_SIZE
        numberFactCells = self.NUMBER_FACTS * self.fsa.CA_SIZE
        numberActionCells = self.NUMBER_ACTIONS

        localGoalCells=self.sim.Population(numberGoalCells,self.sim.IF_cond_exp,
                    self.fsa.CELL_PARAMS)
        localModuleCells=self.sim.Population(numberModuleCells,
                    self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        localFactCells=self.sim.Population(numberFactCells,self.sim.IF_cond_exp,
                    self.fsa.CELL_PARAMS)
        resetCells=self.sim.Population(self.fsa.CA_SIZE,self.sim.IF_cond_exp,
                    self.fsa.CELL_PARAMS)
        if (self.simName == 'spinnaker')and(self.spinnVersion == 7) :
                import spynnaker_external_devices_plugin.pyNN as ExternalDevices
                localActionCells=self.sim.Population(numberActionCells,
                    self.sim.IF_cond_exp, self.fsa.CELL_PARAMS,
                    label='actionFromBoard')
                ExternalDevices.activate_live_output_for(localActionCells,
                    database_notify_port_num=12346)

        elif (self.simName == 'spinnaker')and(self.spinnVersion == 8) :
            import spynnaker8.external_devices as ExternalDevices
            localActionCells=self.sim.Population(numberActionCells,
                    self.sim.IF_cond_exp, self.fsa.CELL_PARAMS,
                    label='actionFromBoard')
            ExternalDevices.activate_live_output_for(localActionCells,
                    database_notify_port_num=12346)
            print "hey"
            
        elif (self.simName == 'nest'):
            #change tau_refrac so that the action cells don't fire too fast
            actionCellParams = self.fsa.CELL_PARAMS.copy()
            actionCellParams["tau_refrac"] = 10.0
            localActionCells=self.sim.Population(numberActionCells,
                        self.sim.IF_cond_exp, actionCellParams)

        return [localGoalCells,localModuleCells,localFactCells,localActionCells,resetCells]

    def setupRecording(self):
        if (self.neal.simulator=="nest") or ((self.neal.simulator == 'spinnaker') and (self.spinnVersion == 8)):
            self.goalCells.record({'spikes','v'})
            self.moduleCells.record({'spikes','v'})
            self.resetCells.record({'spikes','v'})
            self.factCells.record({'spikes','v'})
            self.actionCells.record({'spikes','v'})

        elif (self.neal.simulator == 'spinnaker') and (self.spinnVersion == 7):
            self.goalCells.record()
            self.moduleCells.record()
            self.factCells.record()
            self.actionCells.record()
            self.resetCells.record()

    def makeGoalCAs(self):
        for goalNumber  in range (0,self.NUMBER_GOALS):
            self.fsa.makeCA(self.goalCells,goalNumber)

    def makeModuleCAs(self):
        for moduleNumber  in range (0,self.NUMBER_MODULES):
            self.fsa.makeCA(self.moduleCells,moduleNumber)

    def makeFactCAs(self):
        for factNumber  in range (0,self.NUMBER_FACTS):
            self.fsa.makeCA(self.factCells,factNumber)

    #----Connect plan primitives directly
    def goalStartsModule(self,goal,module):
        self.fsa.stateTurnsOnState(self.goalCells,goal,
                                   self.moduleCells,module)

    def moduleHalfStartsAction(self,module,action):
        self.fsa.stateStimulatesOneNeuron(self.moduleCells,module,
                    self.actionCells,action,self.fsa.HALF_ON_WEIGHT) 

    def moduleStartsAction(self,module,action):
        self.fsa.stateTurnsOnOneNeuron(self.moduleCells,module,
                    self.actionCells,action) 

    def moduleStopsModule(self,fromModule,stopModule):
        self.fsa.stateTurnsOffState(self.moduleCells,fromModule,
                                        self.moduleCells,stopModule) 

    def factHalfStartsAction(self,fact,action):
        self.fsa.stateStimulatesOneNeuron(self.factCells,fact,self.actionCells,
                                          action,self.fsa.HALF_ON_WEIGHT) 

    def factStartsReset(self,fact):
        self.fsa.stateTurnsOnState(self.factCells,fact,self.resetCells,0)

    def factStopsGoal(self,fact,goal):
        self.fsa.stateTurnsOffState(self.factCells,fact,
                                        self.goalCells,goal) 

    def factStopsModule(self,fact,module):
        self.fsa.stateTurnsOffState(self.factCells,fact,
                                        self.moduleCells,module) 

    def actionStopsGoal(self,action,goal):
        self.fsa.oneNeuronTurnsOffState(self.actionCells,action,
                                        self.goalCells,goal) 

    def actionStopsModule(self,action,module):
        self.fsa.oneNeuronTurnsOffState(self.actionCells,action,
                                        self.moduleCells,module) 

    def actionStopsTimer(self,action,timer):
        timer.neuronStopsTimer(self.actionCells,action)

    #---common complex actions
    #A primitive has a goal, module and action.  The goal turns on the module,
    #the module turns on the action.  The action turns off the module and goal.
    def makePrimitive(self,goalNum,moduleNum,actionNum):
        self.fsa.stateTurnsOnState(self.goalCells,goalNum,
                                   self.moduleCells,moduleNum)
        self.fsa.stateTurnsOnOneNeuron(self.moduleCells,moduleNum,
                                self.actionCells,actionNum)
        self.fsa.oneNeuronTurnsOffState(self.actionCells,actionNum, 
                                        self.moduleCells,moduleNum)
        self.fsa.oneNeuronTurnsOffState(self.actionCells,actionNum, 
                                        self.goalCells,goalNum)

    #setup a compound action with two modules and two actions
    def makeCompound(self,goal,firstModule,secondModule,firstAction,
                     secondAction, timer):
        #goal turns on first module
        self.fsa.stateTurnsOnState(self.goalCells,goal,self.moduleCells,
                firstModule)

        #first module turns on first action and action stops it
        self.fsa.stateTurnsOnOneNeuron(self.moduleCells,firstModule,
                    self.actionCells,firstAction)
        self.fsa.oneNeuronTurnsOffState(self.actionCells,firstAction,
                                        self.moduleCells,firstModule)      

        #first module starts the timer which starts the second module
        timer.stateHalfStartsTimer(self.moduleCells,firstModule)
        timer.oneNeuronStartsTimer(self.actionCells,firstAction)
        #self.actxionStopsModule(firstAction,firstModule)
        timer.timerPreventsState(self.moduleCells,firstModule)
        timer.timerStartsState(self.moduleCells,secondModule)

        #the second module prevents the first starting up again
        self.fsa.stateTurnsOffState(self.moduleCells,secondModule,
                                    self.moduleCells,firstModule)

        #second module turns on second action
        self.fsa.stateTurnsOnOneNeuron(self.moduleCells,secondModule,
                                       self.actionCells,secondAction)

        #second action stops goal and second module
        self.fsa.oneNeuronTurnsOffState(self.actionCells,secondAction,
                                        self.goalCells,goal)      
        self.fsa.oneNeuronTurnsOffState(self.actionCells,secondAction,
                                        self.moduleCells,secondModule)      


    #a context sensitive module selection.  The initial module and
    #a fact pick a second module which has an action.  The action stops
    #the second module.
    def moduleAndFactStartModuleWithAction(self, fromModule, fact, toModule,
                                           toAction):
        self.fsa.stateHalfTurnsOnState(self.moduleCells,fromModule,
            self.moduleCells,toModule)
        self.fsa.stateHalfTurnsOnState(self.factCells,fact,
            self.moduleCells,toModule)

        self.fsa.stateTurnsOnOneNeuron(self.moduleCells,
                    toModule,self.actionCells,toAction)
        self.fsa.oneNeuronTurnsOffState(self.actionCells,toAction, 
                self.moduleCells,toModule)
        
    def allActionsCauseFullReset(self):
        for actionNum  in range (0,self.NUMBER_ACTIONS):
            self.actionCausesReset(actionNum,self.resetCells)
        
        for factNum  in range (0,self.NUMBER_FACTS):
            self.resetStopsFact(factNum)

    #RESETS 
    #Cause facts to be turned off.  
    def actionCausesReset(self,action,resetCells):
        #the reset isn't really a CA but it's that size.  The action
        #turns it on. 
        self.fsa.oneNeuronTurnsOnState(self.actionCells,action,resetCells,0)

    #A reset turns all the facts off (they can be turned on again)
    def resetStopsFact(self,fact):
        self.fsa.stateTurnsOffState(self.resetCells,0,self.factCells,fact)

    def connectBasePlanner(self):
        self.makeGoalCAs()
        self.makeModuleCAs()
        self.makeFactCAs()

    def printPklSpikes(self,fileName):
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
                    print neuronNum, spikes[spike]
        fileHandle.close()

    def printResults(self):
        if (self.simName=="spinnaker") and (self.spinnVersion == 7): 
            self.goalCells.write_data('results/planGoal.sp')
            self.moduleCells.write_data('results/planModule.sp')
            self.factCells.write_data('results/planFact.sp')
            self.actionCells.write_data('results/planAction.sp')
            self.resetCells.write_data('results/planReset.sp')
        elif (self.neal.simulator=="nest") or ((self.neal.simulator == 'spinnaker') and (self.spinnVersion == 8)):
            self.goalCells.write_data('results/planGoal.pkl')
            self.moduleCells.write_data('results/planModule.pkl')
            self.resetCells.write_data('results/planReset.pkl')
            self.factCells.write_data('results/planFact.pkl')
            self.actionCells.write_data('results/planAction.pkl')

    #test functions
    def testSetGoal(self,goalNumber,spikeGenerator):
        print "set Goal ", goalNumber
        #self.fsa.turnOnStateSpikeSource(spikeGenerator,goalNumber,self.goalCells)
        self.fsa.turnOnStateFromSpikeSource(spikeGenerator,
                                            self.goalCells, goalNumber)

    def testTurnOnFact(self,factNumber,spikeGenerator):
        self.fsa.turnOnStateFromSpikeSource(spikeGenerator,
                                            self.factCells, factNumber)

#-- Access Functions
    #The goal should be set by the user.  Typically this is done
    #from the parser.
    def getGoalCells(self):
        return self.goalCells

    def getActionCells(self):
        return self.actionCells

    def getModuleCells(self):
        return self.moduleCells

    def getFactCells(self):
        return self.factCells

    #We need to get the action cells in nest to set up the output from cabot
    def getActionSpikeDet(self):
        return self.actionSpikeDet
