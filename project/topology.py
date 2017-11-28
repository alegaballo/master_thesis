import inspect
import os
from random import randint 
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService
from collections import namedtuple

QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None
OUTER = 6
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
        
        # creating custom connections between inner and outer rings
        self.addLinkWithSwitch(outer[0], inner[1], self.addSwitch("sio1",protocols='OpenFlow13'))       
        self.addLinkWithSwitch(outer[2], inner[1], self.addSwitch("sio2", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[2], inner[2], self.addSwitch("sio3", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[3], inner[3], self.addSwitch("sio4", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[5], inner[3], self.addSwitch("sio5", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[5], inner[0], self.addSwitch("sio6", protocols='OpenFlow13'))
        
        
        
        
        

    def createQuaggRing(self, n, quaggaSvc, quaggaBaseConfigPath, r_name="r{:d}", s_name="s{:d}", bw=None):
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
            switches.append(self.addSwitch(s_name.format(i+1),protocols='OpenFlow13'))

        num_routers = len(routers)
        for i in range(num_routers):
            self.addLinkWithSwitch(routers[i], routers[(i+1)%num_routers], switches[i], bw)
            #self.addLink(routers[i], routers[(i+1)%num_routers])
        return routers 
    
    def addLinkWithSwitch(self, r1, r2, s, bw=None):
        bw=randint(5,200)
        self.addLink(r1,s, bw=bw)
        self.addLink(s,r2, bw=bw)
        
