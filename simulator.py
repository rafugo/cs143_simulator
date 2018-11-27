import globals
from host import Host
from link import Link
from packet import Packet
from router import Router
from flow import Flow
import json
from pprint import pprint

class Simulator:
    def __init__(self, filename):
        self.filename = filename

        # import the network object parameters
        with open(self.filename) as f:
            network_objects = json.load(f)

        # create the network objects
        # create links
        for l in network_objects['links']:
            # clear the variable
            link = None

            # add to idmapping
            link = Link(l['id'], l['connection1'], l['connection2'], \
                        l['rate'], l['delay'], l['buffersize'], l['cost'])
            globals.idmapping['links'][l['id']] = link
            for m in globals.LINKMETRICS:
                globals.statistics[l['id']+":"+m] = {}
                # print(globals.statistics);

        # create hosts
        for h in network_objects['hosts']:
            # clear the variable
            host = None

            # add to idmapping
            host = Host(h['id'], h['ip'], h['linkid'])
            globals.idmapping['hosts'][h['id']] = host

        # create routers
        if network_objects['routers'] != [{}]:
            for r in network_objects['routers']:
                # clear the variable
                router = None
            
                # get the list of links connected to each router
                link_list = []
                for lin_id in r['links']:
                    link_list.append(globals.idmapping['links'][lin_id])
            
                # initialize router and add to idmapping
                router = Router(r['id'], r['ip'], link_list)
                globals.idmapping['routers'][r['id']] = router

        for f in network_objects['flows']:
            # clear the variable
            flow = None
            # add to idmapping
            flow = Flow(f['id'], f['source'], f['destination'], f['amount'], \
                f['start'], f['congestion_control'], f['window_size'], f['min_rtt'])
            globals.idmapping['flows'][f['id']] = flow

    def run(self):

        # make a packet
        # packet0 = Packet("H0", "0", "H1", None, globals.STANDARDPACKET, data = '143 rox!')
        #
        # host0 = globals.idmapping['hosts']['H0']
        #
        # host0.send_packet(packet0)

        for i in range(10000000):
            for flow in globals.idmapping['flows'].values():
                flow.send_packets()
            for link in globals.idmapping['links'].values():
                link.send_packet()


            globals.systime += globals.dt
        # print(globals.statistics)



    def plot_metrics(self):
        #TODO
        pass

    def rt_init_test(self):
        for router in globals.idmapping['routers'].values():
            router.init_routing_table()

        for i in range(500000):
            for link in globals.idmapping['links'].values():
                link.send_packet()

            globals.systime += globals.dt

        # print (globals.statistics)
        t2 = {'H1': ['L01', -200], 'R1': ['L02', 1], 'R2': ['L04', 1]}
        for router in globals.idmapping['routers'].values():

            print(router.routing_table)
