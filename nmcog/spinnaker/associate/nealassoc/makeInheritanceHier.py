# ~/nmcog/spinnaker/associate/nealassoc/makeInheritanceHier.py
#
# Documentation by Lungsi 24 March 2020
#
# Code based on Jan2020 Chris Huyck et al.
# http://www.cwa.mdx.ac.uk/NEAL/code/assocMemJan2020.tar.gz
#
# Create an neural topology that has an inheritance hierarchy.
# In PyNN/python the topology can be accessed via this class.
#
# Invoke by creating the class, then calling createNeuralInheritanceHierarcy 
# with an inheritance hierarchy specified in python (readInheritanceClass is one
# way).

import sys
import numpy as np
#import cPickle as pickle
import pickle # for Python3
# added for nmcog
import spynnaker8 as sim
from nmcog.spinnaker.specialfunction.neal import NealCoverFunctions
from nmcog.spinnaker.specialfunction.neal import FSAHelperFunctions

class NeuralInheritanceClass:
    """
    
    +-------------------+--------+----------------------------------------------+
    | Constants         | values | comments                                     |
    +===================+========+==============================================+
    | ``neuronsPerCA``  | 10     | -                                            |
    +-------------------+--------+----------------------------------------------+
    | ``intraCAWeight`` | 0.0085 | - 0.01 is hot (every 4 ms)                   |
    |                   |        | - 0.005 does not go                          |
    +-------------------+--------+----------------------------------------------+
    | ``hierWeight``    | 0.0012 | - replaced with 1/2 fsa connection           |
    +-------------------+--------+----------------------------------------------+
    | ``primeWeight``   | 0.017  | - 0.016-0.015 threee levels of hier in 75 ms |
    |                   |        | - 0.02 too big                               |
    +-------------------+--------+----------------------------------------------+
    
    
    
    +----------------------------------------------+---------------------------------------------+----------------------------------------------+
    | Methods                                      |  Argument                                   | Caller                                       |
    +==============================================+=============================================+==============================================+
    | :py:meth:`.createNeuralInheritanceHierarchy` | - instance of :ref:`InheritanceReaderClass` | :ref:`NeuralThreeAssocClass`                 |
    +----------------------------------------------+---------------------------------------------+----------------------------------------------+
    | :py:meth:`.createNeurons`                    | - number of neurons                         | :py:meth:`.createNeuralInheritanceHierarchy` |
    +----------------------------------------------+---------------------------------------------+----------------------------------------------+
    | :py:meth:`.setRecord`                        | -                                           | :py:meth:`.createNeuralInheritanceHierarchy` |
    +----------------------------------------------+---------------------------------------------+----------------------------------------------+
    | :py:meth:`.makeCAs`                          | -                                           | :py:meth:`.createNeuralInheritanceHierarchy` |
    +----------------------------------------------+---------------------------------------------+----------------------------------------------+
    | :py:meth:`.makeHiersFromHier`                | - instance of :ref:`InheritanceReaderClass` | :py:meth:`.createNeuralInheritanceHierarchy` |
    +----------------------------------------------+---------------------------------------------+----------------------------------------------+
    | :py:meth:`.createTestAllUnits`               | - initial (first) start time                | :ref:`NeuralThreeAssocClass`                 |
    +----------------------------------------------+---------------------------------------------+----------------------------------------------+
    
    
    
    **Note:**
    
    * Specifically the instance of :ref:`InheritanceReaderClass` is the base data for :ref:`NEAL3Way`. An example base data is
    
    ::
    
        bases = {"units": ["animal", "mammal", "bird", "canary"],
                "relations": [ ["canary", "bird"], ["bird", "animal"], ["mammal", "animal"] ]}
        basedata = InheritanceReaderClass()
        basedata.numberUnits = len(bases["units"])
        basedata.units = bases["units"]
        basedata.isARelationships = bases["relations"]
    
    
    """
    #constants
    neuronsPerCA = 10
    intraCAWeight = 0.0085 # .01 is hot (every 4 ms) .005 doesn't go #replaced with fsa state weights
    hierWeight = 0.0012 #replaced with half fsa connections undone 
    primeWeight = 0.017#0.016-0.015 three levels of hier in 75 ms#.02 too big

    #class variables
    numCAs = -1
    cells = None
    
    #def __init__(self, simName,sim,neal,spinnVersion,fsa):
    def __init__(self, simName="spinnaker",spinnVersion=8): # modified for nmcog
        self.simName = simName
        self.spinnVersion = spinnVersion
        self.sim = sim
        self.neal = NealCoverFunctions()
        self.fsa = FSAHelperFunctions()

    def createNeurons(self,numNeurons):
        """Creates a population of `IF_cond_exp <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_ neurons with :ref:`FSAHelperFunctions` ``.CELL_PARAMS``."""
        self.cells = self.sim.Population(numNeurons,self.sim.IF_cond_exp, 
                                    self.fsa.CELL_PARAMS)

    def setRecord(self):
        """Records spikes of all the neurons in the population created via :py:meth:`.createNeurons`."""
        self.cells.record(['spikes'])

    #Make a binary CA for each unit
    def makeCAs(self):
        """Makes ``numCAs`` assemblies of cell, i.e. connect neurons in the population created via :py:meth:`.createNeurons`."""
        for CA in range (0,self.numCAs):
            self.fsa.makeCA(self.cells,CA)

    #make a hierarchical relationship for each isA pair passed in
    def makeHiersFromHier(self,pythonHier):
        """Makes a hierarchical relationship for each "isA" pair (see above for a ``basedata`` example).
        For each "isA" relationship pair cell assemblies of the first element excites those of the second (using :ref:`FSAHelperFunctions` ``.stateHalfTurnsOnState`` with constant :ref:`FSAHelperFunctions` ``.HALF_ON_WEIGHT``).
        
        * Refer to :ref:`FSAHelperFunctions` ``.stateHalfTurnsOnState`` for how the cell assemblies are connected.
        
        """
        isAPairs = pythonHier.isARelationships
        numberPairs = len(isAPairs)
        for pairNumber in range (0,numberPairs):
            subCatName = isAPairs[pairNumber][0]
            superCatName = isAPairs[pairNumber][1]
            subCatNumber = pythonHier.getUnitNumber(subCatName)
            superCatNumber = pythonHier.getUnitNumber(superCatName)
            #print subCatName,superCatName,subCatNumber,superCatNumber
            #make one hierarchical relations as a half CA connection
            self.fsa.stateHalfTurnsOnState(self.cells,subCatNumber,
                                           self.cells,superCatNumber)

    #--Main way to create the heirarchy topology
    def createNeuralInheritanceHierarchy(self,inheritanceStructure):
        """Given an instance of :ref:`InheritanceReaderClass` a heirarchy topology is created.
        
        Consider the example for :ref:`NEAL3Way` whose base data is the instance such that,
        
        ::
        
            bases = {"units": ["animal", "mammal", "bird", "canary"],
                    "relations": [ ["canary", "bird"], ["bird", "animal"], ["mammal", "animal"] ]}
            basedata = InheritanceReaderClass()
            basedata.numberUnits = len(bases["units"])
            basedata.units = bases["units"]
            basedata.isARelationships = bases["relations"]
        
        Then,
        
        * A cell assembly is created for each association unit, i.e. respective assemblies for "animal", "mammal", "bird", and "canary".
        
            - A cell assembly by default has ten `neuron populations <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_. See :ref:`FSAHelperFunctions` ``.makeCA`` for more detail.
            - For this example four cell assemblies will be created.
        
        * Size of each population in an assembly comprises of some factor of the total number of association units considered. For instance, some factor times the total number of association units. The factor is named ``neuronsPerCA``.
        
            - By default, this is 10 times the total number of units.
            - For our example every population in each cell assembly will contain 40 `neurons. <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#standard-cell-types>`_
        
        * Connect (excitatory) cell assemblies among association units that form a "isA" relationship pair.
        
        Therefore, the hierarchy topology is connection among cell assemblies that form a "isA" relationship pair.
        
        **What is the practical meaning of the cell assemblies of a "hierarchy topology" in terms of extracting/visualizing the neuron units in a population?**
        
        * For our example of four base units ``["animal", "mammal", "bird", "canary"]``, i.e. there will be four cell assemblies.
        * By default ``neuronsPerCA`` = 10 (Notice that this value is equal to :ref:`FSAHelperFunctions` ``.CA_SIZE`` = 10)
        * Invoking :py:meth:`createNeurons` creates all the neuron units that will make the cell assemblies.
        
            - :py:meth:`createNeurons` creates all the neuron units in one attribute ``self.cells``
            
        * After simulating for a particular runtime, spikes from all the neurons (i.e. all neuron units in all the neuronal populations in all the assemblies) by
        
        ::
        
            allspikes = self.cells.get_data( variables=["spikes"] )
        
        
            - It should be noted that the above ``allspikes`` object is the `Neo Block <https://neo.readthedocs.io/en/latest/api_reference.html#neo.core.Block>`_
            - It is a Neo Block with only one `Segment <https://neo.readthedocs.io/en/latest/api_reference.html#neo.core.Segment>`_
        
        * Therefore,
        
            - Spike trains for all the neuron units in the cell assembly for the base unit "animal" would be.
            
                * ``allspikes.segments[0].spiketrains[0]``
                * That is, spike trains from all the ten neuron units in this cell assembly.
            
            - Similarly, for "mammal", "bird", and "canary" are respectively
            
                * ``allspikes.segments[0].spiketrains[0]``
                * ``allspikes.segments[0].spiketrains[1]``
                * ``allspikes.segments[0].spiketrains[2]``
        
        """
        self.numCAs = inheritanceStructure.numberUnits 
        numberNeurons = self.numCAs * self.neuronsPerCA
        self.createNeurons(numberNeurons)
        self.setRecord()
        self.makeCAs()
        self.makeHiersFromHier(inheritanceStructure)

    #---Test code.
    #Set up spike generators to start each unit, then stop them.
    #When run, each unit should persist, but only that unit 
    #should.
    def makeGenerator(self,genTime):
        """Set up spike generator to start each unit. ``genTime`` is a float representing the start time."""
        genTimes = genTime
        genTimeArray = {'spike_times': [genTimes]}
        spikeGen=self.sim.Population(1,self.sim.SpikeSourceArray,genTimeArray)
        return spikeGen

    #now stop all of the units after each individual unit is tested.
    def createStopAll(self,stopTimes):
        """Stop all the spikes generated, **each** generated using :py:meth:`.makeGenerator`."""
        stopTimeArray = {'spike_times': [stopTimes]}
        stopSpikeGen=self.sim.Population(1,self.sim.SpikeSourceArray,
                                         stopTimeArray)
        for unit in range (0,self.numCAs): #numCAs is numUnits
            self.fsa.turnOffStateFromSpikeSource(stopSpikeGen,self.cells,unit)

    def createTestAllUnits(self,firstTestStart):
        """The state for every cell assembly in the hierarchy topology is turned on.
        The method returns the time after turning on the state for the last cell assembly.
        """
        oneTestDuration = 100.0
        stopTimes = []
        for unit in range (0,self.numCAs): #numCAs is numUnits
            startTime = 25.0 + (unit*oneTestDuration)+firstTestStart
            generator = self.makeGenerator([startTime])
            self.fsa.turnOnStateFromSpikeSource(generator,self.cells,unit)
            lastTime =(((unit+1)*oneTestDuration)+firstTestStart)
            stopTimes = stopTimes + [lastTime]

        self.createStopAll(stopTimes)
        return lastTime

    #Create a spikeGen that primes all of the units numTests times.
    #Connect it to all of the units.
    def createTestPrimeAllUnits(self,firstTestStart,numTests):
        """Legacy."""
        oneTestDuration = 100.0
        timeBetweenSteps = 5.0
        numberPrimeSteps = 10
        for primeEpoch in range (0,self.numCAs): #numCAs is numUnits
            startTime = 25.0 + (primeEpoch*oneTestDuration)+firstTestStart
            primeTimes = []
            for primeStep in range (0,numberPrimeSteps): 
                primeTimes = primeTimes + [startTime + 
                                           (timeBetweenSteps*primeStep)]
            generator = self.makeGenerator(primeTimes)

            #self.connectGeneratorToPrimeUnit(generator,unit)
            for unit in range (0,self.numCAs): #numCAs is numUnits
                self.fsa.stimulateStateFromSpikeSource(generator,self.cells,
                                                       unit,self.primeWeight)
        return firstTestStart + (self.numCAs*oneTestDuration)

    #Create spikeGens and synapses to connect all the units
    #to be tested, and to spread up the hierarchy.
    def createTestAllInheritanceUnits(self,firstTestStart):
        """Legacy."""
        testFullTime = self.createTestPrimeAllUnits(firstTestStart,self.numCAs)
        #this assumes that both of the functions have the same testduration.
        otherTestFullTime = self.createTestAllUnits(firstTestStart)
        print("bob", testFullTime, otherTestFullTime)
        return otherTestFullTime

    #This is a test to see if some neurons are firing.
    def createSimpleTest(self):
        """Legacy."""
        primeTimes = [5]
        primeArray = {'spike_times': [primeTimes]}
        generator=self.sim.Population(1,self.sim.SpikeSourceArray,primeArray)

        self.fsa.turnOnStateFromSpikeSource(generator,self.cells,0)

    #def printInheritanceHier(self,fileName):
    #    """Legacy."""
    #    self.cells.write_data(fileName) #self.cells.printSpikes(fileName) depreciated

    

