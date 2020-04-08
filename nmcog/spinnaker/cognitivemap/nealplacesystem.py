# =============================================================================
# ~/spinnaker/cognitivemap/nealplacesystem.py
#
# created January 2020 Lungsi
#
# =============================================================================
import spynnaker8 as sim

#import quantities as pq
# for plotting
#import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
#from matplotlib import gridspec
#from matplotlib import cm

from .nealmentalmap.placecellsysClass import PlaceCellSystemClass
from nmcog.spinnaker.specialfunction.neal import NealCoverFunctions

class NEALPlaceSystem(object):
    """
    Consider nobject = 2 and nplaces = 3
    
    +------------------+---------------------+------------------+-----------------+
    | Example use case | objectsTOplaces     | findPlaceFor     | findObjectFor   |
    +==================+=====================+==================+=================+
    | 1 (default)      | None                | None             | None            |
    +------------------+---------------------+------------------+-----------------+
    | 2                | [(0,1),(1,0),(1,2)] | None             | None            |
    +------------------+---------------------+------------------+-----------------+
    | 3                | [(0,1),(1,0),(1,2)] | 1 (for object 1) | None            |
    +------------------+---------------------+------------------+-----------------+
    | 4                | [(0,1),(1,0),(1,2)] | None             | 2 (for place 2) |
    +------------------+---------------------+------------------+-----------------+
    
    """
    def __init__(self, nobjects=2, nplaces=3, objectsTOplaces=None, findPlaceFor=None, findObjectFor=None):
        self.nobjects = nobjects
        self.nplaces = nplaces
        #
        neal = NealCoverFunctions()
        sim.setup(timestep=neal.DELAY, min_delay=neal.DELAY, max_delay=neal.DELAY, debug=0)
        #
        inputTimes = self.__generateSpikeTimes( objectsTOplaces )
        self.spikeSource = self.__makeSpikeSource( inputTimes )
        self.__createCogmap( self.nobjects, self.nplaces )
        self.cogmap.sourceStartsAutomaton( self.spikeSource[0] )
        #
        self.__bindObjectsToPlaces( objectsTOplaces )
        self.__retrievePlaceForObject( findPlaceFor )
        self.__retrieveObjectForPlace( findObjectFor )
        #
        neal.nealApplyProjections()
        sim.run( inputTimes[-1]+500 )
        #
        #self.cogmap.printCogMapNets()
        #sim.end()
    
    def __createCogmap(self, nobjects, nplaces):
        """Creates the cognitive map for the place cell system using :ref:`PlaceCellSystemClass`."""
        self.cogmap = PlaceCellSystemClass()
        self.cogmap.createAutomaton()
        self.cogmap.createObjects(nobjects)
        self.cogmap.connectObjects()
        self.cogmap.createPlaces(nplaces)
        self.cogmap.connectPlaces()
        self.cogmap.setupCogMapRecording()
        self.cogmap.makeLearningSynapses()
        self.cogmap.connectAutomaton()
        
    def __makeSpikeSource(self, inputTimes):
        """Returns a list of spike sources. The number of spike source determined by
        the number of ``inputTimes`` produced by :py:meth:`.generateSpikeTimes`."""
        spikeArrays = [ {"spike_times": [ anInputTime ]} for anInputTime in inputTimes ]
        spikeGens = [ sim.Population( 1, sim.SpikeSourceArray, spikeArrays[i],
                                      label="inputSpikes_"+str(i+1) )
                        for i in range( len(spikeArrays) ) ]
        return spikeGens
    
    # Private function
    def __generateSpikeTimes(self, objectsTOplaces):
        """Creates array of spike times required for making spike source.
        
        * The first spike time is for starting the automaton.
        * The second for the first object with a place
        * The rest for objects with a place but **not** for objects with no place
        * The last spike time for retrieving and quering about an object.
        
        """
        inputTimes = [ 10. ] # for starting the automaton
        if objectsTOplaces is not None: # does not include objects with no place,
            oTp = self.__object_place_tuple_list(objectsTOplaces)
            for i in range( 0, len(oTp)+1 ):
                if i==0: # for first object
                    inputTimes.append( 50. )
                elif i==1: # for second object
                    inputTimes.append( inputTimes[-1] * inputTimes[0] )
                else: # rest object, last is for retrieval and query about an object
                    inputTimes.append( inputTimes[-1] + 500. )
        return inputTimes
    
    # Private function
    def __object_place_tuple_list(self, objectsTOplaces):
        """Not all the objects in the ``objectTOplaces`` are in a place.
        Return a list of tuple that only includes objects in a place."""
        oTp = []
        [oTp.append(tupl) for tupl in objectsTOplaces if len(tupl)!=1]
        return oTp
    
    # Private function
    def __bindObjectsToPlaces(self, objectsTOplaces):
        """Binds objects to place using :ref:`PlaceCellSystemClass` ``.sourceTurnsOnBind``, :ref:`PlaceCellSystemClass` ``.sourceTurnsOnPlaceOn``, and
        :ref:`PlaceCellSystemClass` ``.sourceTurnsOnObjectOn``."""
        if objectsTOplaces is not None:
            oTp = self.__object_place_tuple_list(objectsTOplaces)
            for i in range( len(oTp) ):
                sourceIndx = i+1 # first,0, spike source is reserved for automaton
                objPlacePair = oTp[i]
                self.cogmap.sourceTurnsOnBind( self.spikeSource[sourceIndx] )
                self.cogmap.sourceTurnsOnPlaceOn( objPlacePair[1], self.spikeSource[sourceIndx] )
                self.cogmap.sourceTurnsOnObjectOn( objPlacePair[0], self.spikeSource[sourceIndx] )
        else:
            pass
    
    def __retrievePlaceForObject(self, findPlaceFor):
        """Where is the object?"""
        if findPlaceFor is not None:
            self.cogmap.sourceTurnOnRetrievePlaceFromObject( self.spikeSource[-1] )
            self.cogmap.sourceTurnsOnObjectQuery( self.spikeSource[-1], findPlaceFor )
        else:
            pass
            
    def __retrieveObjectForPlace(self, findObjectFor):
        """What object are in the place?"""
        if findObjectFor is not None:
            self.cogmap.sourceTurnOnRetrieveObjectFromPlace( self.spikeSource[-1] )
            self.cogmap.sourceTurnsOnPlaceQuery( self.spikeSource[-1], findObjectFor )
        else:
            pass