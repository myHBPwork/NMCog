from types import SimpleNamespace as structdata

import spynnaker8 as sim

from .nealassoc.readInheritanceFile import InheritanceReaderClass
from .nealassoc.readUnitFile import UnitReaderClass
#from readAssocFile import AssocReaderClass
from .nealassoc.make3Assoc import NeuralThreeAssocClass
from nmcog.spinnaker.specialfunctions.neal.nealCoverClass import NealCoverFunctions

class NEAL3Way(object):
    
    def __init__(self, bases, associate, turnon="all"):
        # bases = {"units": ["animal", "mammal", "bird", "canary"],
        #          "relations": [ ["canary", "bird"], ["bird", "animal"], ["mammal", "animal"] ]}
        # associate = {"properties": ["food", "fur", "flying", "yellow"], # properties to be associated between base units and its relations
        #              "relations": ["eats", "likes", "travels", "has", "colored"], # relations associated with properties and base units
        #              "connections": [ ["animal", "eats", "food"], ["mammal", "has", "fur"], # specific combos of base-props-relations
        #                               ["bird", "travels", "flying"], ["canary", "colored", "yellow"]] }
        neal = NealCoverFunctions()
        sim.setup(timestep=neal.DELAY, min_delay=neal.DELAY, max_delay=neal.DELAY, debug=0)
        #
        self._create_datastructures(bases, associate)
        self._create_network()
        self._choose_applicable_test( turnon )
        #
        neal.nealApplyProjections()
        sim.run(self.simTime)
        
    def _create_datastructures(self, bases, associate):
        #self.basedata = structdata()
        self.basedata = InheritanceReaderClass()
        self.basedata.numberUnits = len(bases["units"])
        self.basedata.units = bases["units"]
        self.basedata.isARelationships = bases["relations"]
        #self.basedata.getUnitNumber = lambda checkUnit: [ resultUnit for resultUnit in range(0, self.basedata.numberUnits)
        #                                                              if checkUnit==self.basedata.units[resultUnit] ][0]
        #self.propdata = structdata()
        self.propdata = UnitReaderClass()
        self.propdata.numberUnits = len(associate["properties"])
        self.propdata.units = associate["properties"]
        #self.propdata.getUnitNumber = lambda checkUnit: [ resultUnit for resultUnit in range(0, self.propdata.numberUnits)
        #                                                              if checkUnit==self.propdata.units[resultUnit] ][0]
        #self.reldata = structdata()
        self.reldata = UnitReaderClass()
        self.reldata.numberUnits = len(associate["relations"])
        self.reldata.units = associate["relations"]
        #self.reldata.getUnitNumber = lambda checkUnit: [ resultUnit for resultUnit in range(0, self.reldata.numberUnits)
        #                                                              if checkUnit==self.reldata.units[resultUnit] ][0]
        self.assocdata = structdata() #AssocReaderClass()
        self.assocdata.numberAssocs = len(associate["connections"])
        self.assocdata.assocs = associate["connections"]
        
    def _create_network(self):
        self.neural3assoc_topology = NeuralThreeAssocClass()
        self.neural3assoc_topology.createBaseNet( self.basedata )
        self.neural3assoc_topology.createAssociationTopology( self.propdata, self.reldata )
        self.neural3assoc_topology.addAssociations( self.assocdata )
        
    def _choose_applicable_test(self, turnon):
        if turnon=="all":
            self.simTime = self.neural3assoc_topology.createUnitTests() + 100
        else:
            baseNum = self.basedata.getUnitNumber( turnon[0] )
            probNum = self.propdata.getUnitNumber( turnon[1] )
            relNum = self.reldata.getUnitNumber( turnon[2] )
            self.neural3assoc_topology.createTwoPrimeTest( baseNum, probNum, relNum )
            self.simTime = 200.0
