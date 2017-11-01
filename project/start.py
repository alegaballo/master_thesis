#!/usr/bin/python

"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit

# patch isShellBuiltin
import mininet.util
import mininext.util
mininet.util.isShellBuiltin = mininext.util.isShellBuiltin
sys.modules['mininet.util'] = mininet.util

from mininet.util import dumpNodeConnections
from mininet.node import OVSController
from mininet.log import setLogLevel, info

from mininext.cli import CLI
from mininext.net import MiniNExT

from topology import MyTopo

net = None

routers = {"r1":["172.168.0.1","172.168.3.2"], "r2":["172.168.0.2","172.168.1.1"], 
        "r3":["172.168.1.2","172.168.2.1"], "r4": ["172.168.2.2","172.168.3.1"]}

def startNetwork():
    "instantiates a topo, then starts the network and prints debug information"

    info('** Creating Quagga network topology\n')
    topo = MyTopo()

    info('** Starting the network\n')
    global net
    net = MiniNExT(topo, controller=OVSController)
    
    info('** Configuring addresses on interfaces\n')
    setInterfaces(net, "configs/interfaces")
#    for router in routers:
#        print(router)
#        net.get(router).setIP(routers[router][0], 24, "{:s}-eth0".format(router))
#        net.get(router).setIP(routers[router][1], 24, "{:s}-eth1".format(router))
#
    net.start()
    net.start()

    info('** Dumping host connections\n')
    dumpNodeConnections(net.hosts)

    info('** Testing network connectivity\n')
    net.ping(net.hosts)

    info('** Dumping host processes\n')
    for host in net.hosts:
        host.cmdPrint("ps aux")

    info('** Running CLI\n')
    CLI(net)

def setInterfaces(net, confFile):
    with open(confFile) as conf:
        for line in conf.readlines():
            params = line.strip()
            if params:
                params = params.split(" ")
                print(params)
                net.get(params[0]).setIP(params[2], params[1])

def stopNetwork():
    "stops a network (only called on a forced cleanup)"

    if net is not None:
        info('** Tearing down Quagga network\n')
        net.stop()

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
