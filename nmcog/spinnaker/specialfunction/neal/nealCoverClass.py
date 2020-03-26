# ~/nmcog/spinnaker/specialfunction/neal/nealCoverClass.py
#
# Documentation by Lungsi 25 March 2020
#
import spynnaker8 as sim # added for nmcog

class NealCoverFunctions:
    """Functions to isolate differences between different list synapse constructors.
    
    +----------------------------------+--------------------------------------------------------------------------------------------------------------------------------+------------------------------------+
    | Methods                          |  Argument                                                                                                                      | Caller                             |
    +==================================+================================================================================================================================+====================================+
    | :py:meth:`.nealProjection`       | - projection from a `PyNN based spike source <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ | usually to connect between two     |
    |                                  |or a `PyNN based Population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_                                  |populations between cell assemblies |
    |                                  | - projection into another `PyNN based Population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_            |                                    |
    |                                  | - a list of connection parameter                                                                                               |                                    |
    |                                  | - string describing the connection type; "excitatory" or "inhibitory"                                                          |                                    |
    +----------------------------------+--------------------------------------------------------------------------------------------------------------------------------+------------------------------------+
    | :py:meth:`.sameProjectionType`   | - two projections                                                                                                              | :py:meth:`.nealApplyProjections`   |
    +----------------------------------+--------------------------------------------------------------------------------------------------------------------------------+------------------------------------+
    | :py:meth:`.nealApplyProjections` | - (class must be instantiated because ``self.projections`` would have been the argument if this method had one)                |                                    |
    +----------------------------------+--------------------------------------------------------------------------------------------------------------------------------+------------------------------------+
    
    
    **Note:**
    
    * The `PyNN based Population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_ is usually a population within a cell assembly.
    * The list of connection parameter is of the form such that
    
        - first element is the projection source (i.e. `PyNN based spike source <http://neuralensemble.org/docs/PyNN/reference/neuronmodels.html#spike-sources>`_ or `PyNN based Population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_)
        - second element is the projection target (usually another `PyNN based Population <http://neuralensemble.org/docs/PyNN/reference/populations.html>`_)
        - third element is a float type value representing weight value
        - fourth element is the ``self.DELAY`` (default = 0.1)
    
    * The two projections must each be a list of the form ``[preNeurons, postNeurons, inhExc]`` or ``[preNeurons, postNeurons, inhExc, connectorList]``.
    
    """

    projections = []
    
    #def __init__(self, simName,sim,spinnVersion):
    def __init__(self, simName="spinnaker", spinnVersion=8): # modified for nmcog
        self.DELAY = 1.0
        self.simulator = simName
        self.sim = sim
        self.spinnVersion = spinnVersion

    def nealProjection(self,preNeurons,postNeurons,connectorList,inhExc):
        """Given ``preNeurons``, ``postNeurons``, ``connectorList``, and ``inhExc`` (string, "inhibitory" or "excitatory") these four arguments are put
        into a list and reordered such that ``inhExc`` goes in front of ``connectorList``.
        The list is then appended to the class attribute ``self.projections``, a list.
        """
        newProjection = [preNeurons,postNeurons,inhExc,connectorList]
        self.projections.append(newProjection)

    def sameProjectionType(self,projectionA,projectionB):
        """Checks if two given projections (between two cell assemblies) are of the same type. Returns Boolean. Note these projections are **not** ``self.projections``."""
        if ((projectionA[0] == projectionB[0]) and # pre Neurons 
            (projectionA[1] == projectionB[1]) and # post Neurons
            (projectionA[2] == projectionB[2])):   # inh or exc
            return True
        return False

    #collect the projections into projections that are pre post and type
    #specific.  Write those out in one fromList
    def nealApplyProjections(self):
        """Collect the projections (i.e. ``self.projections``) into projections that are pre post and type specific (via :py:meth:`.sameProjectionType`).
        And write them into one fromList."""
        while (len(self.projections) > 0):
            projectionNumber = 0
            #get the first projection and collect all projections like it
            firstProjection = self.projections[0]
            connList = firstProjection[3]
            self.projections.remove(firstProjection)
            while (projectionNumber < len(self.projections)):
                if (self.sameProjectionType(self.projections[projectionNumber],
                           firstProjection)):
                    connList = connList + self.projections[projectionNumber][3]
                    #print projectionNumber,len(connList)
                    self.projections.remove(self.projections[projectionNumber])
                else:
                    projectionNumber = projectionNumber + 1
                    
            #actually put out the projections
            fromListConnector = self.sim.FromListConnector(connList)
            preNeurons = firstProjection[0]
            postNeurons = firstProjection[1]
            inhExc = firstProjection[2]
            if ((self.simulator=="spinnaker") and (self.spinnVersion==7)):
                self.sim.Projection(preNeurons, postNeurons, fromListConnector,
                                   target=inhExc)
            elif ((self.simulator=="nest") or
              ((self.simulator=="spinnaker") and (self.spinnVersion==8))):
                    self.sim.Projection(preNeurons, postNeurons, fromListConnector,
                                   receptor_type=inhExc)
            
            else: print("bad simulator nealProjection")