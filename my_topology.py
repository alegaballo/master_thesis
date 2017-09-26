from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import logging
import random

logger = logging.getLogger()

class CustomTopology(Topo):
    def build(self, inner=4, outer=12):
        hosts=[]
        outer_s=[]
        hosts.append(self.addHost('h1'))
        outer_s.append(self.addSwitch('s1'))
        self.addLink(hosts[0], outer_s[0])
        for i in range(1, outer):
            hosts.append(self.addHost('h{:}'.format(i+1)))
            outer_s.append(self.addSwitch('s{:}'.format(i+1)))
            # connecting each outer switch to a host
            self.addLink(hosts[i], outer_s[i])
            logger.info('created link s{:}-h{:}'.format(i+1, i+1))
            try:
                self.addLink(outer_s[i-1], outer_s[i])
                logger.info('created link h{:}-h{:}'.format(i+1, i))
            except Exception:
                logger.warning('can\' create link h{:}-h{:}'.format(i+1, i))
        # closing the ring
        self.addLink(outer_s[0], outer_s[-1])
        logger.info('created link s{:}-h{:}'.format(i+1, 0))
        # creating inner ring
        inner_s = []
        inner_s.append(self.addSwitch('is1'))
        for i in range (1, inner):
            inner_s.append(self.addSwitch('is{:}'.format(i+1)))
            self.addLink(inner_s[i-1], inner_s[i])
        self.addLink(inner_s[0], inner_s[-1])
        
        for i_s in inner_s:
            self.addLink(i_s, outer_s.pop(random.randint(0, len(outer_s)-1)))
            self.addLink(i_s, outer_s.pop(random.randint(0, len(outer_s)-1)))

def start_network():
    topo = CustomTopology()
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.stop()


if __name__=='__main__':
    setLogLevel('info')
    start_network()
    
