import globals

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
        self.amount = round(((amount *  globals.MEGABITSTOBITS) / globals.PACKETSIZE)) + 1

        # time at which the flow simulation starts, in s
        self.start = start
        self.synack_received = False
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
        self.frwindow = 20000 * globals.dt
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

    def process_ack(self, p):

        print("received ack with data ", p.data)
        # print(p.packetid)

        # check to see if this is a duplicate ack
        if self.dup_count[p.packetid] < 2:
            self.rto = max(self.min_timeout_time, 1.3 * self.rtt)
            self.timeout_marker = self.send_times[p.packetid] + self.rto

        # check if it's a synack
        if (p.packetid == 0):
            # set the rtt
            # get send time from the packet data to calculate intial RTT
            print(self.send_times)
            self.rtt = globals.systime - self.send_times[p.packetid]
            self.window_start += 1

            self.setRTT = True
            self.synack_received = True
            # good to go ahead and start send packets from the flow now
            self.next_packet_send_time = globals.systime
            if ((self.track) and globals.FLOWRTT in globals.FLOWMETRICS) and (not globals.SMOOTH):
                key = self.id + ":" + globals.FLOWRTT
                globals.statistics[key][globals.systime] = self.rtt
            return

        # otherwise we have a normal acknowledgment
        # if we have a duplicate packet
        print(p.data)
        print(self.duplicate_packet)
        print("-------------------------------------------------------------")
        if (p.data == self.duplicate_packet):
            print(self.duplicate_count)
            self.duplicate_count = self.duplicate_count + 1
            if (self.duplicate_count == 3 and globals.systime >= \
                self.next_cut_time):
                # retransmit the packet
                # fast recovery
                print("fast recovery")
                print("sending packet ", self.duplicate_packet)
                self.source.send_packet(self.packets[self.duplicate_packet])
                self.ssthresh = self.window_size / 2
                self.window_size = self.ssthresh
                print('window_size ', self.window_size)
                self.state = "congestion_avoidance"
                print(self.state)

                self.duplicate_count = 0
                self.duplicate_packet = p.data
                self.window_start = p.data
                self.next_cut_time = globals.systime + self.rto


        else:
            # reset our counter for duplicates if we have a new ACK
            self.duplicate_count = 0
            self.duplicate_packet = p.data
            self.window_start = p.data

            # if we receive an ack for a packet, want to remove it from the list of unacked packets
            if p.packetid in self.send_times.keys():
                del self.send_times[p.packetid]

            # if we are in slow_start
            if (self.state == "slow_start"):
                self.window_size+=1
                print('window_size ', self.window_size)
                if (self.window_size >= self.ssthresh):
                    self.state = "congestion_avoidance"
                    print(self.state)
            else:

                # if we are in congestion_avoidance
                self.window_size += 1/self.window_size
                print('window_size ', self.window_size)


            # Time to do some metric tracking
            if (self.track and globals.FLOWRATE in globals.FLOWMETRICS):
                if p.packetid not in self.successfullytransmitted.keys():
                    self.successfullytransmitted[p.packetid] = 1
                    self.added = True
                    rate = 0
                    assert globals.systime >= self.start
                    if (len(self.frsteps) < self.frwindow/globals.dt):
                        self.frsteps.append(globals.PACKETSIZE)
                        if (globals.systime != self.start ):
                            rate = sum(self.frsteps)/(globals.systime - self.start)
                    else:
                        self.frsteps.pop(0)
                        rate = sum(self.frsteps)/(self.frwindow)

                    key = self.id + ":" + globals.FLOWRATE
                    #print("STORING FLOW RATE")
                    globals.statistics[key][globals.systime] = rate


    # gets called every dt
    def send_packets(self):
        # if we shouldnt do anything, leave
        if self.start >= globals.systime or self.done == True:
            return

        # if we have timed out (not recently)
        if globals.systime >= self.timeout_marker and \
            globals.systime >= self.next_cut_time:

            # enter slow_start
            self.ssthresh = self.window_size / 2
            self.window_size = 1

            print('window_size ', self.window_size)
            self.state = 'slow_start'
            print(self.state)
            self.next_cut_time = globals.systime + self.rto
            # maybe we should update time out marker here???????????????


        # send everything in the window that has not been sent
        for i in range(self.window_start, round(self.window_start + self.window_size)):

            # if it has not been sent
            if i not in self.send_times.keys():

                # update duplicate counter
                if i not in self.dup_count.keys():
                    self.dup_count[i] = 1
                else:
                    self.dup_count[i] += 1

                # update the sent time
                self.send_times[i] = globals.systime

                # # send the packet
                # print("sending packet ", i, self.send_times[i])
                if i == 403:
                    print("flow sending 403")
                self.source.send_packet(self.packets[i])


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
