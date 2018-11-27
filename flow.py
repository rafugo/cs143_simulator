import globals

from host import Host
from link import Link
from packet import Packet
from router import Router

class Flow:
    def __init__(self, id, source, destination, amount,\
                    start, congestion_control, window_size, min_rtt):
        self.id = id
        if source[0] == 'H':
            print(globals.idmapping['hosts'])
            self.source = globals.idmapping['hosts'][source]
        else:
            self.source = globals.idmapping['routers'][source]
        if destination[0] == 'H':
            self.destination = globals.idmapping['hosts'][destination]
        else:
            self.destination = globals.idmapping['routers'][destination]
        # amount of data to be transmitted in bytes
        self.amount = amount
        self.total = amount
        # time at which the flow simulation starts, in ms
        self.start = start
        # next time to send a packet
        self.next_packet_send_time = start
        # list of actual packets to be sent
        self.packets = []
        for i in range(0, amount):
            p = None
            p = Packet(self.source.id, self.id, self.destination.id, i, \
                globals.STANDARDPACKET, '')
            self.packets.append(p)
        # instance of our congestion controllers
        self.congestion_control = congestion_control
        # packet number that the window needs to start at, default first packet
        self.next_packet = 0;
        # current size of the window used for the congestion controller
        self.window_size = window_size
        # minimum round trip time used for congestion control
        self.min_rtt = min_rtt
        # flag to demonstrate if the
        self.done = False
        # processes the acknowledgement packet received by its source.
        # should pop the corresponding packet off the queue (may not be the
        #   first one if the first wasnt acknowledged)
        # does congestion control if needed
    def process_ack(self, p):
        # make sure it's an acknowledgement
        assert p.is_ack();
        # make sure it got to the right place from the right place
        assert p.sourceid == self.destination.id
        assert p.destinationid == self.source.id

        print("Flow " + self.id + " received ack with number " + str(p.data))
        # remove the packet from the list of packets that need to be sent
        # p.data contains the id of the next packet it needs
        if (p.data >  self.next_packet):
            self.next_packet = p.data
        # the next packet to send is out of index so we've sent everything
        if (self.next_packet >= len(self.packets)):
            self.done = True

    # attempts to send window_size amount of packets through the host
    def send_packets(self):
        # if sending first packet in the flow
        # SEND SYNC PACKET FIRST
        #if (self.next_packet = 0):

        # need to check when to send the next window size of packets
        if (globals.systime >= self.start and \
            globals.systime >= self.next_packet_send_time):

            # check to see if more than 0 packets exist need to be sent
            assert(self.amount > 0)
            # assumes packet id is the same as its index in the list
            # send a window size of packets
            #if ()
            for p in range(self.next_packet, self.next_packet + self.window_size):
                self.source.send_packet(self.packets[p])
            self.next_packet_send_time += self.min_rtt
            # log if the flow is completed
            # log when the acknowledgement is received

    def completed(self):
        return self.done
    # TODO:
    #       - add other fields as necessary for the implementation of
    #         congestion control algorithms.
