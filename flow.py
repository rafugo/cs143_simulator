import globals

from congestion_controller import *
from host import Host
from link import Link
from packet import Packet
from router import Router
from congestion_controller import CongestionController

class Flow:
    def __init__(self, id, source, destination, amount,\
                    start, congestion_control, window_size, min_rtt):
        self.id = id
        if source[0] == 'H':
            #print(globals.idmapping['hosts'])
            self.source = globals.idmapping['hosts'][source]
        else:
            self.source = globals.idmapping['routers'][source]
        if destination[0] == 'H':
            self.destination = globals.idmapping['hosts'][destination]
        else:
            self.destination = globals.idmapping['routers'][destination]
        # amount of data to be transmitted in bits
        self.amount = amount * 8 * 10 ** 6
        # time at which the flow simulation starts, in ms
        self.start = start
        # next time to send a packet
        self.next_packet_send_time = start
        # list of actual packets to be sent
        self.packets = []

        amountInPackets = 0
        i = 0
        while (amountInPackets < self.amount):
            p = None
            p = Packet(self.source.id, self.id, self.destination.id, i, \
                globals.STANDARDPACKET, '')
            self.packets.append(p)
            amountInPackets = amountInPackets + globals.PACKETSIZE
            i = i + 1
        print("numberofPackets = ", len(self.packets), "amount =", self.amount, "amount given = ", amount)

        # instance of our congestion controllers
        if (congestion_control == 'reno'):
            self.congestion_control = CongestionControllerReno()
        else:
            self.congestion_control = CongestionController()
        # packet number that the window needs to start at, default first packet
        self.next_packet = -1;
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
        # check if it's a synack
        if (p.get_packet_type() == globals.SYNACK):
            # set the rtt
            self.min_rtt = globals.systime - float(p.data)
            print("______________________NEW RTT CALCULATED: " + str(self.min_rtt) + "______________________")
            self.next_packet = 0

        else:
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
                print()
                print("done sending flow " + self.id)
                print()

    # attempts to send window_size amount of packets through the host
    def send_packets(self):
        # make sure it's send time
        if (globals.systime >= self.next_packet_send_time):
            # if sending first packet in the flow
            # SEND SYNC PACKET FIRST
            if (self.next_packet == -1):
                print("Sending sync_packet")
                sync_packet = Packet(self.source.id, self.id, self.destination.id, \
                    -1, globals.SYNPACKET, globals.systime)
                self.source.send_packet(sync_packet)
                self.next_packet_send_time += self.min_rtt

            # need to check when to send the next window size of packets
            elif (not self.done):

                print("flow " + self.id + " is sending packets")
                # check to see if more than 0 packets exist need to be sent
                assert(self.amount > 0)
                # assumes packet id is the same as its index in the list
                # send a window size of packets
                #if ()
                for p in range(self.next_packet, min(self.next_packet + self.window_size, len(self.packets))):

                    print("flow " + self.id + " is sending packet no. " + str(self.packets[p].get_packetid()))
                    self.source.send_packet(self.packets[p])
                self.next_packet_send_time += self.min_rtt
                # log if the flow is completed
                # log when the acknowledgement is received

    def completed(self):
        return self.done
    # TODO:
    #       - add other fields as necessary for the implementation of
    #         congestion control algorithms.
