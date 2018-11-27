import globals
from host import Host
from link import Link
from packet import Packet
import json
from pprint import pprint

class Simulator:
    # I'm not actually sure that the things that we thought would be fields of
    # the simulator class should be. I think we need them to be global variables,
    # and in order to do that I believe that they have to be declared outside of
    # a class, but I'm really not sure. Or we can pass the simulator itself as
    # and argument to pretty much everything else and use it as a context.

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

        # create hosts
        for h in network_objects['hosts']:
            # clear the variable
            host = None

            # add to idmapping
            host = Host(h['id'], h['ip'], h['linkid'])
            globals.idmapping['hosts'][h['id']] = host


    def run(self):

        



        # make a packet
        packet0 = Packet("H0", "0", "H1", 0, False, globals.STANDARDPACKET, False, False, \
                            data = '143 rox!')

        host0 = globals.idmapping['hosts']['H0']

        host0.send_packet(packet0)

        for i in range(100000):
            for link in globals.idmapping['links'].values():
                link.send_packet()

            globals.systime += globals.dt

    def plot_metrics(self):
        #TODO
        pass
