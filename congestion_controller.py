import sys

class CongestionController:
    '''
        ssthresh: Slow Start Threshold
        cwnd: Congestion Window Size
        timeout: Time period after which TCP times out
        not_acknowledged: Dictionary with IDs of unacknowledged packets as key,
            and timestamp that packet was sent as value
        timed_out: List of packets whose acknowledgements haven't been received,
            and have now timed out
        duplicate_count: Counter of the number of duplicate acknowledgements
            we have received (to determine number of dropped packets)
        last_ack_received: ID of the last acknowledgement packet received
        window_start: ID of the first packet in the congestion window
        retransmit: Boolean specifying whether packets have timed out and must
            be retransmitted
        flow: Flow that the Congestion controller belongs to
        wake_event: Event specifying whether the controller should continue
            sending packets

        event_scheduler: Priority queue of events to hold FlowWakeEvents
        clock: Clock for congestion controller
    '''
    def __init__(self):
        self.ssthresh = 50
        self.cwnd = 2.0
        self.timeout = 1000
        self.not_acknowledged = dict()
        self.timed_out = []
        self.duplicate_count = 0
        self.last_ack_received = -1
        self.window_start = 0
        self.retransmit = False
        self.flow = None
        self.wake_event = None

        self.event_scheduler = None
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
