#!/usr/bin/python
"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit
import itertools
# patch isShellBuiltin
import re
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
import random
import pickle


REF_BANDWIDTH = 500
blacklist = [('r3', 'r6'), ('r6', 'r3'), ('r4', 'r1')]
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
    for sw in net.switches:
        sw.start([c])    
    
    # waiting for ospf to converge
    info('\n** Waiting for OSPF to converge\n')
    time.sleep(60)
    simulateTraffic(net)

#    info("** Enabling spanning tree on switches\n")
    
    #info('** Dumping host connections\n')
    #dumpNodeConnections(net.hosts)

    #info('** Testing network connectivity\n')
    # net.ping(net.hosts)
    
    #info('** Dumping host processes\n')
    #for host in net.hosts:
    #    host.cmdPrint("ps aux")

    #info('** Running CLI\n')
    #CLI(net)


def simulateTraffic(net):

    #print(hosts)
    valid = []
    with open('addresses.pkl', 'rb') as f:
        rout_addr = pickle.load(f)
    
    with open('addr_rout.pkl', 'rb') as f:
        addr_rout = pickle.load(f)

    for host in net.hosts:
        if 'i' not in host.name:
            valid.append(host)
            info('*** Starting iperf server on {:}\n'.format(host.name))
            host.cmd('pkill iperf')
            # using & allows to nonblocking cmd
            host.cmd('iperf -s &', printPid=True)
    
    valid_addr = []
    for host in valid:
        valid_addr.extend(rout_addr[host.name])

    info('***Starting traffic simulation\n')
    # list of (src_router, dst_ip)
    combinations =  list(itertools.product(valid, valid_addr))
    
    while True:
        random.shuffle(combinations)
        #print(combinations)
        for s, d in combinations:
            d_name = addr_rout[d]
            if is_valid_path(s.name,d_name):
                s.cmd('iperf -t {:} -c {:} &'.format(random.randint(1,5),d))

                    
def is_valid_path(s,d):
    if s==d:
        return False

    #if 'i' in s or 'i' in d:
    #    return False

    #if s == 'r5' or d == 'r5':
    #    return False

    if (s,d) in blacklist:
        return False

    return True

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
            conf.write("\nlog file /var/log/quagga/{:}.log\n".format(router))
            conf.write("\nrouter ospf\n")
            conf.write("auto-cost reference-bandwidth {:}\n".format(REF_BANDWIDTH))
            for network in networks[router]:
                conf.write("  network {:}\n".format(network))


# get network address from host, to be implemented
def getNetwork(address, prefix):
    return re.sub("([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+", "\\1.0", address)

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
