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
               congestion_control : The congestion control algorithm the flow
                                    will use
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
               next_packet_send_time : the time to send the next packet
               packets : a list of the packets of the flow
               next_packet :
               window_size :
               min_rtt :
               done :
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
        self.window_size = 80
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
        # time at which the flow simulation starts, in s
        self.start = start
        # next time to send a packet
        self.next_packet_send_time = self.start
        # list of actual packets to be sent
        self.packets = []
        self.setRTT = False


        amountInPackets = 0
        i = 0
        while (amountInPackets < self.amount):
            p = None
            p = Packet(self.source.id, self.id, self.destination.id, i, \
                globals.STANDARDPACKET, '')
            self.packets.append(p)
            amountInPackets = amountInPackets + globals.PACKETSIZE - globals.PACKETHEADERSIZE
            i = i + 1

        # instance of our congestion controllers
        if (congestion_control == 'reno'):
            self.congestion_control = CongestionControllerReno()
        else:
            self.congestion_control = CongestionController()

        # flag to demonstrate if the
        self.done = False

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
        """ This function processes the acknowledgement packet recieved by its
            source. It should pop the corresponding packet off the queue (may
            bot be the first one if the first wasn't acknowledged).
            Does congestion control if needed
        """
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

            #print("Flow " + self.id + " received ack with number " + str(p.data[0]))
            # send min round trip time
            self.rtt = globals.systime - float(p.data[1])
            #print("______________________NEW RTT CALCULATED: " + \
            #    str(self.rtt) + "______________________")
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




    # attempts to send window_size amount of packets through the host
    def send_packets(self):
        # make sure it's send time
        if (globals.systime >= self.next_packet_send_time):
            # if sending first packet in the flow
            # SEND SYNC PACKET FIRST
            if (self.next_packet == -1):
                #print("Sending first sync_packet")
                # generating sync_packet with data that is the time the packet was sent
                # data is used to calc rtt
                sync_packet = Packet(self.source.id, self.id, self.destination.id, \
                    -1, globals.SYNPACKET, globals.systime)
                self.source.send_packet(sync_packet)
                self.next_packet_send_time = globals.systime + self.rtt


            # need to check when to send the next window size of packets
            elif (not self.done):

                #print("flow " + self.id + " is sending packets")
                # check to see if more than 0 packets exist need to be sent
                assert(self.amount > 0)
                # assumes packet id is the same as its index in the list
                # send a window size of packets
                #if ()
                for p in range(self.next_packet, min(self.next_packet + self.window_size, len(self.packets))):
                    #print("flow " + self.id + " is sending packet no. " + str(self.packets[p].get_packetid()))
                    # adding info to packet about when it is sent
                    self.packets[p].data = globals.systime
                    self.source.send_packet(self.packets[p])
                self.next_packet_send_time += self.rtt
                # log if the flow is completed
                # log when the acknowledgement is received

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
