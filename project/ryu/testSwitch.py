#!/usr/bin/python3.4
# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#from keras.models import load_model
#from keras import backend as K
from ryu.controller.dpset import DPSet
from ryu.base import app_manager
from ryu.controller import event
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib import hub
from ryu.app.ofctl import api
from collections import defaultdict
import pickle
import time
import os
import numpy as np
from multiprocessing.connection import Client

EMPTY_COUNTER = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]
ROUTERS_NAMING = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'ri1', 'ri2', 'ri3', 'ri4']
POLLING_INTERVAL = 1
OUT_DIR = '/home/mininet/miniNExT/examples/master_thesis/project/'
MODELS_DIR = '/home/mininet/miniNExT/examples/master_thesis/project/models_final/'
ITERATION = 15
ROUTER_CONF = '/home/mininet/miniNExT/examples/master_thesis/project/configs/interfaces'

class EventMsg(event.EventBase):
    def __init__(self, msg):
        super(EventMsg, self).__init__()
        self.msg =  msg


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _EVENT = [EventMsg]
    
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        # saving all switches
        self.datapaths = set()
        self.monitor = hub.spawn(self._get_stats)      
        #self.load_models()
        self.collector = hub.spawn(self.counter)

        self.in_mapping = pickle.load(open(OUT_DIR + 'switch_mapping.pkl','rb'))
        self.packet_count = self._init_pckt_count()
        self.addresses = defaultdict(list)
        self.stats = {}

    def getAddresses(self, conf_file):
        with open(conf_file, 'r') as f:
            for line in f:
	        line = line.strip()
	        if line:
                    router, interface, address = line.split()
                    self.addresses[router].append(address)
    
    def _init_pckt_count(self):
        # inverting saved dict to have the following dict {rx:{sy:0,sz:0}}
        inverted = defaultdict(dict)
        for k,v in self.in_mapping.items():
            for r in v:
                inverted[r][k]=0

        return dict(inverted)

    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
        
        self.datapaths.add(datapath)


    def _get_stats(self):
        while True:
            for dp in self.datapaths:
                self.switch_stats(dp)
            hub.sleep(POLLING_INTERVAL)


    def switch_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _stats_reply(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        body = ev.msg.body
        sw_name = 's' + str(datapath.id)
        sw_mapping =  self.in_mapping[sw_name]
        
        # saving the switch id in the flows
        flows = [sw_name]
        
        for i,stat in enumerate(body):
            if 'in_port' in stat.match:
                # for the first time when there are no old statistics
                if sw_name not in self.stats:
                    self.stats[sw_name]=body 
                
                for router in sw_mapping:
                    # checking if the port is the incoming port for that router
                    if sw_mapping[router] == stat.match['in_port']:
                        #update count : current stats - previous stats for the specific router,switch,port triple
                        try:
                            self.packet_count[router][sw_name] = stat.packet_count - self.stats[sw_name][i].packet_count
                        except IndexError:
                            print_break_line()
                            print(stat)
                            print(router, sw_name, i)
                            print(self.stats[sw_name])
                            print_break_line()
                flows.append('packet_count=%s in_port=%s'%(stat.packet_count, stat.match['in_port']))
        
        # only if the stats data structure has been already initialized and contains alle the information
        if sw_name in self.stats and len(body)==3:
            self.stats[sw_name]=body 
        
    
    def predictor(self):
     
        self.getAddresses(ROUTER_CONF)
        print('predictor daemon started')
        while True:
           cnt = self._print_packet_count()
           print(cnt)
           self.predict('r1', '172.168.3.2', cnt)
           hub.sleep(10)

    
    def load_models(self):
        target = [t for t in os.listdir(MODELS_DIR) if t.endswith('_3_2')]
        self.models = {t:self.get_model(t) for t in target if t=='r1_172_168_3_2'}
        print(self.models)


    def predict(self, src, dst_addr, counter):
        path = [src]
        counter = np.array(counter[1:]).reshape(1,1,10)
   
        while True:
            if dst_addr in self.addresses[src]:
                break
            target = '{:}_{:}'.format(src, dst_addr.replace('.', '_'))
            model = self.models[target]
            predictions = model.predict(counter)
            next_router = ROUTERS_NAMING[np.argmax(predictions)]
            path.append(next_router)
            src = next_router
        print(path)


    def get_model(self, target):
        model_dir = os.path.join(MODELS_DIR, target)
        t0 = time.time()
        model = load_model(model_dir + '/{:}_model.h5'.format(target))
        model._make_predict_function()
        t1=time.time()
        print('Loading time: {:}'.format(t1-t0))
        return model
    

    def counter_2(self):
        counter = self._print_packet_count()
        #self.send_event_to_observers(EventMsg(str(counter)))
        #print('event sent')
        #hub.sleep(10)
    
    def counter(self):
        hub.sleep(5)
        address = ('localhost', 6000)
        print('connecting to server')
        conn = Client(address, authkey='hola')
        t0 = time.time()
        while True: 
            counter = self._print_packet_count()
            conn.send(counter)
            hub.sleep(5)
        conn.close()
    
    def _print_packet_count(self, file=None):
        t = time.time()
        counter = [t]
        for r in sorted(self.packet_count):
            # print(t, r, sum(self.packet_count[r].values()))
            counter.append(sum(self.packet_count[r].values()))
        #print(counter) 

        if file and sum(counter[1:]) > 100:
            line = ' '.join(str(e) for e in counter)
            file.write(line + '\n') 
        return counter


def print_break_line(char='*'):
    print(char*75)
