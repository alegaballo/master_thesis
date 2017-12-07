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
    # contains all the address associated to each router
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
    get_path('r1', '172.168.4.1', routes, addr_rout)

def get_path(src_router, dst_addr, routes, addr_rout):
    next_hop = ''
    while next_hop!='0.0.0.0':
        next_hop = routes[src_router][_addr_to_net(dst_addr)]
        print(src_router + '-> ' + next_hop)
        src_router=addr_rout[next_hop]

# all my networks are /24, not a proper implementet method, just putting a 0 instead of the host
def _addr_to_net(addr, prefix=24):
    return re.sub("([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+", "\\1.0", addr)

def _is_same_network(next_hop):
    return next_hop=='0.0.0.0'

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
