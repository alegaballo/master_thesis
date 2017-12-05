#!/usr/bin/python
"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit
import itertools
# patch isShellBuiltin
import time
import mininet.util
import mininext.util
mininet.util.isShellBuiltin = mininext.util.isShellBuiltin
sys.modules['mininet.util'] = mininet.util

from mininet.util import dumpNodeConnections
from mininet.node import RemoteController
#from mininet.node import Ryu
from mininet.log import setLogLevel, info
from mininet.link import TCLink

from mininext.cli import CLI
from mininext.net import MiniNExT

from topology import MyTopo

net = None


def startNetwork():
    "instantiates a topo, then starts the network and prints debug information"

    info('** Creating Quagga network topology\n')
    topo = MyTopo()

    info('** Starting the network\n')
    global net
    net = MiniNExT(topo, controller=None, link=TCLink)
    c=net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633) 

    #net = MiniNExT(topo, controller=Ryu) 

    info('** Configuring addresses on interfaces\n')
    setInterfaces(net, "configs/interfaces")
    net.start()
    #waiting for OSPF to converge
 #   time.sleep(90)
  #  simulateTraffic(net,topo.hosts())
#    info("** Enabling spanning tree on switches\n")
    for sw in net.switches:
#        sw.sendCmd('ovs-vsctl set bridge {:}  stp-enable=true'.format(sw))
        sw.start([c])    

    info('** Dumping host connections\n')
    dumpNodeConnections(net.hosts)

    info('** Testing network connectivity\n')
    # net.ping(net.hosts)

    info('** Dumping host processes\n')
    for host in net.hosts:
        host.cmdPrint("ps aux")

    info('** Running CLI\n')
    CLI(net)


def simulateTraffic(net, hosts):
    print(hosts)
    for s, d in itertools.product(hosts, hosts):
        if s != d:
            print(s, d)
            net.iperf([net.get(s),net.get(d)])

def setInterfaces(net, confFile):
    # conf file: router interface address
    networks = {}
    with open(confFile) as conf:
        for line in conf.readlines():
            params = line.strip()
            if params and params[0] == "#":
                continue
            elif params:
                router, interface, ip = params.split(" ")
#                print(params)
                net.get(router).setIP(ip, 24, interface)
                # checking if switch or router
                if "s" in router:
                    continue
                if not router in networks:
                    networks[router] = set([])
                networks[router].add(getNetwork(ip, 24)+"/24 area 0")
    createQuaggaConfig(networks)


def createQuaggaConfig(networks):
    CONFIG_PATH = "./configs/"
    for router in networks:
        with open(CONFIG_PATH+router+"/ospfd.conf", "w+") as conf:
            conf.write("hostname {:}\n".format(router))
            # conf.write("password {:}\n".format(router))
            # conf.write("enable password {:}\n".format(router))
            conf.write("\nlog file /var/log/quagga/{:}.log\n".format(router))
            conf.write("\nrouter ospf\n")
            for network in networks[router]:
                conf.write("  network {:}\n".format(network))


# get network address from host, to be implemented
def getNetwork(address, prefix):
    return address[:-1]+"0"


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
