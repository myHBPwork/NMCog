# =============================================================================
# ~/spinnaker/associate/neal3way.py
#
# created January 2020 Lungsi
#
# =============================================================================
from types import SimpleNamespace as structdata

import spynnaker8 as sim

import quantities as pq
# for plotting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import gridspec
from matplotlib import cm

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
    * Refer to :ref:`FSAHelperFunctions` ``.getCAConnectors`` for details on how the cell units in the `neuron population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly are connected.
    
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
    
    def __init__(self, bases, associate, turnon="all", twotest=None):
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
        self.__choose_applicable_test( turnon, twotest )
        #
        neal.nealApplyProjections()
        sim.run(self.simTime)
        [neo_base, neo_property, neo_relation] = self.__getdata()
        self.results = { "base": self.__split_spiketrains("basedata", neo_base, turnon),
                         "property": self.__split_spiketrains("propdata", neo_property, turnon),
                         "relation": self.__split_spiketrains("reldata", neo_relation, turnon) }
        #sim.reset()
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
        
    def __choose_applicable_test(self, turnon, twotest=None):
        """If ``turnon = "all"`` then all the cell assemblies for each subject (base), object (property) and relation (predicate) is activated.
        On the other hand, if ``turnon = [<subject-name>, <predicate-name>, <object-name>]`` only cell assemblies for these are trigerred."""
        if turnon=="all":
            self.simTime = self.neural3assoc_topology.createUnitTests() + 100
            self.test_metadata = [turnon, twotest]
        elif (turnon!="all" and twotest=="prime"):
            baseNum = self.__check_and_returnUnitNumber( self.basedata, turnon, 0 ) # base or subject
            probNum = self.__check_and_returnUnitNumber( self.propdata, turnon, 1 ) # property or object
            relNum = self.__check_and_returnUnitNumber( self.reldata, turnon, 2 ) # relation or predicate
            self.neural3assoc_topology.createTwoPrimeTest( baseNum, probNum, relNum )
            self.simTime = 200.0
            self.test_metadata = [None, "prime"]
        elif (turnon!="all" and twotest is None):
            baseNum = self.__check_and_returnUnitNumber( self.basedata, turnon, 0 ) # base or subject
            probNum = self.__check_and_returnUnitNumber( self.propdata, turnon, 1 ) # property or object
            relNum = self.__check_and_returnUnitNumber( self.reldata, turnon, 2 ) # relation or predicate
            self.neural3assoc_topology.createTwoTest( baseNum, probNum, relNum )
            self.simTime = 200.0
            self.test_metadata = [None, None]
    
    # Private function for returning a unit number for respective structured data
    def __check_and_returnUnitNumber(self, strdata, turnon, indx):
        try:
            someNum = strdata.getUnitNumber( turnon[indx] )
        except:
            someNum = -1 # cell assembly will not be activated
        return someNum
    
    # Private function for getting Neo object for all the created cell assemblies.
    def __getdata(self):
        """Gets the recorded `Neo <https://neo.readthedocs.io/en/latest/>`_ objects."""
        neo_base = self.neural3assoc_topology.neuralHierarchyTopology.cells.get_data(variables=["spikes"])
        neo_property = self.neural3assoc_topology.propertyCells.get_data(variables=["spikes"])
        neo_relation = self.neural3assoc_topology.relationCells.get_data(variables=["spikes"])
        return [neo_base, neo_property, neo_relation]
        
    # Private function for return overall spike train 
    def __get_overallspikes(self, dataname, neo_data, turnon):
        """Returns `Neo SpikeTrain <https://neo.readthedocs.io/en/stable/api_reference.html#neo.core.SpikeTrain>`_.
        All of it if the data structure is basedata other wise the they are shifted accordingly for propdata and reldata.
        
        This function is no longer used by __split_spiketrains
        """
        if turnon=="all":
            if dataname=="basedata":
                return neo_data.segments[0].spiketrains
            else:
                if dataname=="propdata":
                    data = getattr(self, "basedata")
                    tstart = data.numberUnits * 100 # this 100 is the same value as in :py:meth:`.__choose_applicable_test`
                else:
                    data1 = getattr(self, "basedata")
                    data2 = getattr(self, "propdata")
                    tstart = (data1.numberUnits * 100) + (data2.numberUnits * 100)
                spktrains_all = []
                for spktrain in neo_data.segments[0].spiketrains:
                    spktrains_all.append( spktrain - tstart*pq.ms )
                return spktrains_all
        else:
            return neo_data.segments[0].spiketrains
    
    # Private function for segregating respective spike trains for each cell assembly within a Neo object.
    def __split_spiketrains(self, dataname, neo_data, turnon):
        """Given the Neo object of a given data name ("basedata" or "propdata" or "reldata", see :py:meth:`.__create_datastructures`),
        this function returns a dictionary with "units" in the structured data as keys and its value the respective spike trains (all cell units in an assembly, i.e. the "unit").
        """
        ca_size = self.neural3assoc_topology.fsa.CA_SIZE
        #
        spkindices = lambda n : (0,ca_size) if (n==0) else ( (n*ca_size), (n*ca_size)+ca_size )
        #
        data = getattr(self, dataname) # "basedata" or "propdata" or "reldata"
        overallspikes = neo_data.segments[0].spiketrains
        #overallspikes = self.__get_overallspikes(dataname, neo_data, turnon)
        #
        parsed_spiketrains = {"all": overallspikes} # this will be the returned value
        for unit in data.units:
            n = data.getUnitNumber(unit)
            indx = spkindices(n)
            parsed_spiketrains.update( {unit: overallspikes[ indx[0] : indx[-1] ] } )
        return parsed_spiketrains
    
    # Plotting functions
    # Private function to get first key for self.results dictionary
    def __get_resultskey(self, dataname):
        """Returns key string for ``self.results``. This is because the attribute names for the data structures are a shortened
        version of the keys in ``self.results`` with the exception of ``self.basedata``."""
        if dataname=="reldata":
            return "relation" # corresponding key in self.results is "relation"
        elif dataname=="propdata":
            return "property" # corresponding key in self.results is "property"
        else:
            return dataname.strip("data") # basedata -> base
    
    # Private function for each subplot in :py:meth:`.plot_all`
    def __subplot_all(self, dataname, colorname, subplotobject):
        """For a given ``subplotobject`` this function returns matplotlib's `eventplot <https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.eventplot.html>`_
        for spiketrains from all the cell units of all the cell assemblies for a given data structure (assigned by the ``dataname`` argument)."""
        legpatches = []
        data = getattr(self, dataname) # "basedata" or "propdata" or "reldata"
        #clrs = self.__generate_compatible_subplot_colors(colorname, data.numberUnits)
        clrs = cm.get_cmap(colorname, 12) # "Reds", "Greens", "Blues"
        for unit in data.units:
            i = data.getUnitNumber(unit)
            #if self.test_metadata[0]=="all":
            subplotobject.eventplot( self.results[ self.__get_resultskey(dataname) ][ unit ],
                                     color = clrs(1.0 - (i*0.1) ) )
            legpatches.append( mpatches.Patch(color=clrs( 1.0-(i*0.1) ), label=unit) )
            #else:
            #    subplotobject.eventplot( self.results[ self.__get_resultskey(dataname) ][ unit ],
            #                             color = clrs[i] )
            #    legpatches.append( mpatches.Patch(color=clrs[i], label=unit) )
        subplotobject.legend( handles=legpatches, shadow=True )
        
    # Private function for returning color map (a tuple) or list of colors
    def __generate_compatible_subplot_colors(self, colorname, numberUnits):
        """This is no longer used."""
        if self.test_metadata[0]=="all": # returns a tuple
            return cm.get_cmap(colorname, 12) # "Reds", "Greens", "Blues"
        else:
            return ['C{}'.format(i) for i in range(numberUnits)]
    
    def plot_all(self, form="1"):
        """Plot of three subplots such that each subplot (invoking :py:meth:`.__subplot_all`) is the matplotlib's `eventplot <https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.eventplot.html>`_
        of `SpikeTrain <https://neo.readthedocs.io/en/stable/api_reference.html#neo.core.SpikeTrain>`_ such that
        
        +---------+------------------------------------------------------------+----------------------------------+
        | subplot | spike trains for all cell units in all cell assemblies for | color map for ``turnon = "all"`` |
        +=========+============================================================+==================================+
        | top     | subject (a.k.a base in ``basedata``)                       | Reds                             |
        +---------+------------------------------------------------------------+----------------------------------+
        | middle  | predicate (a.k.a relation in ``reldata``)                  | Greens                           |
        +---------+------------------------------------------------------------+----------------------------------+
        | bottom  | object (a.k.a property in ``propdata``)                    | Blues                            |
        +---------+------------------------------------------------------------+----------------------------------+
        legpatches = []
        data = getattr(self, dataname) # "basedata" or "propdata" or "reldata"
        #clrs = self.__generate_compatible_subplot_colors(colorname, data.numberUnits)
        clrs = cm.get_cmap(colorname, 12) # "Reds", "Greens", "Blues"
        for unit in data.units:
            i = data.getUnitNumber(unit)
            #if self.test_metadata[0]=="all":
            subplotobject.eventplot( self.results[ self.__get_resultskey(dataname) ][ unit ],
                                     color = clrs(1.0 - (i*0.1) ) )
            legpatches.append( mpatches.Patch(color=clrs( 1.0-(i*0.1) ), label=unit) )
            #else:
            #    subplotobject.eventplot( self.results[ self.__get_resultskey(dataname) ][ unit ],
            #                             color = clrs[i] )
            #    legpatches.append( mpatches.Patch(color=clrs[i], label=unit) )
        subplotobject.legend( handles=legpatches, shadow=True )
        """
        if form=="1":
            datanames = ["basedata", "propdata", "reldata"]
            colornames = ["Reds", "Blues", "Greens"]
            legpatches = []
            for i in range(len(datanames)):
                dataname = datanames[i]
                data = getattr(self, dataname)
                clrs = cm.get_cmap(colornames[i], 12)
                for unit in data.units:
                    j = data.getUnitNumber(unit)
                    plt.eventplot( self.results[ self.__get_resultskey(dataname) ][ unit ],
                                   color = clrs(1.0 - (i*0.1) ) )
                    legpatches.append( mpatches.Patch(color=clrs( 1.0-(i*0.1) ), label=unit) )
            plt.legend( handles=legpatches, shadow=True
                        ('No mask', 'Masked if > 0.5', 'Masked if < -0.5'), loc='upper right' )
            plt.ylabel("cell units\nper CA")
            plt.xlabel("time (ms)")
            plt.title("Three-way Association")
        elif form=="2":
            fig, ((sp1),
                  (sp2),
                  (sp3)) = plt.subplots(3,1, sharex=True)
            # If turnon is "all" Red color for subject, i.e. base Therefore its spectrum is used here
            self.__subplot_all("basedata", "Reds", sp1)
            #
            # If turnon is "all" Blue color for object, i.e. property
            self.__subplot_all("propdata", "Blues", sp2)
            #
            # If turnon is "all" Green color for predicate, i.e. relation
            self.__subplot_all("reldata", "Greens", sp3)
            #
            sp1.title.set_text("Subject (base)")
            sp2.title.set_text("Object (property)")
            sp3.title.set_text("Predicate (relation)")
            #
            sp1.set(ylabel="cell units\nper CA")
            sp2.set(ylabel="cell units\nper CA")
            sp3.set(ylabel="cell units\nper CA")
            sp3.set(xlabel="time (ms)")
            #
            plt.subplots_adjust( hspace=0.5 ) # spacing for the each subplot title
        plt.show()
        
    def plot_specific(self, basename=None, relname=None, propname=None):
        """Plot of three subplots such that each is the matplotlib's `eventplot <https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.eventplot.html>`_
        of `SpikeTrain <https://neo.readthedocs.io/en/stable/api_reference.html#neo.core.SpikeTrain>`_ of all the cell units in cell assembly for given
        
        * ``basename`` in top subplot for subject, color is red
        * ``relname`` in middle subplot for predicate, color is green
        * ``propname`` in bottom subplot for object, color is blue
        
        """
        fig, ((sp1),
              (sp2),
              (sp3)) = plt.subplots(3,1, sharex=True)
        #
        sp1.eventplot( self.results["base"][basename], color="red" ) # animal
        z_patch = mpatches.Patch( color="red", label=basename )
        sp1.legend( handles=[z_patch], shadow=True )
        #
        sp2.eventplot( self.results["property"][propname], color="blue" ) # food
        z_patch = mpatches.Patch( color="blue", label=propname )
        sp2.legend( handles=[z_patch], shadow=True )
        #
        sp3.eventplot( self.results["relation"][relname], color="green" ) # eats
        z_patch = mpatches.Patch( color="green", label=relname )
        sp3.legend( handles=[z_patch], shadow=True )
        #
        sp1.title.set_text('Subject (base)')
        sp2.title.set_text('Object (property)')
        sp3.title.set_text('Predicate (relation)')
        #
        sp1.set(ylabel="cell units\nper CA")
        sp2.set(ylabel="cell units\nper CA")
        sp3.set(ylabel="cell units\nper CA")
        sp3.set(xlabel="time (ms)")
        #
        plt.subplots_adjust( hspace=.5 ) # spacing for the each subplot title
        plt.show()