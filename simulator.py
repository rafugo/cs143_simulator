import matplotlib.pyplot as plot
import globals
from host import Host
from link import Link
from packet import Packet
from flow_fast import Flow_FAST
from router import Router
from flow_reno import Flow

import json
from pprint import pprint

# This class runs a simulation of a network with a certain congestion
# control algorithm.
class Simulator:
    """
    This function initializes a simulator object by loading the input
    file and creating the objects according to their specifications.
    Input arguments:
        - filename : name of the input file
    Attributes:
        - network_objects: 3-dimensional list of all network objects
    """
    def __init__(self, filename, duration):
        self.filename = filename
        # the duration of the simulation, in number of timesteps
        self.duration = int(duration / globals.dt)
        # Import the network object parameters
        with open(self.filename) as f:
            network_objects = json.load(f)
        # Create links
        for l in network_objects['links']:
            # Clear the variable
            link = None

            # Add to idmapping
            link = Link(l['id'], l['connection1'], l['connection2'], \
                        l['rate'], l['delay'], l['buffersize'], l['track1'] == 1, \
                        l['track2'] == 1)
            globals.idmapping['links'][l['id']] = link

        # Create hosts
        for h in network_objects['hosts']:
            # Clear the variable
            host = None

            # Add to idmapping
            host = Host(h['id'], h['linkid'])
            globals.idmapping['hosts'][h['id']] = host

        # Create routers
        if network_objects['routers'] != [{}]:
            for r in network_objects['routers']:
                # Clear the variable
                router = None

                # Get the list of links connected to each router
                link_list = []
                for lin_id in r['links']:
                    link_list.append(globals.idmapping['links'][lin_id])

                # Initialize router and add to idmapping
                router = Router(r['id'], link_list)
                globals.idmapping['routers'][r['id']] = router

        # Create flows
        for f in network_objects['flows']:
            # Clear the variable
            flow = None

            # add to idmapping
            if f['congestion_control'] == 'reno':
                flow = Flow(f['id'], f['source'], f['destination'], f['amount'], \
                    f['start'], f['track'] == 1)
            else:
                flow = Flow_FAST(f['id'], f['source'], f['destination'], f['amount'], \
                    f['start'], f['track'] == 1)


            globals.idmapping['flows'][f['id']] = flow

    # prepares host metrics for tracking
    def prepare_host_metrics(self):
        """This function constructs a dictionaries tracking host send/recive
           rates using the recorded flow send/recieve rates"""
        for (h, host) in globals.idmapping['hosts'].items():
            tracking = False
            dict = {}
            for (id, flow) in globals.idmapping['flows'].items():
                if flow.track and flow.source == host:
                    if not tracking:
                        dict = globals.statistics[id+":"+globals.FLOWRATE].copy()
                        tracking = True
                    else:
                        newdict = globals.statistics[id+":"+globals.FLOWRATE]
                        for i in dict.keys() | newdict.keys():
                            if i in dict.keys() & newdict.keys():
                                dict[i] = dict[i] + newdict[i]
                            elif i in newdict.keys():
                                dict[i] = newdict[i]
            if tracking:
                globals.statistics[h+":"+globals.HOSTFLOWRATE] = dict


    # Plots metrics based on data collected while the simulations was running
    def plot_metrics(self):
        self.prepare_host_metrics()
        if (globals.PRESENTATIONMODE):
            plot.rcParams.update({'font.size' : 12})
            plot.tight_layout()
        # Access all metrics
        all_metrics = globals.LINKMETRICS + globals.HALFLINKMETRICS + \
                      globals.FLOWMETRICS + [globals.HOSTFLOWRATE]
        # For every timestep
        for t in all_metrics:
            legend = []
            plot.figure(figsize = (12,4.5))
            plot.xlim(xmax = self.duration*globals.dt)
            #plot.ylim(ymin = 0)
            print("Plotting ", t)
            for s in globals.statistics.keys():
                x = []
                y = []
                lines = 0
                dict = globals.statistics[s]
                #print(s)
                name = s.split(":")
                name.pop()
                name = ":".join(name)

                # Plot buffer occupancy
                if globals.BUFFEROCCUPANCY in s and globals.BUFFEROCCUPANCY == t:
                    for key in sorted(dict.keys()):
                        x.append(key)
                        # Converts the buffer occupancy from bits to Kilobytes
                        y.append(dict[key]*globals.BITSTOKILOBITS/8)
                    lines = plot.plot(x,y)
                    plot.ylabel("buffer occupancy (in KB)")
                    legend.append(name)

                # Plot link rates
                if globals.LINKRATE in s and globals.LINKRATE == t:
                    for key in sorted(dict.keys()):
                        x.append(key)
                        y.append(dict[key]*globals.BITSTOMEGABITS)
                    lines = plot.plot(x,y)
                    plot.ylabel("link rate (in Mbps)")
                    legend.append(name)

                # Plot packet loss
                if globals.PACKETLOSS in s and globals.PACKETLOSS == t:
                    for key in sorted(dict.keys()):
                        x.append(key)
                        y.append(dict[key])
                    lines = plot.plot(x,y)
                    plot.ylabel("number of packets dropped")
                    legend.append(name)

                # Plot flow rates
                if (globals.HOSTFLOWRATE not in s) and globals.FLOWRATE in s and globals.FLOWRATE == t:
                    for key in sorted(dict.keys()):
                        x.append(key)
                        # converts flow rate from bps to Mbps
                        y.append(dict[key]*globals.BITSTOMEGABITS)
                    lines = plot.plot(x,y)
                    plot.ylabel("flow rate (in Mbps)")
                    legend.append(name)

                # Plot window size
                if globals.WINDOWSIZE in s and globals.WINDOWSIZE == t:
                    for key in sorted(dict.keys()):
                        x.append(key)
                        y.append(dict[key])
                    lines = plot.plot(x,y)
                    plot.ylabel("window size")
                    legend.append(name)

                # Plot round trip times
                if globals.FLOWRTT in s and globals.FLOWRTT == t:
                    for key in sorted(dict.keys()):
                        x.append(key)
                        y.append(dict[key])
                    lines = plot.plot(x,y)
                    plot.ylabel("round trip time (in seconds)")
                    legend.append(name)

                # Plot per host flow rate
                if globals.HOSTFLOWRATE in s and globals.HOSTFLOWRATE == t:
                    for key in sorted(dict.keys()):
                        x.append(key)
                        y.append(dict[key]*globals.BITSTOMEGABITS)
                    lines = plot.plot(x,y)
                    plot.ylabel("flow rate (in Mbps)")
                    legend.append(name)

                if (lines != 0):
                    if globals.PRESENTATIONMODE:
                        plot.setp(lines, linewidth = 1)
                    else:
                        plot.setp(lines, linewidth = 0.5)
                    plot.xlabel("time (in seconds)")


            plot.title(t)
            plot.legend(legend)
            plotname = self.filename.split(".")[0] + " " + t
            #if globals.PRESENTATIONMODE:
                #plotname = plotname + " presentation"

            plot.savefig(plotname, bbox_inches = "tight")
            plot.gcf().clear()

    # Function to actually run the simulator
    def run(self):
        # Make handshakes to learn routing table
        for router in globals.idmapping['routers'].values():
            router.send_handshake()

        # Run the simulation for so many dt's
        # For every dt
        for i in range(self.duration):

            # Send packets from links
            for link in globals.idmapping['links'].values():
                link.update_link_statistics()
                link.send_packet()

            # Send link states every 5 seconds
            if (i+1) % 50000 == 0:
                print("systime : ", globals.systime)

                for router in globals.idmapping['routers'].values():
                    router.recalc_link_state()

            # Send out packets from the flows
            for flow in globals.idmapping['flows'].values():
                flow.run()
                flow.update_flow_statistics()

            # Increment the global clock
            globals.systime += globals.dt

        for flow in globals.idmapping['flows'].values():
            print(flow.states_tracker)
