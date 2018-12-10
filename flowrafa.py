import globals
import math

from host import Host
from link import Link
from packet import Packet
from router import Router

class Flow:
    def __init__(self, id, source, destination, amount,\
                    start, congestion_control, track=True):
        # current size of the window used for the congestion controller
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

        # converts the amount of data from Megabytes to bits
        self.amount = round((amount * 8 * globals.MEGABITSTOBITS) / (globals.PACKETSIZE - (20 * 8))) + 1

        # time at which the flow simulation starts, in s
        self.start = start
        self.min_timeout_time = 1      # in seconds

        self.setRTT = False
        self.state = "slow_start"
        # list of actual packets to be sent
        self.packets = []

        for i in range(self.amount):
            p = None
            p = Packet(self.source.id, self.id, self.destination.id, i, \
                globals.STANDARDPACKET, '')
            self.packets.append(p)


        # flag to demonstrate if the flow has all been sent
        self.done = False
        self.ssthresh = 1000
        # packets that have been sent but not acknowledged yet
        self.send_times = dict()
        # used to calculate RTT
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


        # tracking what states we are in and the time
        self.states_tracker = []


    def run(self):
        # if we shouldn't do anything, leave
        if self.start >= globals.systime or self.done == True or \
            self.state == "fast_recovery":
            return

        # send any available packets otherwise
        self.send_packets()

    def process_ack(self, p):
        if p.data >= self.amount:
            self.done = True

        if self.done:
            return

        # handle duplicate packets
        if p.data == self.duplicate_packet:
            self.handle_dup_ack(p)
            return

        # if we're in fast_recovery with a new packet, enter congestion_avoidance
        if self.state == 'fast_recovery':
            self.state = 'congestion_avoidance'
            self.states_tracker.append((self.state, globals.systime))

        self.duplicate_count = 0
        self.duplicate_packet = p.data
        self.window_start = p.data

        # if this is first successful transmission of packet, set new rtt & rto
        if self.dup_count[p.packetid] == 1:
            self.rtt = globals.systime - self.send_times[p.packetid]
            self.rto = 2 * self.rtt

        # this is a new ACK, update rto
        self.timeout_marker = globals.systime + self.rto

        # if it's the synack, start metrics
        if p.packetid == 0:
            self.start_metrics()
            return

        # if we hit the threshold, enter congestion avoidance
        if self.window_size >= self.ssthresh and self.state == 'slow_start':
            self.state = 'congestion_avoidance'
            self.states_tracker.append((self.state, globals.systime))

        # slow start
        if self.state == 'slow_start':
            self.window_size += 1
            self.window_start = p.data


        # congestion avoidance
        elif self.state == 'congestion_avoidance':
            self.window_size += 1 / self.window_size
            self.window_start = p.data


        # Time to do some metric tracking
        self.track_metrics(p)
        return


    def handle_dup_ack(self, p):

        self.duplicate_count += 1

        if self.state != 'fast_recovery' and self.duplicate_count == 3:
            self.ssthresh = self.window_size / 2

            # retransmit
            self.source.send_packet(self.packets[p.data])

            self.window_size = self.ssthresh + 3
            self.state = 'fast_recovery'
            self.states_tracker.append((self.state, globals.systime))


        elif self.state == 'fast_recovery':
            self.window_start += 1

            # send any packets we can send
            self.send_packets()


    # gets called every dt
    def send_packets(self):
        # if we have timed out (not recently)
        if globals.systime >= self.timeout_marker and \
            globals.systime >= self.next_cut_time:
            # enter slow_start
            self.ssthresh = self.window_size / 2

            self.window_size = 1

            self.state = 'slow_start'
            self.next_cut_time = globals.systime + self.rto
            self.states_tracker.append((self.state, globals.systime))

            '''
            THIS IS JANK YO
            vvvvvvvvvvvvvvvvvv
            '''
            # print(self.window_start)
            # dup_count_keys_copy = list(self.dup_count.keys()).copy()
            # # need to resend window_start
            # for k in dup_count_keys_copy:
            #     if k > self.window_start:
            #         del self.dup_count[k]

            self.source.send_packet(self.packets[self.window_start])
            self.send_times[self.window_start] = globals.systime
            self.dup_count[self.window_start] += 1

            # clear out the send times for all the packets larger than
            # the current packet
            send_times_keys_copy = list(self.send_times.keys()).copy()
            for i in send_times_keys_copy:
                if i > self.window_start:
                    del self.send_times[i]

            '''
            ^^^^^^^^^^^^^^^^^^
            '''
            self.rto = 2 * self.rto
            self.next_cut_time += self.rto

        else:
            # send everything in the window that has not been sent
            self.send_window()


    def send_window(self):
        # send everything in the window that has not been sent
        for i in range(self.window_start, min(round(self.window_start + self.window_size), self.amount)):
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
                # print("sending packet ", i)

    def start_metrics(self):
        self.setRTT = True
        if ((self.track) and globals.FLOWRTT in globals.FLOWMETRICS) and (not globals.SMOOTH):
            key = self.id + ":" + globals.FLOWRTT
            globals.statistics[key][globals.systime] = self.rtt
        return


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
            #print("STORING FLOW RATE")
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

    def completed(self):
        return self.done
