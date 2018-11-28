import sys

class CongestionController:
    '''
        ssthresh: slow start threshold
        cwnd: congestion window size
        timeout: time period after which TCP times out
        not_acknowledged: Dictionary with IDs of unacknowledged packets as key,
            and timestamp that packet was sent as value
        timed_out: list of packets whose acknowledgements haven't been received,
            and have now timed out
        retransmit: flag describing if packets have timed out and need to be
            retransmitted
        duplicate_count: the number of duplicate acknowledgements to
            determine number of dropped packets
        last_ack_received: ID of the last acknowledgement packet received
        first_packet: ID of the first packet in the congestion window
        flow_id: flow that the congestion controller belongs to
        clock: clock for congestion controller
    '''
    def __init__(self):
        self.ssthresh = 50
        self.cwnd = 2.0
        self.timeout = 1000
        self.not_acknowledged = dict()
        self.timed_out = []
        self.retransmit = False
        self.duplicate_count = 0
        self.last_ack_received = -1
        self.first_packet = 0
        self.flow_id = None
        self.clock = None

    # functions to use before congestion contoller method has actually been implemented
    def acknowledgement_received(self, packet):
        sys.exit("Abstract method acknowledgement_received not implemented")

    def send_packet(self):
        sys.exit("Abstract method send_packet not implemented")

    def restart(self):
        sys.exit("Abstract method wake not implemented")

# implement TCP Reno
class CongestionControllerReno(CongestionController):

    def __init__(self):
        pass

    def acknowledgement_received(self, packet):
        pass

    def send_packet(self):
        pass

    def restart(self):
        pass
