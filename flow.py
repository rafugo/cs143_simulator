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

        self.window_size = window_size
        self.min_rtt = min_rtt

        # processes the acknowledgement packet received by its source.
        # should pop the corresponding packet off the queue (may not be the
        #   first one if the first wasnt acknowledged)
        # does congestion control if needed
        def process_ack(Packet p):
            # make sure it's an acknowledgement
            assert p.ack_flag
            # make sure it got to the right place from the right place
            assert packet.source == self.destination
            assert packet.destination == self.source

            # remove the packet from the list of packets that need to be sent
            self.packets.remove(p)
            if (len(self.packets) == 0)
                self.done = True
            # check if pass

        # attempts to send window_size amount of packets through the host
        def send_packets():
            # check to see if more than 0 packets exist need to be sent
            assert(self.amount > 0)

            self.source.send_packet(packet);
            self.amount =

            # log if the flow is completed
            # log when the acknowledgement is received
            pass

        def completed():
            return self.done
        # TODO:
        #       - add other fields as necessary for the implementation of
        #         congestion control algorithms.
