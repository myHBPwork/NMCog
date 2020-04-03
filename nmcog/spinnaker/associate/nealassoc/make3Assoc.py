# ~/nmcog/spinnaker/associate/nealassoc/make3Assoc.py
#
# Documentation by Lungsi 24 March 2020
#
# Code based on Jan2020 Chris Huyck et al.
# http://www.cwa.mdx.ac.uk/NEAL/code/assocMemJan2020.tar.gz
#
# This creates a three way association topology.  One of the types
# is the base type (typically a node in a semantic net).  The other
# two are the same but one is named relation and the other property.
# If you turn two on, the third should come on.  You should also be
# able to get the (base) to spread up the inheritance hierarchy.
#
# Testing is weak.  It has only been tested in nest.

from nmcog.spinnaker.specialfunction.neal import FSAHelperFunctions
from .makeInheritanceHier import NeuralInheritanceClass

# added for nmcog
import spynnaker8 as sim
from nmcog.spinnaker.specialfunction.neal import NealCoverFunctions

class NeuralThreeAssocClass:
    """
    
    +---------------------------------------+------------------------------------------------+----------------------------------------------+
    | Methods                               |  Argument                                      | Caller                                       |
    +=======================================+================================================+==============================================+
    | :py:meth:`.createBaseNet`             | - instance of :ref:`InheritanceReaderClass`    | :ref:`NEAL3Way`                              |
    +---------------------------------------+------------------------------------------------+----------------------------------------------+
    | :py:meth:`.createAssociationTopology` | - instance of :ref:`UnitReaderClass`           | :ref:`NEAL3Way`                              |
    |                                       | - different instance of :ref:`UnitReaderClass` |                                              |
    +---------------------------------------+------------------------------------------------+----------------------------------------------+
    | :py:meth:`.addAssociations`           | - a structured data                            | :ref:`NEAL3Way`                              |
    +---------------------------------------+------------------------------------------------+----------------------------------------------+
    
    
    **Note:**
    
    * Specifically the instance of :ref:`InheritanceReaderClass` is the base data for :ref:`NEAL3Way`. An example base data is
    
    ::
    
        bases = {"units": ["animal", "mammal", "bird", "canary"],
                 "relations": [ ["canary", "bird"], ["bird", "animal"], ["mammal", "animal"] ]}
        associate = {"properties": ["food", "fur", "flying", "yellow"], # properties to be associated between base units and its relations
                     "relations": ["eats", "likes", "travels", "has", "colored"], # relations associated with properties and base units
                     "connections": [ ["animal", "eats", "food"], ["mammal", "has", "fur"], # specific combos of base-props-relations
                                      ["bird", "travels", "flying"], ["canary", "colored", "yellow"]] }
    
    
    """
    #class variables
    numPropertyCAs = -1
    numRelationshipCAs = -1
    neuralHierarchyTopology = None
    baseStructure = None
    propStructure = None
    relStructure = None

    #def __init__(self, simName,sim,neal,spinnVersion,fsa):
    def __init__(self, simName="spinnaker", spinnVersion=8): # modified for nmcog
        self.simName = simName
        self.sim = sim
        self.spinnVersion = spinnVersion
        self.neal = NealCoverFunctions()
        self.fsa = FSAHelperFunctions()

    def createNeurons(self,numPropertyNeurons,numRelationNeurons):
        """Creates a two population (``propertyCells`` and ``relationCells``) of `IF_cond_exp <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_ neurons with :ref:`FSAHelperFunctions` ``.CELL_PARAMS``."""
        self.propertyCells = self.sim.Population(numPropertyNeurons,
                    self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.relationCells = self.sim.Population(numRelationNeurons,
                    self.sim.IF_cond_exp, self.fsa.CELL_PARAMS)

    def setRecord(self):
        """Records spikes of all the neurons in the ``propertyCells`` and ``relationCells`` populations created via :py:meth:`.createNeurons`."""
        self.propertyCells.record(['spikes'])
        self.relationCells.record(['spikes'])

    #Make a binary CA for each unit
    def makeCAs(self):
        """Makes ``numCAs`` assemblies of cell, i.e. connect neurons in the two population created via :py:meth:`.createNeurons`.
        
        * ``numPropertyCAs`` assemblies of ``propertyCells``
        * ``numRelationCAs`` assemblies of ``relationCells``
        
        Like the "hierarchy topology" created with :ref:`NeuralInheritanceClass` ``.createNeuralInheritanceHierarchy`` the practical meaning of the cell assemblies of "property" and "relations" in terms of extracting/visualizing the neuron units in a population is as follows.
        
        * For our example of four property units ``["food", "fur", "flying", "yellow"]`` there will be four cell assemblies for "property".
        * For our example of four relation units ``["eats", "likes", "travels", "has", "colored"]`` there will be five cell assemblies for "relation".
        * By default :ref:`FSAHelperFunctions` ``.CA_SIZE`` = 10, which is the number of neuron units in each assembly.
        
            - This is done by invoking :py:meth:`createNeurons`
            - The result is ``self.propertyCells`` and ``self.relationCells``
            
        * After simulating for a particular runtime, spikes from all the neurons (i.e. all neuron units in all the neuronal populations in all the assemblies) by
        
        ::
        
            allpropertyspikes = self.propertyCells.get_data( variables=["spikes"] )
            allrelationspikes = self.relationCells.get_data( variables=["spikes"] )
        
        
            - It should be noted that the above objects are `Neo Blocks <https://neo.readthedocs.io/en/latest/api_reference.html#neo.core.Block>`_
            - It is a Neo Block with only one `Segment <https://neo.readthedocs.io/en/latest/api_reference.html#neo.core.Segment>`_
        
        * Therefore,
        
            - Spike trains for all the neuron units in the cell assembly for the property units "food", "fur", "flying", and "yellow" are respectively
            
                * ``allpropertyspikes.segments[0].spiketrains[0]`` for "food"
                * ``allpropertyspikes.segments[0].spiketrains[1]`` for "fur"
                * ``allpropertyspikes.segments[0].spiketrains[2]`` for "flying"
                * ``allpropertyspikes.segments[0].spiketrains[3]`` for "yellow"
            
            - Similarly, for the relation units "eats", "likes", "travels", "has", and "colored" are respectively
            
                * ``allrelationspikes.segments[0].spiketrains[0]`` for "eats"
                * ``allrelationspikes.segments[0].spiketrains[1]`` for "likes"
                * ``allrelationspikes.segments[0].spiketrains[2]`` for "travels"
                * ``allrelationspikes.segments[0].spiketrains[3]`` for "has"
                * ``allrelationspikes.segments[0].spiketrains[4]`` for "colored"
        
        """
        for CA in range (0,self.numPropertyCAs):
            self.fsa.makeCA(self.propertyCells,CA)
        for CA in range (0,self.numRelationCAs):
            self.fsa.makeCA(self.relationCells,CA)
    
    #main function
    def createBaseNet(self,baseNodeStructure):
        """Creates a hierarchy topology for base data. See :ref:`NeuralInheritanceClass.createNeuralInheritanceHierarchy` to know more about hierarchy topology."""
        self.baseStructure = baseNodeStructure
        #self.neuralHierarchyTopology = NeuralInheritanceClass(self.simName,
        #        self.sim,self.neal,self.spinnVersion,self.fsa)
        self.neuralHierarchyTopology = NeuralInheritanceClass() # modified for nmcog
        self.neuralHierarchyTopology.createNeuralInheritanceHierarchy(baseNodeStructure)

    def createAssociationTopology(self,propertyStructure,relationStructure):
        """Given two instances of :ref:`UnitReaderClass` this method creates cell assemblies (:py:meth:`.makeCAs`) based on the two neuron populations (:py:meth:`.createNeurons`)."""
        self.propStructure = propertyStructure
        self.relStructure = relationStructure
        self.numPropertyCAs = propertyStructure.numberUnits 
        numberPropertyNeurons = self.numPropertyCAs * self.fsa.CA_SIZE
        self.numRelationCAs = relationStructure.numberUnits 
        numberRelationNeurons = self.numRelationCAs * self.fsa.CA_SIZE
        self.createNeurons(numberPropertyNeurons,numberRelationNeurons)
        self.setRecord()
        self.makeCAs()

    #Add synapses that make a 2/3 CA.
    def addThreeAssoc(self,assocTuple):
        """Given an association tuple (list of three strings representing base, relation, and property) this method connects
        
        * The hierarchy topology to the cell assemblies for property.
        * The hierarchy topology to the cell assemblies for relation.
        * The cell assemblies for property to the hierarchy topology.
        * The cell assemblies for property to the cell assemblies for relation.
        * The cell assemblies for relation to the hierarchy topology.
        * The cell assemblies for relation to the cell assemblies for property.
        
        """
        base = assocTuple[0]
        relation = assocTuple[1]
        property = assocTuple[2]
        baseNum = self.baseStructure.getUnitNumber(base)
        propertyNum = self.propStructure.getUnitNumber(property)
        relationNum = self.relStructure.getUnitNumber(relation)
        #print(assocTuple)
        #print(type(base),  base)
        self.fsa.stateHalfTurnsOnState(self.neuralHierarchyTopology.cells,
                                       baseNum,self.propertyCells,propertyNum)
        self.fsa.stateHalfTurnsOnState(self.neuralHierarchyTopology.cells,
                                       baseNum,self.relationCells,relationNum)

        self.fsa.stateHalfTurnsOnState(self.propertyCells,propertyNum,
                                self.neuralHierarchyTopology.cells,baseNum)
        self.fsa.stateHalfTurnsOnState(self.propertyCells,propertyNum,
                                       self.relationCells,relationNum)

        self.fsa.stateHalfTurnsOnState(self.relationCells,relationNum,
                                self.neuralHierarchyTopology.cells,baseNum)
        self.fsa.stateHalfTurnsOnState(self.relationCells,relationNum,
                                       self.propertyCells,propertyNum)

    def addAssociations(self,assocStructure):
        """Add associations for each tuple in a data structure of associations by calling :py:meth:`.addThreeAssoc` for each association."""
        #print(assocStructure.numberAssocs)
        for assocNum in range (0,assocStructure.numberAssocs):
            self.addThreeAssoc(assocStructure.assocs[assocNum])


    #-print function
    #def printSpikes(self):
    #    """."""
    #    self.propertyCells.write_data("testProps.pkl")
    #    self.relationCells.write_data("testRels.pkl")
    #    self.neuralHierarchyTopology.cells.write_data("test3.pkl")


    def printPklSpikes(self,inFileName,outFileName):
        """Legacy."""
        outFileHandle = open(outFileName,'w')
        inFileHandle = open(inFileName)
        neoObj = pickle.load(inFileHandle)
        segments = neoObj.segments
        segment = segments[0]
        spikeTrains = segment.spiketrains
        neurons = len(spikeTrains)
        for neuronNum in range (0,neurons):
            if (len(spikeTrains[neuronNum])>0):
                spikes = spikeTrains[neuronNum]
                for spike in range (0,len(spikes)):
                    #outFileHandle.print(neuronNum, spikes[spike])
                    outString = str(neuronNum) + " " + str(spikes[spike]) +"\n";
                    outFileHandle.write(outString)
        inFileHandle.close()
        outFileHandle.flush()
        outFileHandle.close()

    def printSpikes(self,fileName):
        """."""
        # Commented out for nmcog
        #if ((self.simName =="spinnaker") and (self.spinnVersion == 7)):
        #    suffix = ".sp"
        #elif ((self.simName =="nest") or
        #      ((self.simName =="spinnaker") and (self.spinnVersion == 8))):
        #    suffix = ".pkl"
        suffix = ".pkl"
        basePklFile = "results/"+fileName +"Bases" + suffix
        #baseSpFile = "results/"+fileName +"Bases.sp"
        self.neuralHierarchyTopology.cells.write_data(basePklFile)
        #self.printPklSpikes(basePklFile,baseSpFile)
        propPklFile = "results/"+fileName +"Props"+ suffix
        self.propertyCells.write_data(propPklFile)
        relPklFile = "results/"+fileName +"Rels"+ suffix
        #self.relationCells.printSpikes(relPklFile)
        self.relationCells.write_data(relPklFile)

    #--test functions
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
    def createStopAll(self,stopTimes,cells,numUnits):
        """Stop all the spikes generated, **each** generated using :py:meth:`.makeGenerator`."""
        stopTimeArray = {'spike_times': [stopTimes]}
        stopSpikeGen=self.sim.Population(1,self.sim.SpikeSourceArray,
                                         stopTimeArray)
        for unit in range (0,numUnits): 
            self.fsa.turnOffStateFromSpikeSource(stopSpikeGen,cells,unit)

    def createSimpleTest(self):
        """Legacy."""
        primeTimes = [5]
        primeArray = {'spike_times': [primeTimes]}
        generator=sim.Population(1,sim.SpikeSourceArray,primeArray)
        
        self.fsa.turnOnStateFromSpikeSource(generator,self.propertyCells,1)
        self.fsa.turnOnStateFromSpikeSource(generator,self.relationCells,2)
        self.neuralHierarchyTopology.createSimpleTest()

    #call this with 0-3 items to be stimulated (but typically two)
    def createTwoTest(self,baseNum,propNum,relNum):
        """Legacy."""
        primeTimes = [5]
        primeArray = {'spike_times': [primeTimes]}
        generator=self.sim.Population(1,self.sim.SpikeSourceArray,primeArray)
        
        if (baseNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,
                        self.neuralHierarchyTopology.cells,baseNum)
        if (propNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,self.propertyCells,
                                                propNum)
        if (relNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,self.relationCells,
                                                relNum)

    def createTestPrimeAllBaseUnits(self,firstTestStart,hierarchy):
        """."""
        primeWeight = 0.014#0.017
        oneTestDuration = 100.0
        timeBetweenSteps = 5.0
        numberPrimeSteps = 10
        for primeEpoch in range (0,hierarchy.numCAs): 
            startTime = 25.0 + (primeEpoch*oneTestDuration)+firstTestStart
            primeTimes = []
            for primeStep in range (0,numberPrimeSteps): 
                primeTimes = primeTimes + [startTime + 
                                           (timeBetweenSteps*primeStep)]
            generator = self.makeGenerator(primeTimes)

            for unit in range (0,hierarchy.numCAs): #numCAs is numUnits
                self.fsa.stimulateStateFromSpikeSource(generator,hierarchy.cells,
                                                       unit,primeWeight)
        return firstTestStart + (hierarchy.numCAs*oneTestDuration)

    #call this with 0-3 items to be stimulated (but typically two)
    def createTwoPrimeTest(self,baseNum,propNum,relNum):
        """."""
        primeTimes = [5]
        primeArray = {'spike_times': [primeTimes]}
        generator=self.sim.Population(1,self.sim.SpikeSourceArray,primeArray)
        
        if (baseNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,
                        self.neuralHierarchyTopology.cells,baseNum)
            self.createTestPrimeAllBaseUnits(5.0,self.neuralHierarchyTopology)

        if (propNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,self.propertyCells,
                                                propNum)
        if (relNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,self.relationCells,
                                                relNum)

    #call this with 0-3 items to be stimulated (but typically two) 
    def createTwoPrimeTestPoisson(self,baseNum,propNum,relNum):
        """Legacy."""
        PoissonParameters = {'duration': 200.0, 'start': 0.0, 'rate': 200.0} # rate = 200 Hz  
        generator=self.sim.Population(1,self.sim.SpikeSourcePoisson,PoissonParameters)
        
        if (baseNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,
                        self.neuralHierarchyTopology.cells,baseNum)
            self.createTestPrimeAllBaseUnits(5.0,self.neuralHierarchyTopology)

        if (propNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,self.propertyCells,
                                                propNum)
        if (relNum >= 0):
            self.fsa.turnOnStateFromSpikeSource(generator,self.relationCells,
                                                relNum)

    def createTestAllUnits(self,firstTestStart,cells,numUnits):
        """Given a start time ``firstTestStart``, the state for ``numUnits`` cell assemblies of a neuron population (``cells``) is turned on.
        The method returns the time after turning on the state for the last cell assembly.
        """
        #print(numUnits)
        oneTestDuration = 100.0
        stopTimes = []
        for unit in range (0,numUnits): 
            startTime = 25.0 + (unit*oneTestDuration)+firstTestStart
            generator = self.makeGenerator([startTime])
            self.fsa.turnOnStateFromSpikeSource(generator,cells,unit)
            lastTime =(((unit+1)*oneTestDuration)+firstTestStart)
            stopTimes = stopTimes + [lastTime]

        #print(stopTimes)
        self.createStopAll(stopTimes,cells,numUnits)
        return lastTime

    def createUnitTests(self):
        """Turns on the state for every cell assembly in
        
        * The hierarchy topology (base data)
        * The populations for ``propertyCells`` and ``relationCells``.
        
        """
        baseUnitTime = self.neuralHierarchyTopology.createTestAllUnits(0.0)
        propUnitTime = self.createTestAllUnits(baseUnitTime,self.propertyCells,
                                               self.numPropertyCAs)
        relUnitTime = self.createTestAllUnits(propUnitTime,self.relationCells,
                                               self.numRelationCAs)
        #print(baseUnitTime,propUnitTime,relUnitTime)
        return relUnitTime
