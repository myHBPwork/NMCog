import spynnaker8 as sim

from .nealmentalmap.cogmapClass import CogmapBaseClass
from nmcog.spinnaker.specialfunction.neal import NealCoverFunctions

class NEALCogmap(object):
    def __init__(self, nobjects=2, nplaces=3, objectsTOplaces=None, findPlaceFor=None, findObjectFor=None):
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
        neal = NealCoverFunctions()
        sim.setup(timestep=neal.DELAY, min_delay=neal.DELAY, max_delay=neal.DELAY, debug=0)
        #
        inputTimes = self.generateSpikeTimes( objectsTOplaces )
        spikeSource = self.makeSpikeSource( inputTimes )
        self.createCogmap( nobjects, nplaces )
        self.cogmap.sourceStartsAutomaton( spikeSource[0] )
        #
        self.bindObjectsToPlaces(spikeSource, objectsTOplaces)
        self.retrievePlaceForObject(spikeSource, findPlaceFor)
        self.retrieveObjectForPlace(spikeSource, findObjectFor)
        #
        neal.nealApplyProjections()
        sim.run( inputTimes[-1]+500 )
        #
        #self.cogmap.printCogMapNets()
        sim.end()
    
    def createCogmap(self, nobjects, nplaces):
        self.cogmap = CogmapBaseClass()
        self.cogmap.createAutomaton()
        self.cogmap.createObjects(nobjects)
        self.cogmap.connectObjects()
        self.cogmap.createPlaces(nplaces)
        self.connectPlaces()
        self.cogmap.setupCogMapRecording()
        self.cogmap.makeLearningSynapses()
        self.cogmap.connectAutomaton()
    
    def generateSpikeTimes(self, ojectsTOplaces):
        inputTimes = [ 10. ]
        if objectsTOplaces is not None:
            for i in range( 1, len(objectsTOplaces) ):
                if i==1:
                    inputTimes.append( 50. )
                elif i==2:
                    inputTimes.append( inputTimes[-1] * inputTimes[0] )
                else:
                    inputTimes.append( inputTimes[-1] + 500. )
        return inputTimes
    
    def makeSpikeSource(self, inputTimes):
        spikeArrays = [ {"spike_times": [ anInputTime ]} for anInputTime in inputTimes ]
        spikeGens = [ sim.Population( 1, sim.SpikeSourceArray, spikeArrays[i],
                                      label="inputSpikes_"+str(i+1) )
                        for i in range( len(spikeArrays) ) ]
        return spikeGens
    
    def bindObjectsToPlaces(self, spikeGens, objectsTOplaces):
        if objectsTOplaces in not None:
            for i in range( len(objectsTOplaces) ):
                sourceIndx = i+1
                objPlacePair = objectsTOplaces[i]
                self.cogmap.sourceTurnsOnBind( spikeGens[sourceIndx] )
                self.cogmap.sourceTurnsOnPlaceOn( objPlacePair[-1], spikeGens[sourceIndx] )
                self.cogmap.sourceTurnsOnObjectOn( objPlacePair[0], spikeGens[sourceIndx] )
        else:
            pass
    
    def retrievePlaceForObject(self, spikeGens, findPlaceFor):
        "Where is the object?"
        if findPlaceFor is not None:
            self.cogmap.sourceTurnOnRetrievePlaceFromObject( spikeGens[-1] )
            self.cogmap.sourceTurnsOnObjectQuery( spikeGens[-1], findPlaceFor )
        else:
            pass
            
    def retrieveObjectForPlace(self, spikeGens, findObjectFor):
        "What object are in the place?"
        if findObjectFor is not None:
            self.cogmap.sourceTurnOnRetrievePlaceFromPlace( spikeGens[-1] )
            self.cogmap.sourceTurnsOnPlaceQuery( spikeGens[-1], findObjectFor )
        else:
            pass