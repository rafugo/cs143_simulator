import matplotlib.pyplot as plot
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
                        l['rate'], l['delay'], l['buffersize'])
            globals.idmapping['links'][l['id']] = link

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



    # TODO: we should improve packet loss so that that it is updated more
    # frequently than just when a packet drops so that the plot appears more
    # reasonable. Perhaps I will make the buffer occupancy update more
    # frequently as well
    def plot_metrics(self):
        for s in globals.statistics.keys():
            x = []
            y = []
            dict = globals.statistics[s]
            # converts buffer occupancys from bits to KB
            if globals.BUFFEROCCUPANCY in s:
                for key in sorted(dict.keys()):
                    x.append(key)
                    y.append(dict[key]*1.25*10**(-4))
                plot.plot(x,y)
                plot.ylabel("buffer occupancy (in KB)")
            # converts link rate from bps to MBps
            if globals.LINKRATE in s:
                for key in sorted(dict.keys()):
                    x.append(key)
                    y.append(dict[key]*1.25*10**(-7))
                plot.plot(x,y)
                plot.ylabel("link rate (in MBps)")
            if globals.PACKETLOSS in s:
                for key in sorted(dict.keys()):
                    for key in sorted(dict.keys()):
                        x.append(key)
                        y.append(dict[key])
                    plot.plot(x,y)
                    plot.ylabel("number of packets dropped")
            plot.xlabel("time (in seconds)")
            plot.title(s)
            plot.savefig(s)
            plot.gcf().clear()



    def run(self):

        for router in globals.idmapping['routers'].values():
                print(router.routing_table)

        # Make Handshakes
        for router in globals.idmapping['routers'].values():
                router.init_routing_table()

        for i in range (50000):
            if globals.systime % 0.5 == 0:
                print('systime : '+str(globals.systime))
            for link in globals.idmapping['links'].values():
                link.send_packet()
            globals.systime += globals.dt


        for router in globals.idmapping['routers'].values():
            print ("Router" , router.id, "Table:", router.routing_table)

        for i in range(500000000):

            if i % 500000 == 0:
                print('systime : '+str(globals.systime))

            for flow in globals.idmapping['flows'].values():
                flow.send_packets()

            if i % 5000 == 0:
                for router in globals.idmapping['routers'].values():
                    router.recalculate_routing_table()
                    # print(router.routing_table)

            for link in globals.idmapping['links'].values():
                link.send_packet()

            globals.systime += globals.dt

        # print (globals.statistics)
        for router in globals.idmapping['routers'].values():

            print()
            print("Routing table for " + router.id)
            print(router.routing_table)
            print()



    # def run(self):

    #     # make a packet
    #     # packet0 = Packet("H0", "0", "H1", None, globals.STANDARDPACKET, data = '143 rox!')
    #     #
    #     # host0 = globals.idmapping['hosts']['H0']
    #     #
    #     # host0.send_packet(packet0)

    #     for i in range(10000000):
    #         for flow in globals.idmapping['flows'].values():
    #             flow.send_packets()
    #         for link in globals.idmapping['links'].values():
    #             link.send_packet()


    #         globals.systime += globals.dt

    #     print("statistics:")
    #     print(globals.statistics)
    #     print("end of statistics")
