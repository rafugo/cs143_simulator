import globals

from congestion_controller import *
from host import Host
from link import Link
from packet import Packet
from router import Router
from congestion_controller import CongestionController

class Flow:
    def __init__(self, id, source, destination, amount,\
                    start, congestion_control, track=True):
        """This function initializes new flows
           INPUT ARGUMENTS-
               linkid : The string ID of the flow being constructed
               source : The string ID of the object the flow is coming from
               destination : The string ID of the object that the flow is
                             sending packets to
               amount : The amount of data that the flow is transmitting (in MB)
               start : The time that the flow should start (in seconds)
               track : a boolean value indicating if we are tracking metrics
                       for this flow
           NOTE- I don't think we need min_rtt here and i dont know about
                 window_size.
           FIELDS-
               id : The string ID of the flow
               source : The object which is initially sending the flow packets
               destination : The object that the flow packets are intended to
                             reach
               amount : the amount of data to be transmitted (in bits)
               start : the time at which the flow will start (in seconds)
               started : boolean containing whether or not the flow has begun
               next_packet_send_time : the time to send the next packet
               packets : a list of the packets of the flow
               next_packet :
               window_size :
               window_start : integer marking beginning of window
               min_rtt :
               done :
               packet_timeout_times : dictionary of packetid : systime, where the
                    systime is the time when the packetid will have timedout
               track : a boolean flag indicating if we are tracking metrics for
                       this flow
               frwindow : the window size of time which we are using to
                          approximate flow rate
               frsteps : a list of the number of acknowelegements recieved
                         at various time steps.
               added : a boolean flag that keeps track of whether or not we
                       have already added the flow rate for this time step
                       to the metric tracking
               """
        # packet number that the window needs to start at, default first packet
        self.next_packet = -1;
        # current size of the window used for the congestion controller
        self.window_size = 1
        self.window_start = 0
        # round trip time used for congestion control, starts at arbitrary
        #   value and then is calculated
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
        self.amount = amount * 8 * globals.MEGABITSTOBITS
        # time at which the flow simulation starts, in s
        self.start = start
        self.started = False
        # next time to send a packet
        self.next_packet_send_time = self.start

        self.min_timeout_time = 1      # in seconds
        self.setRTT = False
        self.state = "slow_start"
        # list of actual packets to be sent
        self.packets = []
        amountInPackets = 0
        i = 0
        while (amountInPackets < self.amount):
            p = None
            p = Packet(self.source.id, self.id, self.destination.id, i, \
                globals.STANDARDPACKET, '')
            self.packets.append(p)
            amountInPackets = amountInPackets + globals.PACKETSIZE - globals.PACKETHEADERSIZE
            i = i + 1
        # flag to demonstrate if the
        self.done = False

        self.ssthresh = 1000
        # packets that have been sent but not acknowledged yet
        self.send_times = dict()
        # used to calculate RTT
        self.dup_count = dict()
        # congestion signals to keep track of
        self.duplicate_count = 0
        self.last_ack_received = -1
        self.first_packet = 0

        # Variables for metric tracking
        self.track = track
        self.frwindow = 1000 * globals.dt #was 20000
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
        # check if it's a synack
        if (p.get_packet_type() == globals.SYNACK):
            # set the rtt
            self.rtt = globals.systime - float(p.data)
            self.setRTT = True
            self.next_packet = 0
            # good to go ahead and start send packets from the flow now
            self.next_packet_send_time = globals.systime
            if ((self.track) and globals.FLOWRTT in globals.FLOWMETRICS) and (not globals.SMOOTH):
                key = self.id + ":" + globals.FLOWRTT
                globals.statistics[key][globals.systime] = self.rtt

        # if it's a normal acknowledgement
        else:
            # make sure it's an acknowledgement
            assert p.is_ack();
            # make sure it got to the right place from the right place
            assert p.sourceid == self.destination.id
            assert p.destinationid == self.source.id
            # send current round trip time
            if self.dup_count[p.packetid] < 2:
                self.rtt = globals.systime - self.send_times[p.packetid]

            # for metrics
            if (self.track) and globals.FLOWRTT in globals.FLOWMETRICS:
                key = self.id + ":" + globals.FLOWRTT
                globals.statistics[key][globals.systime] = self.rtt

            # remove the packet from the list of packets that need to be sent
            # p.data contains the id of the next packet it needs
            if (p.data >  self.next_packet):
                self.next_packet = p.data
            # the next packet to send is out of index so we've sent everything
            if (self.next_packet >= len(self.packets)):
                self.done = True

            # -----------------------------------------------------------------
            # CONGESTION CONTROL
            # -----------------------------------------------------------------
            # check to see if this is a duplicate ack
            if self.dup_count[p.packetid] < 2:
                self.rto = max(self.min_timeout_time, 1.3 * self.rtt)
                self.timeout_marker = self.send_times[p.packetid] + self.rto

            # if we receive an ack for a packet, want to remove it from the list of unacked packets
            if p.packetid in self.send_times.keys():
                del self.send_times[p.packetid]

            # In slow start phase, increase congestion window size by 1
            if (self.state == "slow_start"):
                self.window_size += 1
                # If congestion window becomes larger than slow start threshold,
                # switch to congestion avoidance phase
                if (self.window_size >= self.ssthresh):
                    self.state = "congestion_avoidance"
                    print("entering congestion avoidance")

            elif (self.state == "congestion_avoidance"):
                # Check if this is a duplicate acknowledgement
                if p.data == self.last_ack_received:
                    self.duplicate_count += 1
                    # After 3 duplicate acknowledgements, if the packet has not
                    # already been received, halve the congestion window size and
                    # move into fast recovery phase
                    if (self.duplicate_count == 3) and ((p.data) in self.send_times.keys()):
                        self.window_size = self.window_size / 2
                        self.ssthresh = self.window_size
                        self.state = "fast_recovery"
                        print("switched to fast recovery")

                # if this is not a duplicate acknowledgement
                else:
                    self.window_size += 1 / self.window_size
                    # reset duplicate count since the chain of dupACKS is broken
                    self.duplicate_count = 0

            # if we're in fast recovery instead
            elif (self.state == "fast_recovery"):
                # Check if this is a duplicate acknowledgement
                if p.data == self.last_ack_received:
                    self.duplicate_count += 1
                    return
                else:
                    # check if this is the ACK for the packet transmitted during Fast Recovery
                    if p.packetid == self.FR_packet:
                        self.window_size = self.ssthresh
                        self.state = "congestion_avoidance"
                        print("switch to congestion avoidance")
                    # reset duplicate count since the chain of dupACKS is broken
                    self.duplicate_count = 0
            self.last_ack_received = p.packetid + 1

            # --------------------------------------------------------------------------
            # END CONGESTION control

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


    # sliding window packet sending
    def send_packetsV2(self):
        # make sure it's send time
        if (globals.systime >= self.start and self.done == False):
            # checking timeout marker
            if (globals.systime >= self.timeout_marker):
                # we have timed out, so we need to re-enter slow start
                self.state = "slow_start"
                self.ssthresh = max(self.window_size / 2, 1)
                self.window_size = 1
                print("entering slow start after time out ")

            # SEND SYNC PACKET FIRST
            if (self.next_packet == -1):
                if timesout, send again and change marker
                # # if it's the first one or it's timed out, send it again
                # if -1 not in self.packet_timeout_times.keys() or \
                #         self.packet_timeout_times[-1] <= globals.systime:
                #
                #     sync_packet = Packet(self.source.id, self.id, self.destination.id, \
                #         -1, globals.SYNPACKET, globals.systime)
                #
                #     if -1 not in self.dup_count.keys():
                #         self.dup_count[-1] = 1
                #     else:
                #         self.dup_count[-1] = self.dup_count[-1] + 1
                #
                #     self.source.send_packet(sync_packet)
                #     self.packet_timeout_times[-1] = globals.systime + self.timeout_time

            else:
                # if we just started, send out the whole window
                if self.started == False:
                    self.started = True
                    # send the whole first window
                    for i in range(round(self.window_size+1)):
                        self.send_times[i] = globals.systime

                        if i not in self.dup_count.keys():
                            self.dup_count[i] = 1
                        else:
                            self.dup_count[i] = self.dup_count[i] + 1

                        self.source.send_packet(self.packets[i])
                        self.packet_timeout_times[i] = globals.systime + self.timeout_time
                else:
                    # this flow has sent all its first window

                    # if the first few packets have been acked, then move the
                    # window over
                    if self.next_packet > self.window_start:

                        # move the start of the window over
                        self.window_start = self.next_packet

                        # send all packets that havent been sent in the window
                        # yet (it has to be packets that have never been sent
                        # before)
                        for i in range(self.window_start, round(self.window_start + self.window_size)):

                            # if the packet never been sent
                            if i not in self.send_times.keys() and \
                                i not in self.timedout_packets:

                                # send the packet
                                new_packet = self.packets[i]
                                self.send_times[i] = globals.systime

                                if i not in self.dup_count.keys():
                                    self.dup_count[i] = 1
                                else:
                                    self.dup_count[i] = self.dup_count[i] + 1

                                # print("sending packet: ", i)
                                self.source.send_packet(new_packet)


                    # if the first packet timed out, send it again
                    elif self.window_start in self.timedout_packets.keys() and \
                        self.timedout_packets[self.window_start] <= globals.systime:

                        # send all the consecutive timedout packets starting
                        # from the front of the window
                        counter = self.window_start
                        while counter in self.timedout_packets.keys() and \
                            self.timedout_packets[counter] <= globals.systime:
                            # print("resending packet ", counter, "   time : ", globals.systime)
                            # send the packet again, and update the timeout
                            new_packet = self.packets[counter]
                            new_packet.data = globals.systime
                            self.source.send_packet(new_packet)
                            self.packet_timeout_times[counter] \
                                = globals.systime + self.timeout_time

                            counter += 1


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
