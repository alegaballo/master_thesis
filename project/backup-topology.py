import inspect
import os
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService
from collections import namedtuple

QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None

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
        
        quaggaInner = []
        routers = []
        switches = []
        for i in range(4):
            router="r{:d}".format(i+1)
            quaggaContainer = self.addHost(name=router,
                                            hostname=router,
                                            privateLogDir=True,
                                            privateRunDir=True,
                                            inMountNamespace=True,
                                            inPIDNamespace=True,
                                            inUTSNamespace=True)
            quaggaSvcConfig = {'quaggaConfigPath': quaggaBaseConfigPath + router}
            self.addNodeService(node=router, service=quaggaSvc,
                                nodeConfig=quaggaSvcConfig)
            routers.append(quaggaContainer)
            switches.append(self.addSwitch("s{:d}".format(i+1)))

        num_routers = len(routers)
        for i in range(num_routers):
            self.addLink(routers[i], switches[i])
            self.addLink(switches[i], routers[(i+1)%num_routers])

