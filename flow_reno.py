import globals
import math

from host import Host
from link import Link
from packet import Packet
from router import Router

class Flow:
    def __init__(self, id, source, destination, amount,\
                    start, track=True):
        '''
        The function initializes a flow object:
        Initial Arguments:
            - id (string) : id of the flow
            - source (string): id of the source of the flow
            - destination (string): id of the destination of the flow
            - amount (int): number of Megabytes to be sent
            - track (bool): used in determining if metrics should be tracked

        Attributes: 
            - window_size (float) : size of the window used for sending packets
            - window_start (int) : packet number to start sending form
            - FR (int) : packet id of packet sent during fast recovery
            - rtt (float) : current round trip time
            - rto (float) : current timeout value
            - id (int) : id of the flow
            - source (Host/Router) : refers to source object of the flow
            - destination (Host/Router) : refers to the dest object of the flow
            - amount (int) : number of packets within the flow
            - start (float) : time the flow is scheduled to start
            - setRTT (bool) : determine if we have set an RTT yet
            - state (string) : determines what start the congestion control is in
                can take on values of "slow_start", "congestion_avoidance", "fast_recovery"
            - packets (List<Packet>) : List of packets to be sent for the flow
            - done (bool) : flag to demonstrate if the flow has all been sent
            - ssthresh (int) : threshold for TCP Reno window size
            - send_times (dict) : dictionary of packet ids to send times of the packet
                 contains only packets that have not yet been acked
            - dup_count (dict) : a dictionary of packet id and the number of times they
                have been sent, used to calculate the RTT using Karn's algo
            - duplicate_count (int) : number of consecutive duplicative acks received
            - duplicate_packet (int) : value of the duplicate acknowledgements
            - timeout_marker (float) : earliest time at which a packet has timed out
            - next_cut_time (float) : next time we can cut the window size, created to make sure
                we don't trigger a dangerous loop

            Variables for metric tracking:
            TODO: @Kelsi can you fill this in?
            - track 
            - frwindow 
            - frsteps 
            - rttwindow
            - rttsteps
            - added 
            - successfullytransmitted 
        '''
        self.window_size = 1
        self.window_start = 0
        self.FR = -1

        self.rtt = 1
        self.rto = self.rtt
        self.id = id

        if source[0] == 'H':
            self.source = globals.idmapping['hosts'][source]
        else:
            self.source = globals.idmapping['routers'][source]
        if destination[0] == 'H':
            self.destination = globals.idmapping['hosts'][destination]
        else:
            self.destination = globals.idmapping['routers'][destination]

        # Converts the amount of data from Megabytes to bits
        self.amount = round((amount * 8 * globals.MEGABITSTOBITS) / (globals.PACKETSIZE - (20 * 8))) + 1

        # time at which the flow simulation starts, in s
        self.start = start

        self.setRTT = False
        self.state = "slow_start"
        # List of actual packets to be sent
        self.packets = []
        for i in range(self.amount):
            p = None
            p = Packet(self.source.id, self.id, self.destination.id, i, \
                globals.STANDARDPACKET, '')
            self.packets.append(p)

        self.done = False
        self.ssthresh = 1000

        self.send_times = dict()
        self.dup_count = dict()

        # congestion signals to keep track of
        self.duplicate_count = 0
        self.duplicate_packet = -2
        self.timeout_marker = 1000
        self.next_cut_time = 0

        # Variables for metric tracking
        self.track = track
        self.frwindow = 1000 * globals.dt
        self.frsteps = []
        self.rttwindow = 20000 * globals.dt
        self.rttsteps = []
        self.added = False
        self.successfullytransmitted = {}

        # If this flow is being tracked, we set up the dictionaries for all of
        # the metrics to be tracked.
        if (track):
            for m in globals.FLOWMETRICS:
                globals.statistics[id+":"+m] = {}
        # Tracking what states we are in and the time
        self.states_tracker = []

    # Run the flow, this is the function called every dt for the flow
    def run(self):
        # If we shouldn't do anything, leave
        if self.start >= globals.systime or self.done == True or \
            self.state == "fast_recovery":
            return

        # Send any available packets otherwise
        self.send_packets()

    # Process an acknowledgement once received 
    def process_ack(self, p):
        # If we've received the acknowledgment for the last packet
        if p.data >= self.amount:
            self.done = True
        # If we're done
        if self.done:
            return

        # Handle duplicate packets
        if p.data == self.duplicate_packet:
            self.handle_dup_ack(p)
            return

        # If we're in fast_recovery with a new packet, enter congestion_avoidance
        if self.state == 'fast_recovery':
            self.state = 'congestion_avoidance'
            self.states_tracker.append((self.state, globals.systime))

        self.duplicate_count = 0
        self.duplicate_packet = p.data
        self.window_start = p.data

        # If this is first successful transmission of packet, set new rtt & rto
        if self.dup_count[p.packetid] == 1:
            self.rtt = globals.systime - self.send_times[p.packetid]
            self.rto = 2 * self.rtt

        # This is a new ACK, update rto
        self.timeout_marker = globals.systime + self.rto

        # If it's the synack, start metrics
        if p.packetid == 0:
            self.start_metrics()
            return

        # If we hit the threshold, enter congestion avoidance
        if self.window_size >= self.ssthresh and self.state == 'slow_start':
            self.state = 'congestion_avoidance'
            self.states_tracker.append((self.state, globals.systime))

        # Slow start
        if self.state == 'slow_start':
            self.window_size += 1
            self.window_start = p.data


        # Congestion avoidance
        elif self.state == 'congestion_avoidance':
            self.window_size += 1 / self.window_size
            self.window_start = p.data


        # Time to do some metric tracking
        self.track_metrics(p)
        return

    # Handling duplicate acknowledgements depending on the state of TCP Reno
    def handle_dup_ack(self, p):
        self.duplicate_count += 1
        # Time to enter fast recovery
        if self.state != 'fast_recovery' and self.duplicate_count == 3:
            self.ssthresh = self.window_size / 2

            # Retransmit the dropped packet
            self.source.send_packet(self.packets[p.data])
            self.window_size = self.ssthresh + 3
            self.state = 'fast_recovery'
            self.states_tracker.append((self.state, globals.systime))

        # Window inflation
        elif self.state == 'fast_recovery':
            self.window_start += 1
            # Send any packets we can send
            self.send_packets()

    # Sends the packets depending on the time and acks we've received
    def send_packets(self):
        # if we have timed out (not recently)
        if globals.systime >= self.timeout_marker and \
            globals.systime >= self.next_cut_time:
            # Enter slow_start
            self.ssthresh = self.window_size / 2
            self.window_size = 1

            # Update state and track timeout
            self.state = 'slow_start'
            self.next_cut_time = globals.systime + self.rto
            self.states_tracker.append((self.state, globals.systime))

            # Retransmit timed out packet and update send times and 
            #    dup_count
            self.source.send_packet(self.packets[self.window_start])
            self.send_times[self.window_start] = globals.systime
            self.dup_count[self.window_start] += 1

            # Clear out the send times for all the packets larger than
            # the current packet
            send_times_keys_copy = list(self.send_times.keys()).copy()
            for i in send_times_keys_copy:
                if i > self.window_start:
                    del self.send_times[i]

            # Double timeout time
            self.rto = 2 * self.rto
            self.next_cut_time += self.rto

        else:
            # Send everything in the window that has not been sent
            self.send_window()

    # Send a window of packets if it has not been sent
    def send_window(self):
        # Send everything in the window that has not been sent
        for i in range(self.window_start, min(round(self.window_start + \
             self.window_size), self.amount)):
            if i not in self.send_times.keys():
                # update duplicate counter
                if i not in self.dup_count.keys():
                    self.dup_count[i] = 1
                else:
                    self.dup_count[i] += 1

                # update the sent time
                self.send_times[i] = globals.systime

                # send the packet
                self.source.send_packet(self.packets[i])

    # Initialize info to start tracking metrics for the flow
    def start_metrics(self):
        self.setRTT = True
        if ((self.track) and globals.FLOWRTT in globals.FLOWMETRICS) and (not globals.SMOOTH):
            key = self.id + ":" + globals.FLOWRTT
            globals.statistics[key][globals.systime] = self.rtt
        return

    # Track the metrics on the flow
    def track_metrics(self, p):
        if (self.track and globals.FLOWRATE in globals.FLOWMETRICS):
            if p.packetid not in self.successfullytransmitted.keys():
                self.successfullytransmitted[p.packetid] = 1
                self.added = True
                rate = 0
                assert globals.systime >= self.start

                if (True):
                    self.frsteps.append(globals.PACKETSIZE)
                    if (len(self.frsteps) <= self.frwindow/globals.dt):
                        if (globals.systime != self.start ):
                            rate = sum(self.frsteps)/(globals.systime - self.start)
                    else:
                        self.frsteps.pop(0)
                        rate = sum(self.frsteps)/(self.frwindow)

                    key = self.id + ":" + globals.FLOWRATE
                    globals.statistics[key][globals.systime] = rate

                else:
                    self.frsteps.append(0)
                    link = globals.idmapping['links'][self.source.linkid]
                    linkrate = link.rate
                    transmission_time = globals.PACKETSIZE/link.rate
                    if (len(self.frsteps) <= self.frwindow/globals.dt):
                        segments = min(len(self.frsteps), transmission_time/globals.dt)
                        segments = math.ceil(segments)
                        for i in range(segments):
                            self.frsteps[len(self.frsteps)-1-i] += float(globals.PACKETSIZE)/segments
                        if (globals.systime != self.start):
                            rate = sum(self.frsteps)/(globals.systime - self.start)
                    else:
                        self.frsteps.pop(0)
                        segments = min(len(self.frsteps), transmission_time/globals.dt)
                        segments = math.ceil(segments)
                        for i in range(segments):
                            self.frsteps[len(self.frsteps)-1-i] += float(globals.PACKETSIZE)/segments
                        rate = sum(self.frsteps)/(self.frwindow)
                    key = self.id + ":" + globals.FLOWRATE
                    globals.statistics[key][globals.systime] = rate

    # Update the flow statistics for metric tracking
    def update_flow_statistics(self):
        if (not self.added) and (self.track and globals.FLOWRATE in globals.FLOWMETRICS):
            rate = 0
            self.frsteps.append(0)
            if (len(self.frsteps) < self.frwindow/globals.dt):
                if (globals.systime > self.start):
                    rate = sum(self.frsteps)/(globals.systime - self.start)
            else:
                self.frsteps.pop(0)
                rate = sum(self.frsteps)/(self.frwindow)

            key = self.id + ":" + globals.FLOWRATE
            globals.statistics[key][globals.systime] = rate

        if (self.track and globals.WINDOWSIZE in globals.FLOWMETRICS):
            key = self.id + ":" + globals.WINDOWSIZE
            globals.statistics[key][globals.systime] = self.window_size

        if  (self.track and globals.FLOWRTT in globals.FLOWMETRICS) and globals.SMOOTH:
            avgrtt = 0
            if (self.setRTT):
                self.rttsteps.append(self.rtt)
                if (len(self.rttsteps) < self.rttwindow/globals.dt) and globals.systime > 0:
                    avgrtt = sum(self.rttsteps)/(globals.systime) * globals.dt
                else:
                    self.rttsteps.pop(0)
                    avgrtt = sum(self.rttsteps)/(self.rttwindow) * globals.dt
                key = self.id + ":" + globals.FLOWRTT
                globals.statistics[key][globals.systime] = avgrtt

        self.added = False

    # Function to determine if the flow has completed or not
    def completed(self):
        return self.done
