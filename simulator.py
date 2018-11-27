import globals
from host import Host
from link import Link
from packet import Packet
from router import Router
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

        # create hosts
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


    def run(self):

        # make a packet
        packet0 = Packet("H1", "0", "H2", None, globals.STANDARDPACKET, data = '143 rox!')

        host0 = globals.idmapping['hosts']['H1']

        host0.send_packet(packet0)

        for i in range(100000):
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

        for i in range(100000):
            for link in globals.idmapping['links'].values():
                link.send_packet()

            globals.systime += globals.dt

        # print (globals.statistics)

        for router in globals.idmapping['routers'].values():
            print (router.routing_table)
