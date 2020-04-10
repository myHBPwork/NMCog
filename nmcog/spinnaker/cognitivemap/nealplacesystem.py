# =============================================================================
# ~/spinnaker/cognitivemap/nealplacesystem.py
#
# created January 2020 Lungsi
#
# =============================================================================
import spynnaker8 as sim

# for plotting
import quantities as pq
import matplotlib.pyplot as plt
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
    def __init__(self, nobjects=None, nplaces=None, objectsTOplaces=None, find="all"):
        self.nobjects = nobjects
        self.nplaces = nplaces
        self.objectsTOplaces = objectsTOplaces
        #
        self.neal = NealCoverFunctions()
        #
        self.inputTimes = self.__generateSpikeTimes()
        if find=="all":
            self.questions, self.answers = self.__run_all( findkey="for-object" )
            qes, ans = self.__run_all( findkey="for-place" )
            self.questions.update( qes )
            self.answers.update( ans )
        else:
            for findkey, findval in find.items():
                self.questions, self.answers = self.__run( findkey, findval )
    
    def __run_all(self, findkey=None):
        """Given a key, "for-object" or "for-place" this function runs
        for all its respective elements and returns a dictionary."""
        if findkey=="for-object":
            allfinds = self.nobjects
        elif findkey=="for-place":
            allfinds = self.nplaces
        questions = {}
        answers = {}
        for findFor in range(allfinds):
            q_dict, a_dict = self.__run( findkey, findFor )
            if findFor==0: # create initial dictionary for respective findkey
                questions.update( q_dict )
                answers.update( a_dict )
            else: # append on previously created dictionary for respective findkey
                questions[findkey].update( q_dict[findkey] )
                answers[findkey].update( a_dict[findkey] )
        return questions, answers
    
    def __run(self, findkey, findval):
        # one: {findkey: val}
        # all: findkey and findval is i of the loop
        sim.setup( timestep = self.neal.DELAY,
                   min_delay = self.neal.DELAY,
                   max_delay = self.neal.DELAY, debug=0)
        self.spikeSource = self.__makeSpikeSource_from_inputTimes()
        self.__createCogmap()
        self.cogmap.sourceStartsAutomaton( self.spikeSource[0] )
        #
        self.__bindObjectsToPlaces( {findkey: findval} )
        if findkey=="for-object":
            self.__retrievePlaceForObject( findval )
        elif findkey=="for-place":
            self.__retrieveObjectForPlace( findval )
        #
        self.neal.nealApplyProjections()
        sim.run( self.inputTimes[-1]+500 )
        #
        q_dict, a_dict = self.__getdata( findkey, findval )
        #
        #self.cogmap.printCogMapNets()
        #sim.end()
        #
        return q_dict, a_dict
        
    
    def __createCogmap(self):
        """Creates the cognitive map for the place cell system using :ref:`PlaceCellSystemClass`."""
        self.cogmap = PlaceCellSystemClass()
        self.cogmap.createAutomaton()
        self.cogmap.createObjects( self.nobjects )
        self.cogmap.connectObjects()
        self.cogmap.createPlaces( self.nplaces )
        self.cogmap.connectPlaces()
        self.cogmap.setupCogMapRecording()
        self.cogmap.makeLearningSynapses()
        self.cogmap.connectAutomaton()
        
    def __makeSpikeSource_from_inputTimes(self):
        """Returns a list of spike sources. The number of spike source determined by
        the number of ``self.inputTimes`` produced by :py:meth:`.generateSpikeTimes`."""
        spikeArrays = [ {"spike_times": [ anInputTime ]} for anInputTime in self.inputTimes ]
        spikeGens = [ sim.Population( 1, sim.SpikeSourceArray, spikeArrays[i],
                                      label="inputSpikes_"+str(i+1) )
                        for i in range( len(spikeArrays) ) ]
        return spikeGens
    
    # Private function
    def __generateSpikeTimes(self):
        """Creates array of spike times required for making spike source.
        
        * The first spike time is for starting the automaton.
        * The second for the first object with a place
        * The rest for objects with a place but **not** for objects with no place
        * The last spike time for retrieving and quering about an object.
        
        """
        inputTimes = [ 10. ] # for starting the automaton
        if self.objectsTOplaces is not None: # does not include objects with no place,
            oTp = self.__object_place_tuple_list( self.objectsTOplaces )
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
    def __rearrange_oTp_for_findval(self, find, oTp):
        """This step is needed otherwise Chris Huyk et al's function does not behave as
        advertised, i.e. after about two objects querying the succeeding objects does
        not result in answers eventhough by definition these objects are bound to a place.
        I found that for any object (or place) in question if they are moved up the list
        i.e. the will receive the spikesource[1] (the first is reserved for initiating the
        automaton) then querying any bound object will return an answer."""
        y = []; tmp = [] # first and temporary list
        for findkey, findval in find.items():
            if findkey=="for-object":
                indx = 0 # first index of a tupl
            elif findkey=="for-place":
                indx = 1 # second index of a tupl
            [y.append(tupl) if tupl[indx]==findval else tmp.append(tupl) for tupl in oTp]
        return y+tmp
    
    # Private function
    def __bindObjectsToPlaces(self, find):
        """Binds objects to place using :ref:`PlaceCellSystemClass` ``.sourceTurnsOnBind``, :ref:`PlaceCellSystemClass` ``.sourceTurnsOnPlaceOn``, and
        :ref:`PlaceCellSystemClass` ``.sourceTurnsOnObjectOn``."""
        if self.objectsTOplaces is not None:
            oTp = self.__object_place_tuple_list( self.objectsTOplaces )
            reordered_oTp = self.__rearrange_oTp_for_findval(find, oTp)
            for i in range( len(reordered_oTp) ):
                sourceIndx = i+1 # first,0, spike source is reserved for automaton
                objPlacePair = reordered_oTp[i]
                self.cogmap.sourceTurnsOnBind( self.spikeSource[sourceIndx] )
                self.cogmap.sourceTurnsOnPlaceOn( objPlacePair[1], self.spikeSource[sourceIndx] )
                self.cogmap.sourceTurnsOnObjectOn( objPlacePair[0], self.spikeSource[sourceIndx] )
    
    def __retrievePlaceForObject(self, findPlaceFor):
        """Where is the object?"""
        self.cogmap.sourceTurnOnRetrievePlaceFromObject( self.spikeSource[-1] )
        self.cogmap.sourceTurnsOnObjectQuery( self.spikeSource[-1], findPlaceFor )
            
    def __retrieveObjectForPlace(self, findObjectFor):
        """What object are in the place?"""
        self.cogmap.sourceTurnOnRetrieveObjectFromPlace( self.spikeSource[-1] )
        self.cogmap.sourceTurnsOnPlaceQuery( self.spikeSource[-1], findObjectFor )
        
    def __getdata(self, findkey, findval):
        if findkey=="for-object":
            spks_qes = self.cogmap.queryOnObjectCells.get_data( variables=["spikes"] )
            spks_ans = self.cogmap.answerPlaceCells.get_data( variables=["spikes"] )
        elif findkey=="for-place":
            spks_qes = self.cogmap.queryOnPlaceCells.get_data( variables=["spikes"] )
            spks_ans = self.cogmap.answerObjectCells.get_data( variables=["spikes"] )
        q_dict = { findkey: { str(findval): spks_qes } }
        a_dict = { findkey: { str(findval): spks_ans } }
        return q_dict, a_dict
    
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
        """."""
        plt.close() # close any previous figure
        allrange_nplaces = self.__generate_range( self.nplaces )
        allrange_nobjects = self.__generate_range( self.nobjects )
        if obj is not None:
            fig, ( allsps ) = plt.subplots(self.nplaces, 2, sharex=True)
            for i in range(self.nplaces): # second column of subplots for places
                for j in range( allrange_nplace[i][0], allrange_nplace[i][1] ): # shift the spike train by subtracting with last inputTime
                    allsps[i][1].eventplot( self.answers["for-object"][str(obj)].segments[0].spiketrains[j] - self.inputTimes[-1]*pq.ms )
                allsps[i][1].title.set_text('Place-'+str(i))
                allsps[i][1].set_yticks( [] )
                if i==(self.nplaces-1):
                    allsps[i][1].set(xlabel="time (ms)")
            #
            for i in range(self.nobjects): # first column of subplots for objects
                for j in range( allrange_nobjects[i][0], allrange_nobjects[i][1] ): # shift the spike train by subtracting with last inputTime
                    allsps[i][0].eventplot( self.questions["for-object"][str(obj)].segments[0].spiketrains[j] - self.inputTimes[-1]*pq.ms )
                allsps[i][0].title.set_text('Object-'+str(i))
                allsps[i][0].set_yticks( [] )
                if i==(self.nobjects-1):
                    allsps[i][0].set(xlabel="time (ms)")
            plt.subplots_adjust( hspace=.5 ) # spacing for the each subplot title
            plt.show()
        elif pla is not None:
            fig, ( allsps ) = plt.subplots(self.nobjects, 2, sharex=True)
            for i in range(self.nobjects): # second column of subplots for objects
                for j in range( allrange_nobjects[i][0], allrange_nobjects[i][1] ): # shift the spike train by subtracting with last inputTime
                    allsps[i][1].eventplot( self.answers["for-place"][str(pla)].segments[0].spiketrains[j] - self.inputTimes[-1]*pq.ms )
                allsps[i][1].title.set_text('Object-'+str(i))
                allsps[i][1].set_yticks( [] )
                if i==(self.nobjects-1):
                    allsps[i][1].set(xlabel="time (ms)")
            #
            for i in range(self.nplaces): # first column of subplots for places
                for j in range( allrange_nplaces[i][0], allrange_nplaces[i][1] ): # shift the spike train by subtracting with last inputTime
                    allsps[i][0].eventplot( self.questions["for-place"][str(pla)].segments[0].spiketrains[j] - self.inputTimes[-1]*pq.ms )
                allsps[i][0].title.set_text('Place-'+str(i))
                allsps[i][0].set_yticks( [] )
                if i==(self.nplaces-1):
                    allsps[i][0].set(xlabel="time (ms)")
            plt.subplots_adjust( hspace=.5 ) # spacing for the each subplot title
            plt.show()