import globals
from host import Host
from link import Link
from packet import Packet
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
                print(globals.statistics);

        # create hosts
        for h in network_objects['hosts']:
            # clear the variable
            host = None

            # add to idmapping
            host = Host(h['id'], h['ip'], h['linkid'])
            globals.idmapping['hosts'][h['id']] = host


    def run(self):

        # make a packet
        packet0 = Packet("H0", "0", "H1", None, 0, data = '143 rox!')

        host0 = globals.idmapping['hosts']['H0']

        host0.send_packet(packet0)

        for i in range(100000):
            for link in globals.idmapping['links'].values():
                link.send_packet()

            globals.systime += globals.dt
        print(globals.statistics)

    def plot_metrics(self):
        #TODO
        pass
