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
                        l['rate'], l['delay'], l['buffersize'], l['track1'] == 1, \
                        l['track2'] == 1)
            globals.idmapping['links'][l['id']] = link

        # create hosts
        for h in network_objects['hosts']:
            # clear the variable
            host = None

            # add to idmapping
            host = Host(h['id'], h['linkid'])
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
                router = Router(r['id'], link_list)
                globals.idmapping['routers'][r['id']] = router

        for f in network_objects['flows']:
            # clear the variable
            flow = None
            # add to idmapping
            flow = Flow(f['id'], f['source'], f['destination'], f['amount'], \
                f['start'], f['congestion_control'], f['track'] == 1)
            globals.idmapping['flows'][f['id']] = flow

    def plot_metrics(self):
        for s in globals.statistics.keys():
            plot.figure(figsize=(8,3))
            x = []
            y = []
            lines = 0
            dict = globals.statistics[s]
            # converts buffer occupancys from bits to KB
            print(s)
            if globals.BUFFEROCCUPANCY in s:
                #print(dict)
                for key in sorted(dict.keys()):
                    x.append(key)
                    # Converts the buffer occupancy from bits to Kilobytes
                    y.append(dict[key]*globals.BITSTOKILOBITS/8)
                lines = plot.plot(x,y)
                plot.ylabel("buffer occupancy (in KB)")
            if globals.LINKRATE in s:
                for key in sorted(dict.keys()):
                    x.append(key)
                    # converts link rate from bps to Mbps
                    y.append(dict[key]*globals.BITSTOMEGABITS)
                lines = plot.plot(x,y)
                plot.ylabel("link rate (in Mbps)")
            if globals.PACKETLOSS in s:
                for key in sorted(dict.keys()):
                    x.append(key)
                    y.append(dict[key])
                lines = plot.plot(x,y)
                plot.ylabel("number of packets dropped")
            if globals.FLOWRATE in s:
                for key in sorted(dict.keys()):
                    x.append(key)
                    # converts flow rate from bps to Mbps
                    y.append(dict[key]*globals.BITSTOMEGABITS)
                lines = plot.plot(x,y)
                plot.ylabel("flow rate (in Mbps)")
            if globals.WINDOWSIZE in s:
                for key in sorted(dict.keys()):
                    x.append(key)
                    y.append(dict[key])
                lines = plot.plot(x,y)
                plot.ylabel("window size")
            if globals.FLOWRTT in s:
                for key in sorted(dict.keys()):
                    x.append(key)
                    y.append(dict[key])
                lines = plot.plot(x,y)
                plot.ylabel("round trip time (in seconds)")
            plot.setp(lines, linewidth = 0.5)
            plot.xlabel("time (in seconds)")
            plot.title(s)
            plot.savefig(s)
            plot.gcf().clear()



    def run(self):

        for router in globals.idmapping['routers'].values():
            pass
                #print(router.routing_table)

        # Make Handshakes
        for router in globals.idmapping['routers'].values():
            router.init_routing_table()

        # run the simulation
        for i in range(300000):

            for link in globals.idmapping['links'].values():
                link.update_link_statistics()
                link.send_packet()

            if (i+1) % 50000 == 0:
                print("systime : ", globals.systime)
                for router in globals.idmapping['routers'].values():
                    router.recalculate_routing_table()

            for flow in globals.idmapping['flows'].values():
                flow.send_packetsV2()
                flow.update_flow_statistics()

            globals.systime += globals.dt

        for router in globals.idmapping['routers'].values():
            pass
