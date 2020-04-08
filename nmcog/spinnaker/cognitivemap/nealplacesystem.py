# =============================================================================
# ~/spinnaker/cognitivemap/nealplacesystem.py
#
# created January 2020 Lungsi
#
# =============================================================================
import spynnaker8 as sim

#import quantities as pq
# for plotting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    def __init__(self, nobjects=2, nplaces=3, objectsTOplaces=None, find="all"):
        self.nobjects = nobjects
        self.nplaces = nplaces
        #
        self.neal = NealCoverFunctions()
        #
        self.inputTimes = self.__generateSpikeTimes( objectsTOplaces )
        if find=="all":
            [self.questions, self.answers] = self.__run_all( objectsTOplaces, find="for-object" )
            qes, ans = self.__run_all( objectsTOplaces, find="for-place" )
            self.questions.update( qes )
            self.answers.update( ans )
        else:
            self.questions = {}
            self.answers = {}
            for findkey, findval in find.items():
                sim.setup( timestep = self.neal.DELAY, min_delay = self.neal.DELAY, max_delay = self.neal.DELAY, debug=0)
                self.spikeSource = self.__makeSpikeSource( self.inputTimes )
                self.__createCogmap( self.nobjects, self.nplaces )
                self.cogmap.sourceStartsAutomaton( self.spikeSource[0] )
                #
                self.__bindObjectsToPlaces( objectsTOplaces )
                if findkey=="for-object":
                    self.__retrievePlaceForObject( findval )
                    spks_qes = self.cogmap.queryOnObjectCells.get_data( variables=["spikes"] )
                    spks_ans = self.cogmap.answerPlaceCells.get_data( variables=["spikes"] )
                else: # findkey=="for-place"
                    self.__retrieveObjectForPlace( findval )
                    spks_qes = self.cogmap.queryOnPlaceCells.get_data( variables=["spikes"] )
                    spks_ans = self.cogmap.answerObjectCells.get_data( variables=["spikes"] )
                #
                self.questions.update( {findkey: { str(findval): spks_qes } } )
                self.answers.update( { findkey: { str(findval): spks_ans } } )
                #
                self.neal.nealApplyProjections()
                sim.run( self.inputTimes[-1]+500 )
                #
                #self.cogmap.printCogMapNets()
                sim.end()
    
    def __run_all(self, objectsTOplaces, find=None):
        """Given a key, "for-object" or "for-place" this function runs
        for all its respective elements and returns a dictionary."""
        if find=="for-object":
            allfinds = self.nobjects
        elif find=="for-place":
            allfinds = self.nplaces
        #
        questions = {}
        answers = {}
        for findFor in range(allfinds):
            sim.setup( timestep = self.neal.DELAY,
                       min_delay = self.neal.DELAY,
                       max_delay = self.neal.DELAY, debug=0 )
            self.spikeSource = self.__makeSpikeSource( self.inputTimes )
            self.__createCogmap( self.nobjects, self.nplaces )
            self.cogmap.sourceStartsAutomaton( self.spikeSource[0] )
            #
            self.__bindObjectsToPlaces( objectsTOplaces )
            if find=="for-object":
                self.__retrievePlaceForObject( findFor )
                spks_qes = self.cogmap.queryOnObjectCells.get_data( variables=["spikes"] )
                spks_ans = self.cogmap.answerPlaceCells.get_data( variables=["spikes"] )
            else: # find=="for-place"
                self.__retrieveObjectForPlace( findFor )
                spks_qes = self.cogmap.queryOnPlaceCells.get_data( variables=["spikes"] )
                spks_ans = self.cogmap.answerObjectCells.get_data( variables=["spikes"] )
            #
            if findFor==0:
                questions.update( { find: { str(findFor): spks_qes } } )
                answers.update( { find: { str(findFor): spks_ans } } )
            else:
                questions[find].update( { str(findFor): spks_qes } )
                answers[find].update( { str(findFor): spks_ans } )
            #
            self.neal.nealApplyProjections()
            sim.run( self.inputTimes[-1]+500 )
            #
            sim.end()
        return [questions, answers]
    
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
        self.cogmap.sourceTurnOnRetrievePlaceFromObject( self.spikeSource[-1] )
        self.cogmap.sourceTurnsOnObjectQuery( self.spikeSource[-1], findPlaceFor )
            
    def __retrieveObjectForPlace(self, findObjectFor):
        """What object are in the place?"""
        self.cogmap.sourceTurnOnRetrieveObjectFromPlace( self.spikeSource[-1] )
        self.cogmap.sourceTurnsOnPlaceQuery( self.spikeSource[-1], findObjectFor )
    
    # Private function
    def __generate_range(self, n):
        r = []
        for i in range(n):
            if i==0:
                indx_start = 0
                indx_end = self.cogmap.fsa.CA_SIZE
            else:
                indx_start = indx_end
                indx_end = indx_end + self.cogmap.fsa.CA_SIZE
            r.append( [indx_start, indx_end] )
        return r
    
    def plot(self, obj=None, pla=None):
        plt.close() # close any previous figure
        allrange_nplace = self.__generate_range( self.nplaces )
        allrange_nobjects = self.__generate_range( self.nobjects )
        if obj is not None:
            fig, ( allsps ) = plt.subplots(self.nplaces, 2, sharex=True)
            for i in range(self.nplaces): # second column of subplots for places
                for j in range( allrange_nplace[i][0], allrange_nplace[i][1] ):
                    allsps[i][1].eventplot( self.answers["for-objects"][str(obj)].segments[0].spiketrains[j] )
            #
            for i in range(self.nobjects): # first column of subplots for objects
                for j in range( allrange_nobjects[i][0], allrange_nobjects[i][1] ):
                    allsps[i][0].eventplot( self.questions["for-objects"][str(obj)].segments[0].spiketrains[j] )
            plt.show()
        elif pla is not None:
            fig, ( allsps ) = plt.subplots(self.nobjects, 2, sharex=True)
            for i in range(self.nobjects): # second column of subplots for objects
                for j in range( allrange_nobjects[i][0], allrange_nobjects[i][1] ):
                    allsps[i][1].eventplot( self.answers["for-places"][str(pla)].segments[0].spiketrains[j] )
            #
            for i in range(self.nplaces): # first column of subplots for places
                for j in range( allrange_nplaces[i][0], allrange_nplaces[i][1] ):
                    allsps[i][0].eventplot( self.questions["for-places"][str(pla)].segments[0].spiketrains[j] )
            plt.show()