import inspect
import os
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService
from collections import namedtuple

QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None
OUTER = 12
INNER = 4

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        # Directory where this file / script is located"
        selfPath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))  # script directory

        # Initialize a service helper for Quagga with default options
        quaggaSvc = QuaggaService(autoStop=False)

        # Path configurations for mounts
        quaggaBaseConfigPath = selfPath + '/configs/'
        outer = self.createQuaggRing(OUTER, quaggaSvc, quaggaBaseConfigPath)
        inner = self.createQuaggRing(INNER, quaggaSvc, quaggaBaseConfigPath, r_name="ri{:d}", s_name="si{:d}")
        idx=[1,3,4,6,7,9,10,11] # indexes of the outer routers to connect with the inners
        j=0
        for i, ix in enumerate(idx):
            sw = self.addSwitch("sio{:d}".format(i+1))
            self.addLinkWithSwitch(inner[j],outer[ix],sw)     
            j+=i%2 # 2 outer per each inner
        
    def createQuaggRing(self, n, quaggaSvc, quaggaBaseConfigPath, r_name="r{:d}", s_name="s{:d}"):
        routers = []
        switches = []
        for i in range(n): 
            quaggaContainer = self.addHost(name=r_name.format(i+1),
                                            hostname=r_name.format(i+1),
                                            privateLogDir=True,
                                            privateRunDir=True,
                                            inMountNamespace=True,
                                            inPIDNamespace=True,
                                            inUTSNamespace=True)
            quaggaSvcConfig = {'quaggaConfigPath': quaggaBaseConfigPath + r_name.format(i+1)}
            self.addNodeService(node=r_name.format(i+1), service=quaggaSvc,
                                nodeConfig=quaggaSvcConfig)
            routers.append(quaggaContainer)
            switches.append(self.addSwitch(s_name.format(i+1)))

        num_routers = len(routers)
        for i in range(num_routers):
            self.addLinkWithSwitch(routers[i], routers[(i+1)%num_routers], switches[i])
        return routers 
    
    def addLinkWithSwitch(self, r1, r2, s):
        self.addLink(r1,s)
        self.addLink(s,r2)
