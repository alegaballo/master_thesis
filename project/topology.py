import inspect
import os
from random import randint 
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService
from collections import namedtuple
import pickle


OUT_DIR='/home/mininet/miniNExT/examples/master_thesis/project/'
QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None
OUTER = 6
INNER = 4
IN_BW = 1000

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
        
        # Initialize data structure to map each router with the port on the switch corresponding to incoming traffic
        self.in_interface = {}
        # saving speed of each interface
        self.intf_speed = {}
        outer = self.createQuaggRing(OUTER, quaggaSvc, quaggaBaseConfigPath)
        
        # inner = self.createQuaggRing(INNER, quaggaSvc, quaggaBaseConfigPath, r_name="ri{:d}", s_name="si{:d}")
        # test with different naming because of problem with contorller
        inner = self.createQuaggRing(INNER, quaggaSvc, quaggaBaseConfigPath, r_name="ri{:d}", count=OUTER, bw=IN_BW)
        
        # creating custom connections between inner and outer rings
        self.addLinkWithSwitch(outer[0], inner[1], self.addSwitch("s11",protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[2], inner[1], self.addSwitch("s12", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[2], inner[2], self.addSwitch("s13", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[3], inner[3], self.addSwitch("s14", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[5], inner[3], self.addSwitch("s15", protocols='OpenFlow13'))
        self.addLinkWithSwitch(outer[5], inner[0], self.addSwitch("s16", protocols='OpenFlow13'))
        
        # saving mapping on file
        with open(OUT_DIR + 'switch_mapping.pkl', 'wb+') as f:
            pickle.dump(self.in_interface, f)
            
        # saving intf speed on file
        with open(OUT_DIR + 'intf_speed.pkl', 'wb+') as f:
            pickle.dump(self.intf_speed, f)

    def createQuaggRing(self, n, quaggaSvc, quaggaBaseConfigPath, r_name="r{:d}", s_name="s{:d}", count=0, bw=None):
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
            switches.append(self.addSwitch(s_name.format(count + i + 1),protocols='OpenFlow13'))

        num_routers = len(routers)
        for i in range(num_routers):
            self.addLinkWithSwitch(routers[i], routers[(i+1)%num_routers], switches[i], bw)
            #self.addLink(routers[i], routers[(i+1)%num_routers])
        return routers 
    
    def addLinkWithSwitch(self, r1, r2, s, bw=None):
        if not bw:
            # from Ethernet 10Base-X to Gigabit Ethernet
            bw=randint(100, 800)
        self.addLink(r1,s, bw=bw)
        self.addLink(s,r2, bw=bw)
        # saving the port on the switch for incoming traffic on the specific router
        #self.in_interface.append("{:} {:} 2".format(r1, s))
        #self.in_interface.append("{:} {:} 1".format(r2, s))
        self.addIntfSpeed(r1, bw)
        self.addIntfSpeed(r2, bw)

        if s not in self.in_interface:
            self.in_interface[s]={}
        self.in_interface[s][r1]=2
        self.in_interface[s][r2]=1
        

    def addIntfSpeed(self, router, bw):
        i = 0
        while True:
            intf = '{:}-eth{:d}'.format(router, i)
            if intf.format(router, i) not in self.intf_speed:
                self.intf_speed[intf] = bw * 1000
                break
            i += 1

