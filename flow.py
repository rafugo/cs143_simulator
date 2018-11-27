import globals

class Flow:
    def __init__(self, id, source, destination, amount, \
                    start, congestion_control, window_size, min_rtt):
        self.id = id
        self.source = source
        self.destination = destination
        # amount of data to be transmitted in bytes
        self.amount = amount
        self.total = amount
        # time at which the flow simulation starts, in ms
        self.start = start
        # list of actual packets to be sent
        self.packets = []
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
        def process_ack(Packet p):
            # make sure it's an acknowledgement
            assert is_ack(p);
            # make sure it got to the right place from the right place
            assert packet.source == self.destination
            assert packet.destination == self.source

            # remove the packet from the list of packets that need to be sent
            if (p.data >  next_packet)
                next_packet = p.data
            # the next packet to send in out of index so we've sent everything
            if (next_packet >= len(packets))
                self.done = True

        # attempts to send window_size amount of packets through the host
        def send_packets():
            # check to see if more than 0 packets exist need to be sent
            assert(self.amount > 0)
            # assumes packet id is the same as its index in the list
            # send a window size of packets
            for (p in range(next_packet, next_packet + window_size)):
                self.source.send_packet(packets(p));

            # log if the flow is completed
            # log when the acknowledgement is received

        def completed():
            return self.done
        # TODO:
        #       - add other fields as necessary for the implementation of
        #         congestion control algorithms.
