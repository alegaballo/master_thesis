from __future__ import print_function 
import re
import os
import ipaddr as ip
from collections import defaultdict


ROUTES_FILE = '/home/mininet/miniNExT/util/routes.txt'
ROUTER_CONF = '/home/mininet/miniNExT/examples/master_thesis/project/configs/interfaces'


def parse_routes(routes_file, addr_file):
    destinations = set()
    routers = set()
    # contains the networks to which the routers is directly connected [probably useless]
    connected_networks = defaultdict(list)
    # map each router to its list of addresses
    addresses = defaultdict(list)
    # map each address to the router
    addr_rout = defaultdict()
    # contains the routing information: dst->next_hop
    routes = defaultdict(dict)
    # getting routers routing tables
    with open(routes_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                router, network, next_hop = line.split()
                routers.add(router)
                
                if _is_same_network(next_hop):
                    connected_networks[router].append(network)
                routes[router][network] = next_hop

    # getting routers address configuration
    with open(addr_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                router, interface, address = line.split()
                addresses[router].append(address)
                destinations.add(address)
    
    routers = sorted(routers)
    connected_routers = invert_dict(connected_networks)
    addr_rout=invert_dict(addresses, type='')
    get_path('r1', '172.168.2.2', routes, addr_rout)


def get_path(src_router, dst_addr, routes, addr_rout):
    next_hop = routes[src_router][_addr_to_net(dst_addr)]
    path = [src_router]
    while next_hop!='0.0.0.0':
            src_router=addr_rout[next_hop]
            next_hop = routes[src_router][_addr_to_net(dst_addr)]
            path.append(src_router)
   
    # it is possible to reach an ip through another interface, need to double check
    last = addr_rout[dst_addr]
    if last != path[-1]:
        path.append(addr_rout[dst_addr])
    _print_path(path)


def _print_path(path):
    print(path[0], end=' ')
    for hop in path[1:]:
        print('-> ' + hop, end=' ')
    print()


# all my networks are /24, not a proper implementet method, just putting a 0 instead of the host
def _addr_to_net(addr, prefix=24):
    return re.sub("([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+", "\\1.0", addr)

def _is_same_network(next_hop):
    return next_hop=='0.0.0.0'

def _get_connected_router(src, addresses):
    net = _addr_to_net(src)
    print(net)
    for addr in addresses:
        if _addr_to_net(addr) == net and addr !=src:
            return addr


# to be reimplemented as 2 separate methods
def invert_dict(dic, type='list'):
    inverted = defaultdict(list)
    if type != 'list':
        inverted = defaultdict()
    
    for k,v in dic.items():
        for item in v:
            if type != 'list':
                inverted[item]=k
            else:
                inverted[item].append(k)
    return dict(inverted)

    
parse_routes(ROUTES_FILE, ROUTER_CONF)

