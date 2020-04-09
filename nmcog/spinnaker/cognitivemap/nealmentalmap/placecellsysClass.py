# ~/nmcog/spinnaker/cognitivemap/nealmentalmap/placecellsysClass.py
#
# Documentation by Lungsi 6 April 2020
#
#This is driven by an FSA that manages the binding and the retrievals.
#Initially, (startState) it waits for a binding event.  It then
#tryToBind, which uses a timer since it takes time to bind.  If it
#succeeds it goes to bindOnState
#bindOn turns on the bindingTimer
#the bindingTimer turns on bindDone state
#bindDone -> start via bindDoneTimer.
#
#Fail states occurs with bindFailState twoPlacesFact, twoObjectsFact,
#and notEnoughPlaceObjectsFact.
#
#retrievePlaceState is turned on externally by a query.
#It turns off start.  It allows the binding nets to fire, and when a place
#fires, it turns on the placeRetrievedFact (extra neurons in the automaton net).
#Together these turn on retrievePlaceDone, which then goes back to startState
#
#A similar mechanism is used for retrieveObject.
#

from nmcog.spinnaker.specialfunction.neal import NealCoverFunctions
from nmcog.spinnaker.specialfunction.neal import TimerClass

# added for nmcog
import spynnaker8 as sim
from nmcog.spinnaker.specialfunction.neal import FSAHelperFunctions

class PlaceCellSystemClass:
    """
    
    +----------------------------------+-------------------------------+
    | Methods                          | Argument                      |
    +==================================+===============================+
    | :py:meth:`.createObjects`        | integer ``numberObjects``     |
    +----------------------------------+-------------------------------+
    | :py:meth:`.createPlaces`         | integer ``numberPlaces``      |
    +----------------------------------+-------------------------------+
    | :py:meth:`.createAutomaton`      | - integer ``tryToBindStates`` |
    |                                  | - integer ``bindingStates``   |
    |                                  | - integer ``bindDoneStates``  |
    +----------------------------------+-------------------------------+
    | :py:meth:`.connectObjects`       | -                             |
    +----------------------------------+-------------------------------+
    | :py:meth:`.connectPlaces`        | -                             |
    +----------------------------------+-------------------------------+
    | :py:meth:`.connectAutomaton`     | -                             |
    +----------------------------------+-------------------------------+
    | :py:meth:`.setupCogMapRecording` | -                             |
    +----------------------------------+-------------------------------+
    | :py:meth:`.makeLearningSynapses` | -                             |
    +----------------------------------+-------------------------------+
    
    
    +---------------+-----------------+--------------------------------+
    | Methods       | Cell assemblies | Available cells (for analysis) |
    +===============+=================+================================+
    | An object     | to bind cells   | - ``self.objectBindCells``     |
    |               | to bind on      | - ``self.objectBindOnCells``   |
    |               | to bind done    | - ``self.objectBindDoneCells`` |
    |               | to query on     | - ``self.queryOnObjectCells``  |
    |               | to answer       | - ``self.answerObjectCells``   |
    +---------------+-----------------+--------------------------------+
    | A place       | to bind cells   | - ``self.placeBindCells``      |
    |               | to bind on      | - ``self.placeBindOnCells``    |
    |               | to bind done    | - ``self.placeBindDoneCells``  |
    |               | to query on     | - ``self.queryOnPlaceCells``   |
    |               | to answer       | - ``self.answerPlaceCells``    |
    +---------------+-----------------+--------------------------------+
    | The Automaton |      15         | - ``self.automatonCells``      |
    +---------------+-----------------+--------------------------------+

    
    
    +-------------------------------+-------------------+-----------------------------------------------------+
    | Names of 15 Automaton states  | State number      | Methods where state is used                         |
    +===============================+===================+=====================================================+
    | ``startState``                | 0                 | - :py:meth:`.connectStartState`                     |
    |                               |                   | - :py:meth:`.connectBindFailState`                  |
    |                               |                   | - :py:meth:`.connectBindDoneState`                  |
    |                               |                   | - :py:meth:`.connectRetrieveObjectState`            |
    |                               |                   | - :py:meth:`.connectRetrieveObjectDoneState`        |
    |                               |                   | - :py:meth:`.connectRetrievePlaceState`             |
    |                               |                   | - :py:meth:`.connectRetrievePlaceDoneState`         |
    |                               |                   | - :py:meth:`.sourceStartsAutomaton`                 |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``tryBindState``              | 1                 | - :py:meth:`.connectStartState`                     |
    |                               |                   | - :py:meth:`.connectBindOnState`                    |
    |                               |                   | - :py:meth:`.connectBindFailState`                  |
    |                               |                   | - :py:meth:`.sourceTurnsOnBind`                     |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``bindOnState``               | 2                 | - :py:meth:`.connectBindOnState`                    |
    |                               |                   | - :py:meth:`.connectBindFailState`                  |
    |                               |                   | - :py:meth:`.bindOnPrimesPlaceAndObjectBind`        |
    |                               |                   | - :py:meth:`.connectBindDoneState`                  |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``bindFailState``             | 3                 | - :py:meth:`.connectStartState`                     |
    |                               |                   | - :py:meth:`.connectBindFailState`                  |
    |                               |                   | - :py:meth:`.bindFailStopsPlaceObjectOn`            |
    |                               |                   | - :py:meth:`.bindFailStopsPlaceObjectOn`            |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``bindDoneState``             | 4                 | - :py:meth:`.connectStartState`                     |
    |                               |                   | - :py:meth:`.connectBindDoneState`                  |
    |                               |                   | - :py:meth:`.connectBindDoneState`                  |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``retrieveObjectState``       | 5                 | - :py:meth:`.retrieveObjectPrimesPlaceBind`         |
    |                               |                   | - :py:meth:`.connectRetrieveObjectState`            |
    |                               |                   | - :py:meth:`.connectRetrieveObjectDoneState`        |
    |                               |                   | - :py:meth:`.sourceTurnOnRetrieveObjectFromPlace`   |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``retrievePlaceState``        | 6                 | - :py:meth:`.retrievePlacePrimesObjectBind`         |
    |                               |                   | - :py:meth:`.connectRetrievePlaceState`             |
    |                               |                   | - :py:meth:`.connectRetrievePlaceDoneState`         |
    |                               |                   | - :py:meth:`.sourceTurnOnRetrievePlaceFromObject`   |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``retrieveObjectDoneState``   | 7                 | - :py:meth:`.connectStartState`                     |
    |                               |                   | - :py:meth:`.connectRetrieveObjectDoneState`        |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``retrievePlaceDoneState``    | 8                 | - :py:meth:`.connectStartState`                     |
    |                               |                   | - :py:meth:`.connectRetrievePlaceDoneState`         |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``lastState``                 | 8                 |                                                     |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``onePlaceOneObjectFact``     | ``lastState`` + 1 | - :py:meth:`.setupObjectPlaceFacts`                 |
    |                               |                   | - :py:meth:`.connectBindOnState`                    |
    |                               |                   | - :py:meth:`.connectBindFailState`                  |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``twoPlacesFact``             | ``lastState`` + 2 | - :py:meth:`.setupObjectPlaceFacts`                 |
    |                               |                   | - :py:meth:`.connectBindFailState`                  |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``twoObjectsFact``            | ``lastState`` + 3 | - :py:meth:`.setupObjectPlaceFacts`                 |
    |                               |                   | - :py:meth:`.connectBindFailState`                  |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``notEnoughPlaceObjectsFact`` | ``lastState`` + 4 | - :py:meth:`.connectBindFailState`                  |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``placeRetrievedFact``        | ``lastState`` + 5 | - :py:meth:`.answerPlaceStartsPlaceRetrievedFact`   |
    |                               |                   | - :py:meth:`.connectRetrievePlaceDoneState`         |
    +-------------------------------+-------------------+-----------------------------------------------------+
    | ``objectRetrievedFact``       | ``lastState`` + 6 | - :py:meth:`.answerObjectStartsObjectRetrievedFact` |
    |                               |                   | - :py:meth:`.connectRetrieveObjectDoneState`        |
    +-------------------------------+-------------------+-----------------------------------------------------+
    
    
    """
    numberAutomatonStates = 15
    numberObjects = -1
    numberPlaces = -1
    
    #def __init__(self,simName,sim,neal,spinnVersion,fsa):
    def __init__(self,simName="spinnaker",spinnVersion=8):
        self.sim = sim
        self.neal = NealCoverFunctions()
        self.fsa = FSAHelperFunctions()
        # added for nmcog
        self.tryToBindTimer = TimerClass(simName = simName,
                                         spinnVersion = spinnVersion)
        self.bindingTimer = TimerClass(simName = simName,
                                       spinnVersion = spinnVersion)
        self.bindDoneTimer = TimerClass(simName = simName,
                                        spinnVersion = spinnVersion)
        # this instantiates the three timers but the timercells are not created here
        # they are created in self.createTimers where default values are used for the
        # number of states but user can pass custom values.
        # however, self.createTimers is called by self.createAutomaton therefore
        # these custom values must be passed into this function which takes effect on
        # the self.createTimers function.
        #
        #self.automatonCells = self.createAutomaton() # commented out for nmcog

    #-----FSA functions and constants
    #state names for the Automaton
    startState = 0
    tryBindState = 1
    bindOnState = 2
    bindFailState = 3
    bindDoneState = 4
    retrieveObjectState = 5
    retrievePlaceState = 6
    retrieveObjectDoneState = 7
    retrievePlaceDoneState = 8
    lastState = 8
    onePlaceOneObjectFact = lastState+1 #one placeBindOn and one objectBindOn on
    twoPlacesFact = lastState+2 #two or more placeBindOn
    twoObjectsFact = lastState+3 #two or more objectBindOn
    notEnoughPlaceObjectsFact = lastState+4 #0 or 1 objects place in total
    placeRetrievedFact = lastState+5
    objectRetrievedFact = lastState+6

    #Each object and place half connects to the onePlaceOneObjectFact
    #Note that 2 of either will turn it on as will more than one of each.
    #These are handled elsewhere to convert to the bindFailState
    def setupObjectPlaceFacts(self):
        """
        This function connects objects and places with the automaton (see :py:meth:`.createAutomaton`).
        
        Below show the connection for one object and one place. But note that the connections are made
        for all objects and all places with the automaton.

        ::
        
            wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
            w                      An Object                      w
          xxwxxxxxxxxxxxxxxxxxxxxxxxxxxx                          w
          x w                          x                          w
          x w   oooooooooooooo   oooooooooooooo   oooooooooooooo  w
          x w   o    binds   o   o   binds    o   o   binds    o  w
          x w   o    cells   o   o  on-cells  o   o done-cells o  w
          x w   oooooooooooooo   oooooooooooooo   oooooooooooooo  w
          x w                                                     w
          x w   oooooooooooooo   oooooooooooooo                   w
          x w   o  inquire   o   o   answer   o                   w
          x w   o  on-cells  o   o about cell o                   w
          x w   oooooooooooooo   oooooooooooooo                   w
          x w                                                     w
          x w                                                     w
          x wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
          x 
          x 
          x 
          x aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
          x a                               Automaton                                     a
          x a                                                                             a
          x a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
          x a  o startState o   o tryBindState o   o bindFailState o   o bindDoneState o  a
          x a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
          xxaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx                                           a
            a  ooooooooooooooooooooooooooo x  x oooooooooooooooooooooooooo                a
            a  o retrieveObjectDoneState o x  x o retrievePlaceDoneState o                a
            a  ooooooooooooooooooooooooooo x  x oooooooooooooooooooooooooo                a
            a                <1/2-ON> Vxxxxx  V <1/2-ON>                                  a
            a  ooooooooooooooooooooooooo   ooooooooooooooo                                a
            a  o onePlaceOneObjectFact o   o bindOnState o                                a
            a  ooooooooooooooooooooooooo   ooooooooooooooo                                a
            a                         ^       ^                                           a
            a                <1/2-ON> x       x <1/2-ON>                                  a
            a                         xxxxxxxxx                                           a
            a                                 x                                           a
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                                              x
                                              x
                                              x         
            ppppppppppppppppppppppppppppppppppppppppppppppppppppppp
            p                       A Place   x                   p
            p                                 x                   p
            p   oooooooooooooo   oooooooooooooo   oooooooooooooo  p
            p   o    binds   o   o   binds    o   o   binds    o  p
            p   o    cells   o   o  on-cells  o   o done-cells o  p
            p   oooooooooooooo   oooooooooooooo   oooooooooooooo  p
            p                                                     p
            p   oooooooooooooo   oooooooooooooo                   p
            p   o  inquire   o   o   answer   o                   p
            p   o  on-cells  o   o about cell o                   p
            p   oooooooooooooo   oooooooooooooo                   p
            p                                                     p
            p                                                     p
            ppppppppppppppppppppppppppppppppppppppppppppppppppppppp
        
        **NOTE:**
        
        * All the states of an automaton are **not** shown in the above illustration.
        * See :ref:`FSAHelperFunctions` ``.stateHalfTurnsOnState``
        
        """
        #print(self.numberObjects)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.objectBindOnCells,objectNumber,
                            self.automatonCells,self.onePlaceOneObjectFact)
            self.fsa.stateHalfTurnsOnState(self.objectBindOnCells,objectNumber,
                            self.automatonCells,self.twoObjectsFact)

        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.placeBindOnCells,placeNumber,
                            self.automatonCells,self.onePlaceOneObjectFact)
            self.fsa.stateHalfTurnsOnState(self.placeBindOnCells,placeNumber,
                            self.automatonCells,self.twoPlacesFact)

    #---Make the fsa that governs the map.  
    def stateStopsPlaceDone(self,stateNumber):
        """
        The given state of the automaton (see :py:meth:`.createAutomaton`) turns-off the
        ``self.placeBindDoneCells`` for all the places, i.e. over all ``self.numberPlaces``.
        
        Below shows the ``startState`` of the automaton turning-off the state represented by
        ``self.placeBindDoneCells`` of just one place. Note that this will be done for all the
        places in ``self.numberPlaces``.

        ::
        
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
            a                               Automaton                                     a
          xxaxxxxxxxx                                                                     a
          x a       x                                                                     a
          x a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
          x a  o startState o   o tryBindState o   o bindFailState o   o bindDoneState o  a
          x a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
          x a                                                                             a
          x a  ooooooooooooooooooooooooooo   oooooooooooooooooooooooooo                   a
          x a  o retrieveObjectDoneState o   o retrievePlaceDoneState o                   a
          x a  ooooooooooooooooooooooooooo   oooooooooooooooooooooooooo                   a
          x a                                                                             a
          x a                                                                             a
          x a                                                                             a
          x aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
          x
          xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx <OFF>
                                                        x            
            ppppppppppppppppppppppppppppppppppppppppppppppppppppppp
            p                       A Place             x         p
            p                                           V         p
            p   oooooooooooooo   oooooooooooooo   oooooooooooooo  p
            p   o    binds   o   o   binds    o   o   binds    o  p
            p   o    cells   o   o  on-cells  o   o done-cells o  p
            p   oooooooooooooo   oooooooooooooo   oooooooooooooo  p
            p                                                     p
            p   oooooooooooooo   oooooooooooooo                   p
            p   o  inquire   o   o   answer   o                   p
            p   o  on-cells  o   o about cell o                   p
            p   oooooooooooooo   oooooooooooooo                   p
            p                                                     p
            p                                                     p
            ppppppppppppppppppppppppppppppppppppppppppppppppppppppp
        
        **NOTE:**
        
        * All the states of an automaton are **not** shown in the above illustration.
        * See :ref:`FSAHelperFunctions` ``.stateTurnsOffState``
        
        """
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.placeBindDoneCells,placeNumber)

    def stateStopsObjectDone(self,stateNumber):
        """See :py:meth:`.stateStopsPlaceDone` but replace place for object."""
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.objectBindDoneCells,objectNumber)

    def stateStopsDone(self,stateNumber):
        """See :py:meth:`.stateStopsPlaceDone` and :py:meth:`.stateStopsObjectDone`"""
        self.stateStopsPlaceDone(stateNumber)
        self.stateStopsObjectDone(stateNumber)

    def connectStartState(self):
        """
        Following the creation of ``self.automatonCells`` (:py:meth:`.createAutomaton`)
        this function connects the states of the automaton.
        
        Connection for an automaton is done as follows
        
        ::
        
                        <OFF>
                    xxxxxxxxxxxxxx
                    x   <1/2-ON> x
                    x    xxxxxx  x         xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                    \/   x   \/  x         x                                            x
            oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo   x
            o startState o   o tryBindState o   o bindFailState o   o bindDoneState o   x
            oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo   x
            x   x     x  x         <OFF>        /\                  /\                  x
            x   x     x  xxxxxxxxxxxxxxxxxxxxxxxxx       <OFF>       x                  x
            x   x     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx                  x
            x   xxxxxxxxxxxxxxxxxxxxxxxxxxx                                             x
            \/<OFF>                       \/<OFF>                                       x
            ooooooooooooooooooooooooooo   oooooooooooooooooooooooooo                    x
            o retrieveObjectDoneState o   o retrievePlaceDoneState o                    x
            ooooooooooooooooooooooooooo   oooooooooooooooooooooooooo                    x
                                                                                        x
            xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            x                                                                   <OFF>
            x
            \/              tryToBindTimer
            ooooooooooooo   ooooooooooooo   ooooooooooooo
            o  state-0  o   o state-... o   o  state-k  o
            ooooooooooooo   ooooooooooooo   ooooooooooooo
                
        Note that for the above illustration to be complete two more steps are required
        
        * see :py:meth:`.stateStopsDone`
        * see :py:meth:`.statePreventsOutput`
        * All the states of an automaton are **not** shown in the above illustration.
        
        Also see
        
        * :ref:`FSAHelperFunctions` ``.stateHalfTurnsOnState``
        * :ref:`FSAHelperFunctions` ``.stateTurnsOffState``
        * :ref:`TimerClass` ``.stateStartsTimer``
        
        """
        #the bind signal moves from start to tryBind
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.startState,
                                       self.automatonCells,self.tryBindState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.tryBindState,
                                       self.automatonCells,self.startState)
        self.tryToBindTimer.stateStartsTimer(self.automatonCells,
                                                 self.tryBindState)

        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                                       self.automatonCells,self.bindDoneState)

        self.stateStopsDone(self.startState)

        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                            self.automatonCells,self.retrieveObjectDoneState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.startState,
                            self.automatonCells,self.retrievePlaceDoneState)

        self.statePreventsOutput(self.startState)


    def statePreventsPlaceOutput(self,stateNumber):
        """See :py:meth:`.statePreventsObjectOutput` but replace object for place."""
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.answerPlaceCells,placeNumber)

    def statePreventsObjectOutput(self,stateNumber):
        """
        The given state of the automaton (see :py:meth:`.createAutomaton`) turns-off the
        ``self.answerObjectCells`` for all the places, i.e. over all ``self.numberPlaces``.
        
        Below shows the ``startState`` of the automaton turning-off the state represented by
        ``self.answerObjectCells`` of just one place. Note that this will be done for all the
        places in ``self.numberPlaces``.

        ::
        
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
            a                               Automaton                                     a
          xxaxxxxxxxx                                                                     a
          x a       x                                                                     a
          x a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
          x a  o startState o   o tryBindState o   o bindFailState o   o bindDoneState o  a
          x a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
          x a                                                                             a
          x a  ooooooooooooooooooooooooooo   oooooooooooooooooooooooooo                   a
          x a  o retrieveObjectDoneState o   o retrievePlaceDoneState o                   a
          x a  ooooooooooooooooooooooooooo   oooooooooooooooooooooooooo                   a
          x a                                                                             a
          x a                                                                             a
          x a                                                                             a
          x aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
          x
          xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                                                                       x           
            wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww    x
            w                      An Object                      w    x
            w                                                     w    x
            w   oooooooooooooo   oooooooooooooo   oooooooooooooo  w    x
            w   o    binds   o   o   binds    o   o   binds    o  w    x
            w   o    cells   o   o  on-cells  o   o done-cells o  w    x
            w   oooooooooooooo   oooooooooooooo   oooooooooooooo  w    x
            w                                                     w    x
            w   oooooooooooooo   oooooooooooooo                   w    x
            w   o  inquire   o   o   answer   o <xxxxxxxxxxxxxxxxxpxxxxx  <OFF>
            w   o  on-cells  o   o about cell o                   w
            w   oooooooooooooo   oooooooooooooo                   w
            w                                                     w
            w                                                     w
            wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
        
        **NOTE:**
        
        * All the states of an automaton are **not** shown in the above illustration.
        * See :ref:`FSAHelperFunctions` ``.stateTurnsOffState``
        
        """
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.answerObjectCells,objectNumber)

    def statePreventsOutput(self,stateNumber):
        """See :py:meth:`.statePreventsPlaceOutput` and :py:meth:`.statePreventsObjectOutput`"""
        self.statePreventsPlaceOutput(stateNumber)
        self.statePreventsObjectOutput(stateNumber)

    #-----Connect States----
    def connectBindOnState(self):
        """
        The given state of the automaton (see :py:meth:`.createAutomaton`) turns-off the
        ``self.answerObjectCells`` for all the places, i.e. over all ``self.numberPlaces``.
        
        Below shows the ``startState`` of the automaton turning-off the state represented by
        ``self.answerObjectCells`` of just one place. Note that this will be done for all the
        places in ``self.numberPlaces``.

        ::
        
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
            a                               Automaton                                     a
            a                                                                             a
            a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
            a  o startState o   o tryBindState o   o bindFailState o   o bindDoneState o  a
            a  oooooooooooooo   oooooooooooooooo   ooooooooooooooooo   ooooooooooooooooo  a
            a                              x  ^ <OFF>                                     a
            a  ooooooooooooooooooooooooooo x  x oooooooooooooooooooooooooo                a
            a  o retrieveObjectDoneState o x  x o retrievePlaceDoneState o                a
            a  ooooooooooooooooooooooooooo x  x oooooooooooooooooooooooooo                a
            a                     <1/2-ON> V  x                                           a
            a  ooooooooooooooooooooooooo   ooooooooooooooo                                a
            a  o onePlaceOneObjectFact o   o bindOnState o                                a
            a  ooooooooooooooooooooooooo   ooooooooooooooo                                a
            a                    ^   x        ^  x   ;;;;;                                a
            a              <OFF> x   x <STIM> x  x   ;;;;;                                a
            a                    x   xxxxxxxxxx  x   ;;;;;                                a
            a                    xxxxxxxxxxxxxxxxx   ;;;;;                                a
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                                                     ;;;;;
                                                     ;;;;;
                                                   ..;;;;;..
                                                    ':::::'
                                                      ':`
            ttttttttttttttttttttttttttttttttttttttttttttttttttt
            t               tryToBindTimer                    t
            t  ooooooooooooo   ooooooooooooo   ooooooooooooo  t
            t  o  state-0  o   o state-... o   o  state-k  o  t
            t  ooooooooooooo   ooooooooooooo   ooooooooooooo  t
            t                                                 t
            ttttttttttttttttttttttttttttttttttttttttttttttttttt
        
        Note that for the above illustration to be complete the automaton must be connected to
        
        * all the objects and places as shown in :py:meth:`.setupObjectPlaceFacts`
        * see :py:meth:`.statePreventsOutput` but with ``self.bindOnState`` of the automaton, unlike the example in :py:meth:`.statePreventsOutput`
        
        Also,
        
        * All the states of an automaton are **not** shown in the above illustration.
        * See :ref:`FSAHelperFunctions` ``.stateHalfTurnsOnState``
        * See :ref:`FSAHelperFunctions` ``.stateStimulatesState``
        * See :ref:`FSAHelperFunctions` ``.stateTurnsOffState``
        * See :ref:`TimerClass` ``.stateStopsTimer``
        """
        #1p1o fact moves from tryBind to bindOn
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.tryBindState,
                                       self.automatonCells,self.bindOnState)
        self.setupObjectPlaceFacts()
        #Half_on is 0.0012, here we go slower so that it comes up slower
        #if two places is on
        #funnyWt = 0.001
        #if ((self.neal.simulator == 'spinnaker') and (self.neal.spinnVersion == 8)):
        #    funnyWt = 0.0011
        funnyWt = 0.0011

        self.fsa.stateStimulatesState(self.automatonCells,
                        self.onePlaceOneObjectFact,self.automatonCells,
                                      self.bindOnState,funnyWt)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindOnState,
                                       self.automatonCells,self.tryBindState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindOnState,
                                self.automatonCells,self.onePlaceOneObjectFact)
        #stop tryBindTimer
        self.tryToBindTimer.stateStopsTimer(self.automatonCells,
                                            self.bindOnState)

        self.statePreventsOutput(self.bindOnState)
        
    def connectBindFailState(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        #2p, 2o, or timer goes to bindFail 
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.tryBindState,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.twoPlacesFact,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.twoObjectsFact,
                                       self.automatonCells,self.bindFailState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.notEnoughPlaceObjectsFact,self.automatonCells,
                                       self.bindFailState)
        self.tryToBindTimer.timerStartsState(self.automatonCells, #timeout fail
                                            self.notEnoughPlaceObjectsFact)

        #fail prevents on
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.bindOnState)

        #turn states and timers off
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.tryBindState)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.twoPlacesFact)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                                       self.automatonCells,self.twoObjectsFact)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.automatonCells,self.onePlaceOneObjectFact)
        self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.automatonCells,self.notEnoughPlaceObjectsFact)
        self.tryToBindTimer.stateStopsTimer(self.automatonCells,
                                            self.bindFailState)

        #fail goes right back to start
        self.fsa.stateTurnsOnState(self.automatonCells,self.bindFailState,
                            self.automatonCells,self.startState)

    def bindFailStopsPlaceObjectOn(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.placeBindOnCells,placeNumber)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,self.bindFailState,
                            self.objectBindOnCells,objectNumber)

    def bindOnPrimesPlaceAndObjectBind(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,self.bindOnState,
                            self.placeBindCells,placeNumber)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,self.bindOnState,
                            self.objectBindCells,objectNumber)

    def stopPlaceAndObjectBind(self,stateNumber):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.placeBindCells,placeNumber)
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOffState(self.automatonCells,stateNumber,
                            self.objectBindCells,objectNumber)

    def connectBindDoneState(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        #timer moves to binddone
        self.bindingTimer.stateStartsTimer(self.automatonCells, 
                                            self.bindOnState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.bindOnState,
                                       self.automatonCells,self.bindDoneState)
        self.bindingTimer.timerStartsState(self.automatonCells, 
                                            self.bindDoneState)

        self.bindOnPrimesPlaceAndObjectBind()

        self.fsa.stateTurnsOffState(self.automatonCells,self.bindDoneState,
                            self.automatonCells,self.bindOnState)
        self.stopPlaceAndObjectBind(self.bindDoneState)

        #binding done returns to start via timer
        self.bindDoneTimer.stateStartsTimer(self.automatonCells, 
                                            self.bindDoneState)
        self.bindDoneTimer.timerStartsState(self.automatonCells, 
                                            self.startState)

        self.statePreventsOutput(self.bindDoneState)


    def retrieveObjectPrimesPlaceBind(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,
                    self.retrieveObjectState,self.placeBindCells,placeNumber)

    def answerPlaceStartsPlaceRetrievedFact(self):
        """."""
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateTurnsOnState(self.answerPlaceCells,placeNumber,
                    self.automatonCells,self.placeRetrievedFact)

    def connectRetrieveObjectState(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.startState,
                        self.automatonCells,self.retrieveObjectState)
        self.retrieveObjectPrimesPlaceBind()
        self.statePreventsPlaceOutput(self.retrieveObjectState)
        self.answerPlaceStartsPlaceRetrievedFact()
        self.fsa.stateTurnsOffState(self.automatonCells,
                self.retrieveObjectState,self.automatonCells,self.startState)

    def connectRetrieveObjectDoneState(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.retrieveObjectState,self.automatonCells,
                                       self.retrieveObjectDoneState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.objectRetrievedFact,self.automatonCells,
                                       self.retrieveObjectDoneState)
        self.fsa.stateTurnsOffState(self.automatonCells,
            self.retrieveObjectDoneState,self.automatonCells,
                                       self.retrieveObjectState)
        #don't need the output on anymore
        self.statePreventsObjectOutput(self.retrieveObjectDoneState)
        self.stopPlaceAndObjectBind(self.retrieveObjectDoneState)

        self.fsa.stateTurnsOnState(self.automatonCells,
            self.retrieveObjectDoneState,self.automatonCells,
                                       self.startState)

    def retrievePlacePrimesObjectBind(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.automatonCells,
                    self.retrievePlaceState,self.objectBindCells,objectNumber)

    def answerObjectStartsObjectRetrievedFact(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateTurnsOnState(self.answerObjectCells,objectNumber,
                    self.automatonCells,self.objectRetrievedFact)

    def connectRetrievePlaceState(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.stateHalfTurnsOnState(self.automatonCells,self.startState,
                        self.automatonCells,self.retrievePlaceState)
        self.retrievePlacePrimesObjectBind()
        self.statePreventsObjectOutput(self.retrievePlaceState)
        self.answerObjectStartsObjectRetrievedFact()
        self.fsa.stateTurnsOffState(self.automatonCells,
                self.retrievePlaceState,self.automatonCells,self.startState)

    def connectRetrievePlaceDoneState(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.retrievePlaceState,self.automatonCells,
                                       self.retrievePlaceDoneState)
        self.fsa.stateHalfTurnsOnState(self.automatonCells,
            self.placeRetrievedFact,self.automatonCells,
                                       self.retrievePlaceDoneState)
        self.fsa.stateTurnsOffState(self.automatonCells,
            self.retrievePlaceDoneState,self.automatonCells,
                                       self.retrievePlaceState)
        #don't need the output on anymore
        self.statePreventsPlaceOutput(self.retrievePlaceDoneState)
        self.stopPlaceAndObjectBind(self.retrievePlaceDoneState)

        self.fsa.stateTurnsOnState(self.automatonCells,
            self.retrievePlaceDoneState,self.automatonCells,
                                       self.startState)

    def connectAutomaton(self):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.connectStartState()
        self.connectBindOnState()
        self.connectBindFailState()
        self.bindFailStopsPlaceObjectOn()
        self.connectBindDoneState()
        self.connectRetrieveObjectState()
        self.connectRetrievePlaceState()
        self.connectRetrieveObjectDoneState()
        self.connectRetrievePlaceDoneState()

    #def createTimers(self):
        #self.tryToBindTimer = TimerClass(self.simName,self.sim,self.neal,
        #                                 self.spinnVersion,self.fsa,10)
        #self.bindingTimer = TimerClass(self.simName,self.sim,self.neal,
        #                               self.spinnVersion,self.fsa,10)
        #self.bindDoneTimer = TimerClass(self.simName,self.sim,self.neal,
        #                                self.spinnVersion,self.fsa,6)
    def createTimers(self, tryToBindStates=10, bindingStates=10, bindDoneStates=6):
        """
        Given the arguments ``tryToBindStates``, ``bindingStates``, and ``bindDoneStates`` this function creates three timers,
        
        * ``self.tryToBindTimer`` for its given number of states ``tryToBindStates``
        
            - a timer for accounting the time taken for a binding event
        
        * ``self.bindingTimer`` for its given number of states ``bindingStates``
        
            - a timer for binding
        
        * ``self.bindDoneTimer`` for its given number of states ``bindDoneStates``
        
            - a timer for when the binding is achieved
        
        A timer is a collection of cell assemblies such that
        
        * the number of cell assemblies for a timer correspond to the number of possible states of the timer
        * its cell assemblies are connected using :ref:`TimerClass` ``.makeStopNoRestartTimerSynapses``
        
            - the timer goes from state to state and the last stops on its own
            - if the state that turns it ON remains ON, this timer will not restart until its done
        
        Regardless of the state, i.e. the cell assembly, the
        
        * ``self.tryToBindTimer.timerCells``,
        * ``self.bindingTimer.timerCells``, and
        * ``self.bindDoneTimer.timerCells``
        
        are its `neuron population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ for the above timers.
        
        """
        # modified for nmcog
        self.tryToBindTimer.createNeurons( tryToBindStates ) # although default values are set
        self.bindingTimer.createNeurons( bindingStates )     # user can pass custom number of states
        self.bindDoneTimer.createNeurons( bindDoneStates )
        #the timerClass sets recording
        self.tryToBindTimer.makeStopNoRestartTimerSynapses()
        self.bindingTimer.makeStopNoRestartTimerSynapses()
        self.bindDoneTimer.makeStopNoRestartTimerSynapses()

    #def createAutomaton(self): # commented out for nmcog
    def createAutomaton(self, tryToBindStates=10, bindingStates=10, bindDoneStates=6):
        """
        Given the arguments ``tryToBindStates``, ``bindingStates``, and ``bindDoneStates`` this function creates,
        
        * cell assemblies, and
        * three timers (see :py:meth:`.createTimers`)
        
        The cell assemblies are created using :ref:`FSAHelperFunctions` ``.makeCA``. An automaton with five states will therefore have five corresponding cell assemblies as shown below
        
        ::
        
            ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo
            o Automaton o   o Automaton o   o Automaton o   o Automaton o   o Automaton o
            o  state-0  o   o  state-1  o   o  state-2  o   o  state-3  o   o  state-4  o
            ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo   ooooooooooooo
            
        * the number of cell assemblies for *an* automaton is determined by ``self.numberAutomatonStates`` (default = 15)
        * the number of `neuron populations <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ within a cell assembly is given by :ref:`FSAHelperFunctions` ``.CA_SIZE`` (default = 10)
        * the number of neuron units within a population is ``CA_SIZE * numberAutomatonStates`` (default = 150)
        
        This function returns the automaton cells, the prototype `neuron populations <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ used in constructing the above cell assemblies.
        
        """
        numNeurons = self.fsa.CA_SIZE * self.numberAutomatonStates
        
        cells=self.sim.Population(numNeurons,self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        for stateNumber in range (0,self.numberAutomatonStates):
            self.fsa.makeCA(cells,stateNumber)

        #self.createTimers() # commented out for nmcog
        self.createTimers(tryToBindStates=tryToBindStates, bindingStates=bindingStates,
                          bindDoneStates=bindDoneStates)
        #return cells               # replaced for nmcog
        self.automatonCells = cells # with this (i.e, createAutomaton() no longer called in __init__()

    def createObjects(self, numberObjects):
        """For a given ``numberObjects`` this function creates five cell assemblies using :ref:`FSAHelperFunctions` ``.makeCA``
        
        * functionally, one cell assembly each for
        
            - binding the cells
            - binding the on-cells ("on" state of the cells)
            - binding the done-cells ("done" state of the cells)
            - inquiring about the on-cells
            - answering about the cells
        
        * all cell assemblies
        
            - have ``numberObjects`` times :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource`` cells in a `population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_
            - uses the same cell type, `IF_cond_exp <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#pyNN.standardmodels.cells.IF_cond_exp>`_
        
        Therefore each object is represented by five cell assemblies.
        
        ::
    
            oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
            o   CA to bind   o   o   CA to bind   o   o   CA to bind   o
            o object's cells o   o  the on-cells  o   o the done-cells o
            oooooooooooooooooo   oooooooooooooooooo   oooooooooooooooooo
            
            oooooooooooooooooo   oooooooooooooooooo
            o CA to inquire  o   o  CA to answer  o
            o    on-cells    o   o about the cell o
            oooooooooooooooooo   oooooooooooooooooo

        For a population of :math:`n \\times 10` cells the cell assembly comprises of ten such population.
        
        ::
        
            oooooooooooooooooooooooooooooooooooooooooooooooo
            o                                              o
            o   .-.      .-.      .-.      .-.      .-.    o
            o  ( 0 )    ( 2 )    ( 4 )    ( 6 )    ( 8 )   o
            o   '-'      '-'      '-'      '-'      '-'    o
            o                                              o
            o        cell assembly of CA_SIZE = 10         o
            o                                              o
            o   .-.      .-.      .-.      .-.      .-.    o
            o  ( 1 )    ( 3 )    ( 5 )    ( 7 )    ( 9 )   o
            o   '-'      '-'      '-'      '-'      '-'    o
            o                                              o
            oooooooooooooooooooooooooooooooooooooooooooooooo
        
        **NOTE:**
        
        * The value 10 is the default value for :ref:`FSAHelperFunctions` ``.CA_SIZE`
        * See :ref:`FSAHelperFunctions` ``.getCAConnectors` for how the ten populations are connected.
        
        """
        self.numberObjects = numberObjects
        #print 'objects',numberObjects
        numberObjectCells = self.numberObjects*self.fsa.CA_SIZE
        self.objectBindCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.objectBindOnCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.objectBindDoneCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.queryOnObjectCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.answerObjectCells = self.sim.Population(numberObjectCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)

        for objectNumber in range (0,self.numberObjects):
            self.fsa.makeCA(self.objectBindCells,objectNumber)
            self.fsa.makeCA(self.objectBindOnCells,objectNumber)
            self.fsa.makeCA(self.objectBindDoneCells,objectNumber)
            self.fsa.makeCA(self.queryOnObjectCells,objectNumber)
            self.fsa.makeCA(self.answerObjectCells,objectNumber)

    def connectObjects(self):
        """Connects the objects created using :py:meth:`.createObjects`
        
        Connection for an object is done as follows
        
        ::
            
                            <1/2-ON>           <OFF>
            xxxxxxxxx    xxxxxxxxxxxxxx   xxxxxxxxxxxxxxxx
            x       x    V            x   V              x
            x   oooooooooooooo   oooooooooooooo   oooooooooooooo
            x   o    binds   o   o   binds    o   o   binds    o
            x   o    cells   o   o  on-cells  o   o done-cells o
            x   oooooooooooooo   oooooooooooooo   oooooooooooooo
            x       ^    x           <ON>               ^
            x       x    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            x       x <1/2-ON>
            x   oooooooooooooo   oooooooooooooo
            x   o  inquire   o   o   answer   o
            x   o  on-cells  o   o about cell o
            x   oooooooooooooo   oooooooooooooo
            x                           ^
            x          <ON>             x
            xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        
        
        * for <1/2-ON> see :ref:`FSAHelperFunctions` ``.stateHalfTurnsOnState``
        * for <ON> see :ref:`FSAHelperFunctions` ``.stateTurnsOnState``
        * for <OFF> see :ref:`FSAHelperFunctions` ``.stateTurnsOffState``
        
        """
        for objectNumber in range (0,self.numberObjects):
            self.fsa.stateHalfTurnsOnState(self.objectBindOnCells,objectNumber,
                                       self.objectBindCells,objectNumber)
            self.fsa.stateTurnsOnState(self.objectBindCells,objectNumber,
                                       self.objectBindDoneCells,objectNumber)
            self.fsa.stateTurnsOffState(self.objectBindDoneCells,objectNumber,
                                       self.objectBindOnCells,objectNumber)
            self.fsa.stateHalfTurnsOnState(self.queryOnObjectCells,objectNumber,
                                       self.objectBindCells,objectNumber)
            self.fsa.stateTurnsOnState(self.objectBindCells,objectNumber,
                                       self.answerObjectCells,objectNumber)

    #Create neurons for each place and make them CAs.
    def createPlaces(self, numberPlaces):
        """See :py:meth:`.createObjects`"""
        self.numberPlaces = numberPlaces
        #print('places',numberPlaces)
        numberPlaceCells = self.numberPlaces*self.fsa.CA_SIZE
        self.placeBindCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.placeBindOnCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.placeBindDoneCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.queryOnPlaceCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)
        self.answerPlaceCells = self.sim.Population(numberPlaceCells,
                self.sim.IF_cond_exp,self.fsa.CELL_PARAMS)

        for placeNumber in range (0,self.numberPlaces):
            self.fsa.makeCA(self.placeBindCells,placeNumber)
            self.fsa.makeCA(self.placeBindOnCells,placeNumber)
            self.fsa.makeCA(self.placeBindDoneCells,placeNumber)
            self.fsa.makeCA(self.queryOnPlaceCells,placeNumber)
            self.fsa.makeCA(self.answerPlaceCells,placeNumber)

    def connectPlaces(self):
        """See :py:meth:`.connectObjects`"""
        for placeNumber in range (0,self.numberPlaces):
            self.fsa.stateHalfTurnsOnState(self.placeBindOnCells,placeNumber,
                                       self.placeBindCells,placeNumber)
            self.fsa.stateTurnsOnState(self.placeBindCells,placeNumber,
                                       self.placeBindDoneCells,placeNumber)
            self.fsa.stateTurnsOffState(self.placeBindDoneCells,placeNumber,
                                       self.placeBindOnCells,placeNumber)
            self.fsa.stateHalfTurnsOnState(self.queryOnPlaceCells,placeNumber,
                                       self.placeBindCells,placeNumber)
            self.fsa.stateTurnsOnState(self.placeBindCells,placeNumber,
                                       self.answerPlaceCells,placeNumber)

    def setupCogMapRecording(self):
        """Record spikes for
        
        +-----------------------------------------------+---------------------------------------------+
        | cell assemblies (i.e. state) within an Object | cell assemblies (i.e. state) within a Place |
        +===============================================+=============================================+
        | ``self.objectBindCells``                      | ``self.placeBindCells``                     |
        +-----------------------------------------------+---------------------------------------------+
        | ``self.objectBindOnCells``                    | ``self.placeBindOnCells``                   |
        +-----------------------------------------------+---------------------------------------------+
        | ``self.objectBindDoneCells``                  | ``self.placeBindDoneCells``                 |
        +-----------------------------------------------+---------------------------------------------+
        | ``self.queryOnObjectCells``                   | ``self.queryOnPlaceCells``                  |
        +-----------------------------------------------+---------------------------------------------+
        | ``self.answerObjectCells``                    | ``self.answerPlaceCells``                   |
        +-----------------------------------------------+---------------------------------------------+
        
        and also for ``self.automatonCells``
        
        """
        self.placeBindCells.record({'spikes'})
        self.objectBindCells.record({'spikes'})
        self.automatonCells.record({'spikes'})
        self.placeBindOnCells.record({'spikes'})
        self.objectBindOnCells.record({'spikes'})
        self.placeBindDoneCells.record({'spikes'})
        self.objectBindDoneCells.record({'spikes'})
        self.queryOnPlaceCells.record({'spikes'})
        self.queryOnObjectCells.record({'spikes'})
        self.answerPlaceCells.record({'spikes'})
        self.answerObjectCells.record({'spikes'})

    def getWellConnectedConn(self,fromSize,toSize,weight):
        """."""
        connector = []
        for fromNeuron in range (0,fromSize):
            for toNeuron in range (0, toSize):
                connector=connector+[(fromNeuron,toNeuron,weight,
                                      self.neal.DELAY)]
        return connector

    def makeLearningSynapses(self):
        """See :ref:`FSAHelperFunctions` ``.CA_SIZE``"""
        numberPlaceBindCells = self.numberPlaces*self.fsa.CA_SIZE
        numberObjectBindCells = self.numberObjects*self.fsa.CA_SIZE
        synWeight = 0.0

        placeToObjectConnector = self.getWellConnectedConn(
            numberPlaceBindCells,numberObjectBindCells,synWeight)
        placeToObjectConnList = self.sim.FromListConnector(
            placeToObjectConnector)

        objectToPlaceConnector = self.getWellConnectedConn(
            numberObjectBindCells,numberPlaceBindCells,synWeight)
        objectToPlaceConnList = self.sim.FromListConnector(
            objectToPlaceConnector)
        stdp_model = self.sim.STDPMechanism(
                timing_dependence = self.sim.SpikePairRule(tau_plus=16.0, 
                                tau_minus=3.0,A_plus=0.002, A_minus=0.0),
                #timing_dependence = self.sim.SpikePairRule(tau_plus=16.7, 
                #                tau_minus=3.7,A_plus=0.002, A_minus=0.0),
                                #tau_minus=3.7,A_plus=0.005, A_minus=0.0),#works
                                #tau_minus=3.7,A_plus=0.001, A_minus=0.0002),
                                #tau_minus=0.01,A_plus=0.005, A_minus=0.002),
                weight_dependence = self.sim.AdditiveWeightDependence(
                    w_min=0.0, w_max=0.004) 
                    #w_min=0.0, w_max=0.015) #.015 .004 .0015
                    #w_min=0.0, w_max=0.02) 
            )

        self.sim.Projection(self.placeBindCells,self.objectBindCells,
                            self.sim.AllToAllConnector(),
                            #placeToObjectConnList,
                            synapse_type=stdp_model)

        self.sim.Projection(self.objectBindCells,self.placeBindCells,
                            #objectToPlaceConnList,
                            self.sim.AllToAllConnector(),
                            synapse_type=stdp_model)
        #print 'bob', placeToObjectConnector
        #print objectToPlaceConnector

    #---Defs for turning things on and off with spike sources.
    def sourceTurnsOnPlace(self, placeNumber, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.turnOnStateFromSpikeSource(source,self.placeBindCells,
                                            placeNumber)
    def sourceTurnsOffPlace(self, placeNumber, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.turnOffStateFromSpikeSource(source,self.placeBindCells,
                                            placeNumber)

    def sourceTurnsOnObject(self, objectNumber, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.turnOnStateFromSpikeSource(source,self.objectBindCells,
                                            objectNumber)
    def sourceTurnsOffObject(self, objectNumber, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.turnOffStateFromSpikeSource(source,self.objectBindCells,
                                            objectNumber)

    def sourceTurnsOnBind(self, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.halfTurnOnStateFromSpikeSource(source,self.automatonCells,
                                                self.tryBindState)

    def sourceTurnsOnObjectOn(self, objectNumber, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.turnOnStateFromSpikeSource(source,self.objectBindOnCells,
                                            objectNumber)

    def sourceTurnsOnPlaceOn(self, placeNumber, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.turnOnStateFromSpikeSource(source,self.placeBindOnCells,
                                            placeNumber)

    def sourceStartsAutomaton(self, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.turnOnStateFromSpikeSource(source,self.automatonCells,
                                             self.startState)

    def sourceTurnOnRetrieveObjectFromPlace(self, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.halfTurnOnStateFromSpikeSource(source,self.automatonCells,
                                                self.retrieveObjectState)

    def sourceTurnOnRetrievePlaceFromObject(self, source):
        """See :ref:`FSAHelperFunctions` ``.halfTurnOnStateFromSpikeSource``"""
        self.fsa.halfTurnOnStateFromSpikeSource(source,self.automatonCells,
                                                self.retrievePlaceState)

    def sourceTurnsOnPlaceQuery(self, source,placeNumber):
        """See :ref:`FSAHelperFunctions` ``.turnOnStateFromSpikeSource``
        This is meant for place cells unlike :py:meth:`.sourceTurnsOnObjectQuery`"""
        self.fsa.turnOnStateFromSpikeSource(source,self.queryOnPlaceCells,
                                            placeNumber)

    def sourceTurnsOnObjectQuery(self, source,objectNumber):
        """Given a `spikeSource <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ ,
        this method turns **ON** the state of the object cells; the cells are collectively in the form of a
        `PyNN population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_.
        
        The object cells collectively is part of an object identified by its ``objectNumber``
        
        **NOTE:**
        
        * See :ref:`FSAHelperFunctions` ``.turnOnStateFromSpikeSource``
        * Althought
        * This is meant for objects unlike :py:meth:`.sourceTurnsOnPlaceQuery`
        
        """
        self.fsa.turnOnStateFromSpikeSource(source,self.queryOnObjectCells,
                                            objectNumber)

    def printCogMapNets(self):
        """Legacy."""
        suffix = '.pkl'
        self.placeBindCells.write_data('results/cmPlaceBind'+suffix)
        self.objectBindCells.write_data('results/cmObjectBind'+suffix)
        self.automatonCells.write_data('results/cmAutomaton'+suffix)
        self.placeBindOnCells.write_data('results/cmPlaceBindOn'+suffix)
        self.objectBindOnCells.write_data('results/cmObjectBindOn'+suffix)
        self.placeBindDoneCells.write_data('results/cmPlaceBindDone'+suffix)
        self.objectBindDoneCells.write_data('results/cmObjectBindDone'+suffix)
        self.queryOnPlaceCells.write_data('results/cmQueryOnPlace'+suffix)
        self.queryOnObjectCells.write_data('results/cmQueryOnObject'+suffix)
        self.answerPlaceCells.write_data('results/cmAnswerPlace'+suffix)
        self.answerObjectCells.write_data('results/cmAnswerObject'+suffix)
        self.tryToBindTimer.printResults('results/cmTryToBindTimer')
        self.bindingTimer.printResults('results/cmBindingTimer')
        self.bindDoneTimer.printResults('results/cmBindDoneTimer')
