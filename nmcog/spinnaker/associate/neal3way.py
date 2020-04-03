# =============================================================================
# ~/spinnaker/associate/neal3way.py
#
# created January 2020 Lungsi
#
# =============================================================================
from types import SimpleNamespace as structdata

import spynnaker8 as sim

from .nealassoc.readInheritanceFile import InheritanceReaderClass
from .nealassoc.readUnitFile import UnitReaderClass
#from readAssocFile import AssocReaderClass
from .nealassoc.make3Assoc import NeuralThreeAssocClass
from nmcog.spinnaker.specialfunction.neal import NealCoverFunctions

class NEAL3Way(object):
    """Neuromorphic Embodied Agents that Learn `(NEAL) <http://www.cwa.mdx.ac.uk/NEAL/NEAL.html>`_ based three-way association function.
    
    Example
    
    ::
    
        bases = {"units": ["animal", "mammal", "bird", "canary"],
                 "relations": [ ["canary", "bird"], ["bird", "animal"], ["mammal", "animal"] ]}
        associate = {"properties": ["food", "fur", "flying", "yellow"], # properties to be associated between base units and its relations
                     "relations": ["eats", "likes", "travels", "has", "colored"], # relations associated with properties and base units
                     "connections": [ ["animal", "eats", "food"], ["mammal", "has", "fur"], # specific combos of base-props-relations
                                      ["bird", "travels", "flying"], ["canary", "colored", "yellow"]] }
    
    **Note:**
    
    * Specifically the instance of :ref:`InheritanceReaderClass` is the base data for :ref:`NEAL3Way`. An example base data is
    
    
    Considering the above example whose base data is the instance such that,
        
    ::
    
        >>> print(basedata.units)
        ["animal", "mammal", "bird", "canary"]
        
           
    Since there are four association units in the base data, four cell assemblies will be created.
    
    ::
    
             CA for animal            CA for mammal              CA for bird              CA for canary
        ooooooooooooooooooooooo   ooooooooooooooooooooooo   ooooooooooooooooooooooo   ooooooooooooooooooooooo
        o                     o   o                     o   o                     o   o                     o
        o (0) (2) (4) (6) (8) o   o (0) (2) (4) (6) (8) o   o (0) (2) (4) (6) (8) o   o (0) (2) (4) (6) (8) o
        o                     o   o                     o   o                     o   o                     o
        o (1) (3) (5) (7) (9) o   o (1) (3) (5) (7) (9) o   o (1) (3) (5) (7) (9) o   o (1) (3) (5) (7) (9) o
        o                     o   o                     o   o                     o   o                     o
        ooooooooooooooooooooooo   ooooooooooooooooooooooo   ooooooooooooooooooooooo   ooooooooooooooooooooooo
    
    
    * Refer to :ref:`FSAHelperFunctions` ``.makeCA`` about the structure of a cell assembly based on the Neuromorphic Embodied Agents that Learn `(NEAL) <http://www.cwa.mdx.ac.uk/NEAL/NEAL.html>`_.
    * Refer to :ref:`FSAHelperFunctions` ``.getCAConnectors`` for details on how the `neuron populations <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly are connected.
    
    Connection (excitatory) between the cell assemblies is based on the "isA" relationship pair.
    
    ::
    
        >>> print(basedata.isARelationships)
        [ ["canary", "bird"], ["bird", "animal"], ["mammal", "animal"] ]
    
    
    Therefore a hierarchy topology will be created
    
    ::
    
             ;;;;;;;;;;;;;;;;;;;;;;;;;;              ;;;;;;;;;;;;;;;;;;;;;;;;;;
             ;;;;;;;;;;;;;;;;;;;;;;;;;;              ;;;;;;;;;;;;;;;;;;;;;;;;;;
           ..;;;;;..              ;;;;;            ..;;;;;..              ;;;;;
             ':::'                ;;;;;              ':::'                ;;;;;
              ':'                 ;;;;;               ':'                 ;;;;;
        ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo
        o               o   o               o   o               o   o               o
        o CA for animal o   o CA for mammal o   o  CA for bird  o   o CA for canary o
        o               o   o               o   o               o   o               o
        ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo
               .                                     ;;;;;
             .:;:.                                   ;;;;;
           .:;;;;;:.                                 ;;;;;
             ;;;;;                                   ;;;;;
             ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
             ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    
    This hierarchy topology is also refered to a the network of the association units in the base data.
    
    * Refer to :ref:`NeuralInheritanceClass` ``.makeHiersFromHier`` for how the excitatory connections among the assembly of association units are made.
    
    Since,
    
    ::
    
        >>> print(propdata.units)
        ["food", "fur", "flying", "yellow"]
        
        >>> print(reldata.units)
        ["eats", "likes", "travels", "has", "colored"]
    
    
    The association topology is
    
    ::
    
        oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
        o                o   o                o   o                o   o                o
        o  CA for food   o   o   CA for fur   o   o CA for flying  o   o CA for yellow  o
        o                o   o                o   o                o   o                o
        oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
        
        oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
        o                o   o                o   o                o   o                o   o                o
        o  CA for eats   o   o  CA for likes  o   o CA for travels o   o   CA for has   o   o CA for colored o
        o                o   o                o   o                o   o                o   o                o
        oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
    
    
    Given an association tuple (list of three strings representing base, relation, and property),
    
    ::
    
        >>> print(assocdata.assocs)
        [ ["animal", "eats", "food"], ["mammal", "has", "fur"], ["bird", "travels", "flying"], ["canary", "colored", "yellow"] ]
    
    
    * The hierarchy topology to the cell assemblies for property.
    * The hierarchy topology to the cell assemblies for relation.
    * The cell assemblies for property to the hierarchy topology.
    * The cell assemblies for property to the cell assemblies for relation.
    * The cell assemblies for relation to the hierarchy topology.
    * The cell assemblies for relation to the cell assemblies for property.
    
    For illustration below shows only for `[ ["animal", "eats", "food"], ["canary", "colored", "yellow"] ]`
    
    ::
    
                           ;;;;;;;;;;;;;;;;;;;;;;                   ;;;;;;;;;;;;;;;;;;;;;;
                           \/                  ;;                   \/                  ;;
               .    ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo    .
        .......;;.  o               o   o               o   o               o   o               o  .;;..............
        ;;;::::;;;;.o CA for animal o   o CA for mammal o   o  CA for bird  o   o CA for canary o.;;;;:::::::::::;;;
        ;;;::::;;:' o               o   o               o   o               o   o               o ':;;:::::::::::;;;
        ;;;    :'   ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo   ':           ;;;
        ;;;                /\                                       ;;                                           ;;;
        ;;;                ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;                                           ;;;
        ;;;                                                                                                      ;;;
        ;;;    .    oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo    .       ;;;
        ;;;....;;.  o                o   o                o   o                o   o                o  .;;.......;;;
        ;;;::::;;;;.o  CA for food   o   o   CA for fur   o   o CA for flying  o   o CA for yellow  o.;;;;:::::::;;;
        ;;;::::;;:' o                o   o                o   o                o   o                o ':;;::::::;;;;;
        ;;;    :'   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   ':     ':::::'
        ;;;                                                                                                      ':'
        ;;;    .    oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
        ;;;....;;.  o                o   o                o   o                o   o                o   o                o
        ;;;::::;;;;.o  CA for eats   o   o  CA for likes  o   o CA for travels o   o   CA for has   o   o CA for colored o
        ;;;::::;;:' o                o   o                o   o                o   o                o   o                o
               :'   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
    
    
    """
    
    def __init__(self, bases, associate, turnon="all"):
        # bases = {"units": ["animal", "mammal", "bird", "canary"],
        #          "relations": [ ["canary", "bird"], ["bird", "animal"], ["mammal", "animal"] ]}
        # associate = {"properties": ["food", "fur", "flying", "yellow"], # properties to be associated between base units and its relations
        #              "relations": ["eats", "likes", "travels", "has", "colored"], # relations associated with properties and base units
        #              "connections": [ ["animal", "eats", "food"], ["mammal", "has", "fur"], # specific combos of base-props-relations
        #                               ["bird", "travels", "flying"], ["canary", "colored", "yellow"] ] }
        neal = NealCoverFunctions()
        sim.setup(timestep=neal.DELAY, min_delay=neal.DELAY, max_delay=neal.DELAY, debug=0)
        #
        self.__create_datastructures(bases, associate)
        self.__create_network()
        self.__choose_applicable_test( turnon )
        #
        neal.nealApplyProjections()
        sim.run(self.simTime)
        [neo_base, neo_property, neo_relation] = self.__getdata()
        self.results = { "base": self.__split_spiketrains("basedata", neo_base),
                         "property": self.__split_spiketrains("propdata", neo_property),
                         "relation": self.__split_spiketrains("reldata", neo_relation) }
        sim.end()
        
    def get_results(self):
        """Returns a dictionary with keys "base", "property", and "relation" whose values are dictionaries.
        A value dictionary is such that the keys are the names of the cell assemblies (i.e. "units" in respective structured data)
        and values are the respective spike trains (i.e. from all cell units in an assembly).
        """
        return self.results
        
    def __create_datastructures(self, bases, associate):
        """."""
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
        
    def __create_network(self):
        """Moved to main description."""
        self.neural3assoc_topology = NeuralThreeAssocClass()
        self.neural3assoc_topology.createBaseNet( self.basedata )
        self.neural3assoc_topology.createAssociationTopology( self.propdata, self.reldata )
        self.neural3assoc_topology.addAssociations( self.assocdata )
        
    def __choose_applicable_test(self, turnon):
        """."""
        if turnon=="all":
            self.simTime = self.neural3assoc_topology.createUnitTests() + 100
        else:
            baseNum = self.basedata.getUnitNumber( turnon[0] )
            probNum = self.propdata.getUnitNumber( turnon[1] )
            relNum = self.reldata.getUnitNumber( turnon[2] )
            self.neural3assoc_topology.createTwoPrimeTest( baseNum, probNum, relNum )
            self.simTime = 200.0
    
    # Private function for getting Neo object for all the created cell assemblies.
    def __getdata(self):
        """Gets the recorded `Neo <https://neo.readthedocs.io/en/latest/>`_ objects."""
        neo_base = self.neural3assoc_topology.neuralHierarchyTopology.cells.get_data(variables=["spikes"])
        neo_property = self.neural3assoc_topology.propertyCells.get_data(variables=["spikes"])
        neo_relation = self.neural3assoc_topology.relationCells.get_data(variables=["spikes"])
        return [neo_base, neo_property, neo_relation]
    
    # Private function for segregating respective spike trains for each cell assembly within a Neo object.
    def __split_spiketrains(self, dataname, neo_data):
        """Given the Neo object of a given data name ("basedata" or "propdata" or "reldata", see :py:meth:`.__create_datastructures`),
        this function returns a dictionary with "units" in the structured data as keys and its value the respective spike trains (all cell units in an assembly, i.e. the "unit").
        """
        ca_size = self.neural3assoc_topology.fsa.CA_SIZE
        #
        spkindices = lambda n : (0,ca_size) if (n==0) else ( (n*ca_size), (n*ca_size)+ca_size )
        #
        data = getattr(self, dataname) # "basedata" or "propdata" or "reldata"
        overallspikes = neo_data.segments[0].spiketrains
        #
        parsed_spiketrains = {"all": overallspikes} # this will be the returned value
        for unit in data.units:
            n = data.getUnitNumber(unit)
            indx = spkindices(n)
            parsed_spiketrains.update( {unit: overallspikes[ indx[0] : indx[-1] ] } )
        return parsed_spiketrains
