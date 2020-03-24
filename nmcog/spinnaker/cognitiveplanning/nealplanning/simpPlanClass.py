"""
This plan class has just four primitive goal-module-action triples.
"""
# added for nmcog
import spynnaker8 as sim
from nmcog.spinnaker.specialfunction.neal.nealCoverClass import NealCoverFunctions
from nmcog.spinnaker.specialfunction.neal.stateMachineClass import FSAHelperFunctions

from .planBaseClass import PlanBaseClass

class PlanClass (PlanBaseClass):
    NUMBER_GOALS = 4
    goalTurnRight = 0
    goalTurnLeft = 1
    goalStepForward = 2
    goalStepBackward = 3

    NUMBER_MODULES = 4
    moduleTurnRight = 0
    moduleTurnLeft = 1
    moduleStepForward = 2
    moduleStepBackward = 3

    NUMBER_FACTS = 1
    bumpFact = 0

    NUMBER_ACTIONS = 4
    actionRight = 0
    actionLeft = 1
    actionForward = 2
    actionBackward = 3

    #def __init__(self, simName,sim,neal,spinnVersion,fsa):
        #PlanBaseClass.__init__(self,simName,sim,neal,spinnVersion,fsa)
    def __init__(self,simName="spinnaker",spinnVersion=8):
        PlanBaseClass.__init__(self)
        self.simName = simName
        self.spinnVersion = spinnVersion
        self.sim = sim
        elf.neal = NealCoverFunctions()
        self.fsa = FSAHelperFunctions
        self.initializeBasePlanner()


    def connectSimplePlanner(self):
        self.makePrimitive(self.goalTurnRight,self.moduleTurnRight,
                           self.actionRight)
        self.makePrimitive(self.goalTurnLeft,self.moduleTurnLeft,
                           self.actionLeft)
        self.makePrimitive(self.goalStepForward,self.moduleStepForward,
                           self.actionForward)
        self.makePrimitive(self.goalStepBackward,self.moduleStepBackward,
                           self.actionBackward)
 
    def printResults(self):
        PlanBaseClass.printResults(self)

    def testStimulateFact(self,factNumber,spikeGenerator):
        self.fsa.turnOnStateFromSpikeSource(spikeGenerator,
                                            self.factCells, factNumber)

