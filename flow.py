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
        print(self.amount)
        # time at which the flow simulation starts, in s
        self.start = start
        self.started = False
        # next time to send a packet
        self.next_packet_send_time = self.start
        self.packet_timeout_times = {}
        self.timeout_time = 1       # in seconds
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

        self.ssthresh = 64
        self.timeout = 1000
        # packets that have been sent but not acknowledged yet
        self.send_times = dict()
        # used to calculate RTT
        self.dup_count = dict()
        self.timedout_packets = []

        self.retransmit = False
        # congestion signals to keep track of
        self.duplicate_count = 0
        self.last_ack_received = -1
        self.first_packet = 0

        # Variables for metric tracking
        self.track = track
        self.frwindow = 20000 * globals.dt
        self.frsteps = []
        self.rttwindow = 20000 * globals.dt
        self.rttsteps = []
        self.added = False

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
            if (p.data[0] >  self.next_packet):
                self.next_packet = p.data[0]
            # the next packet to send is out of index so we've sent everything
            if (self.next_packet >= len(self.packets)):
                self.done = True

            # -----------------------------------------------------------------
            # CONGESTION CONTROL
            # -----------------------------------------------------------------

            # check for unacknowledged packets that have timed out
            print("acknowledging packet " + str(p.packetid))
            for p_id in self.send_times.keys():
                sent_time = self.send_times[p_id]
                elapsed_time = globals.systime - sent_time
                # if the unacknowledged packet has timed out, move it from
                #   unacknowleged to timed out
                if elapsed_time > self.timeout:
                    del self.send_times[p_id]
                    self.timedout_packets.append(p_id)
                    print("packet timed out" + str(p_id))

            # if we have packets that have timed out, we want to retransmit these
            if len(self.timedout_packets) > 0:
                print(self.timedout_packets)
                self.retransmit = True
                # Half the window size
                print(self.window_size)
                self.window_size = self.window_size / 2
                print(self.window_size)
            else:
                self.retransmit = False

            # if we receive an ack for a packet, want to remove it from the list of unacked packets
            # TODO: NEED TO IMPLEMENT DUPLICATE COUNT FOR PACKETS
            if p.packetid in self.send_times.keys():
                del self.send_times[p.packetid]

            # In slow start phase, increase congestion window size by 1
            if (self.state == "slow_start"):
                self.window_size += 1
                # If congestion window becomes larger than slow start threshold,
                # switch to congestion avoidance phase
                if (self.window_size >= self.ssthresh):
                    self.state = "congestion_avoidance"

            elif (self.state == "congestion_avoidance"):
                # Check if this is a duplicate acknowledgement
                if p.data[0] == self.last_ack_received:
                    self.duplicate_count += 1
                    # After 3 duplicate acknowledgements, if the packet has not
                    # already been received, halve the congestion window size and
                    # move into fast recovery phase
                    if (self.duplicate_count == 3) and ((p.data) in \
                        [key[0] for key in self.send_times.keys()]):
                        self.window_size = self.window_size / 2
                        self.ssthresh = self.window_size
                        self.state = "fast_recovery"

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
                    # reset duplicate count since the chain of dupACKS is broken
                    self.duplicate_count = 0
            self.last_ack_received = p.packetid + 1

            # --------------------------------------------------------------------------
            # END CONGESTION control

            # Time to do some metric tracking
            if (self.track and globals.FLOWRATE in globals.FLOWMETRICS):
                self.added = True
                rate = 0
                assert globals.systime >= self.start
                if (len(self.frsteps) < self.frwindow/globals.dt):
                    self.frsteps.append(1)
                    if (globals.systime != self.start ):
                        rate = sum(self.frsteps)/(globals.systime - self.start)
                else:
                    self.frsteps.pop(0)
                    self.frsteps.append(globals.PACKETSIZE)
                    rate = sum(self.frsteps)/(self.frwindow)

                key = self.id + ":" + globals.FLOWRATE
                #print("STORING FLOW RATE")
                globals.statistics[key][globals.systime] = rate


    # sliding window packet sending
    def send_packetsV2(self):
        # make sure it's send time
        if (globals.systime >= self.start and self.done == False):
            # if sending first packet in the flow
            # SEND SYNC PACKET FIRST
            if (self.next_packet == -1):

                # if it's the first one or it's timed out, send it again
                if -1 not in self.packet_timeout_times.keys() or \
                        self.packet_timeout_times[-1] <= globals.systime:

                    sync_packet = Packet(self.source.id, self.id, self.destination.id, \
                        -1, globals.SYNPACKET, globals.systime)

                    if -1 not in self.dup_count.keys():
                        self.dup_count[-1] = 1
                    else:
                        self.dup_count[-1] = self.dup_count[-1] + 1

                    self.source.send_packet(sync_packet)
                    self.packet_timeout_times[-1] = globals.systime + self.timeout_time

            else:
            # we have received the sync packet and are ready to begin
                if (self.state == "slow_start" or self.state == "congestion_avoidance"):
                   # if we have packets that have timed out that we need to retransmit
                   if self.retransmit == True:
                       # Retransmit timed out packets
                       # if it will all fit into one window
                       while (len(self.send_times) < self.window_size) and (len(self.timedout_packets) > 0):
                           # get the first timed out packet
                           packet_id = self.timedout_packets[0]
                           # set time on the not acknowledgement packet for when it is sent
                           self.send_times[packet_id] = globals.systime
                           self.dup_count[packet_id] = self.dup_count[packet_id] + 1
                           # when this packet is sent, add to the map with the send time
                           self.source.send_packet(self.packets[packet_id])
                           self.packet_timeout_times[packet_id] = globals.systime + self.timeout_time
                           # remove the timed out packet from the list to resend
                           del self.timed_out[0]


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

                    # if the first packet has ACK, move window over and send the next packet
                    # also, if the "new first packet" also has an ACK, repeat the process
                    # until this is not true
                    if self.next_packet > self.window_start:


                        # move the window over, since the first packets have 
                        # been acked
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

                                print("sending packet: ", round(self.window_start + self.window_size))
                                self.source.send_packet(new_packet)





                        # while self.next_packet > self.window_start:
                        #     # the first packet of the window has been sent, move the window
                        #     # over and send the new packet in the window
                        #     self.window_start += 1




                        #     # if there is a packet after the window, add it to the window and
                        #     # send the packet
                        #     if (self.window_start + self.window_size < len(self.packets)):
                        #         i = round(self.window_start + self.window_size)
                        #         new_packet = self.packets[i]
                        #         self.send_times[i] = globals.systime

                        #         if i not in self.dup_count.keys():
                        #             self.dup_count[i] = 1
                        #         else:
                        #             self.dup_count[i] = self.dup_count[i] + 1

                        #         print("sending packet: ", round(self.window_start + self.window_size))
                        #         self.source.send_packet(new_packet)
                        #         self.packet_timeout_times[i] \
                        #             = globals.systime + self.timeout_time


                        # assert(self.window_start == self.next_packet)
                        # print("self.state     :       ", self.state)
                        # print("window set to: ", self.window_start, "  :  ", \
                        #         self.window_start + self.window_size)


                    # if the first packet timed out, send it again
                    elif self.window_start in self.packet_timeout_times.keys() and \
                        self.packet_timeout_times[self.window_start] <= globals.systime:

                        # send all the consecutive timedout packets starting
                        # from the front of the window
                        counter = self.window_start
                        while counter in self.packet_timeout_times.keys() and \
                            self.packet_timeout_times[counter] <= globals.systime:
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
