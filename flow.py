import globals

class Flow:
    def __init__(self, id, source, destination, amount, \
                    start, congestion_control, window_size, min_rtt):
        self.id = id
        self.source = source
        self.destination = destination
        self.amount = amount
        self.start = start
        self.packets = []
        self.congestion_control = congestion_control
        self.window_size = window_size
        self.min_rtt = min_rtt

        # processes the acknowledgement packet received by its source.
        # should pop the corresponding packet off the queue (may not be the 
        #   first one if the first wasnt acknowledged)
        # does congestion control if needed
        def process_ack(Packet p):
            pass

        # attempts to send window_size amount of packets through the host
        def send_packets():
            pass

        # TODO:
        #       - add other fields as necessary for the implementation of
        #         congestion control algorithms.


