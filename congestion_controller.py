import sys
import globals

class CongestionController:
    '''
        ssthresh: slow start threshold
        window_size: congestion window size
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
    '''
    def __init__(self, flow_id, cwnd):
        self.flow_id = flow_id
        self.ssthresh = 50
        self.window_size = cwnd
        self.timeout = 1000
        self.not_acknowledged = dict()
        self.timed_out = []
        self.retransmit = False
        self.duplicate_count = 0
        self.last_ack_received = -1
        self.first_packet = 0

    # functions to use before congestion contoller method has actually been implemented
    def ack_received(self, packet):
        sys.exit("Abstract method ack_received not implemented")

    def send_packet(self):
        sys.exit("Abstract method send_packet not implemented")

    def restart(self):
        sys.exit("Abstract method restart not implemented")

# implement TCP Reno
class CongestionControllerReno(CongestionController):

    def __init__(self, flow_id, cwnd):
        # initalize the controller
        CongestionController.__init__(self, flow_id, cwnd)
        # set state to slow start at the beginning
        self.state = "slow_start"
        # id for the packet sent during fast recovery
        self.FR_packet = None

    # processes an acknowledgement packet for TCP Reno
    # packet refers to an acknowledgement packet
    def ack_received(self, packet):
        flow = globals.idmapping['flows'][self.flow_id]

        # check for unacknowledged packets that have timed out
        for (p_id, num_dup) in self.not_acknowledged.keys():
            sent_time = self.not_acknowledged[(p_id, num_dup)]
            elapsed_time = globals.systime - sent_time

            # if the unacknowledged packet has timed out, move it from
            #   unacknowleged to timed out
            if elapsed_time > self.timeout:
                del self.not_acknowledged[(p_id, num_dup)]
                self.timed_out.append((p_id, num_dup))

            # if we have packets that have timed out, we want to retransmit these
            if len(self.timed_out) > 0:
                self.retransmit = True
                # Half the window size
                self.window_size /= 2
            else:
                self.retransmit = False

            # if we receive an ack for a packet, want to remove it from the list of unacked packets
            # TODO: NEED TO IMPLEMENT DUPLICATE COUNT FOR PACKETS
            if (packet.id, packet.duplicate_num) in self.not_acknowledged.keys():
                del self.not_acknowledged[(packet.id, packet.duplicate_num)]

            # In slow start phase, increase congestion window size by 1
            if (self.state == "slow_start"):
                self.window_size += 1
                # If congestion window becomes larger than slow start threshold,
                # switch to congestion avoidance phase
                if (self.window_size >= self.ssthresh):
                    self.state = "congestion_avoidance"

            elif (self.state == "congestion_avoidance"):
                # Check if this is a duplicate acknowledgement
                if packet.next_id == self.last_ack_received:
                    self.duplicate_count += 1
                    # After 3 duplicate acknowledgements, if the packet has not
                    # already been received, halve the congestion window size and
                    # move into fast recovery phase
                    if (self.duplicate_count == 3) and ((packet.id + 1) in \
                        [key[0] for key in self.not_acknowledged.keys()]):
                        self.window_size /= 2
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
                if packet.data == self.last_ack_received:
                    self.duplicate_count += 1
                    return
                else:
                    # check if this is the ACK for the packet transmitted during Fast Recovery
                    if packet.id == self.FR_packet:
                        self.window_size = self.ssthresh
                        self.state = "congestion_avoidance"
                    # reset duplicate count since the chain of dupACKS is broken
                    self.duplicate_count = 0
            self.last_ack_received = packet.id + 1

            self.send_packet()

    # Determine what packet to send based on the current stage of TCP Reno
    def send_packet(self):
         flow = globals.idmapping['flows'][self.flow_id]
         if (self.state == "slow_start" or self.state == "congestion_avoidance"):
            # if we have packets that have timed out that we need to retransmit
            if self.retransmit == True:
                # Retransmit timed out packets
                # if it will all fit into one window
                while (len(self.not_acknowledged) < flow.window_size) and (len(self.timed_out) > 0):
                    # get the first timed out packet
                    (packet_id, dup_num) = self.timed_out[0]
                    # set time on the not acknowledgement packet for when it is sent
                    self.not_acknowledged[(packet_id, dup_num + 1)] = globals.systime
                    # TODO: write a function in flow to send a packet
                    flow.send_a_packet(packet_id, dup_num + 1)
                    # remove the timed out packet from the list to resend
                    del self.timed_out[0]

            # Send packets, without exceeding congestion window size
            else:
                while (len(self.not_acknowledged) < self.window_size) and (self.window_start * 1024 < flow.total):
                    self.not_acknowledged[(self.window_start, 0)] = globals.systime
                    flow.send_a_packet(self.window_start, 0)
                    self.window_start += 1

         # resend dropped packet
         else:
            packet_id = self.last_ack_received
            # packet sent during fast stage
            self.FR_packet = packet_id
            keys = [key for key in self.not_acknowledged.keys() if key[0] == packet_id]
            if len(keys) == 1:
                dup_num = keys[0][1]
                del self.not_acknowledged[(packet_id, dup_num)]
                self.not_acknowledged[(packet_id, dup_num + 1)] = globals.systime
                flow.send_a_packet(packet_id, dup_num + 1)

    def restart(self):
        # Change from fast recovery to slow start phase
        if self.state == "fast_recovery":
            self.state = "slow_start"
        else:
            # halve window size
            self.window_size /= 2
        # Keep track of timed out packets
        # check for unacknowledged packets that have timed out
        for (p_id, num_dup) in self.not_acknowledged.keys():
            sent_time = self.not_acknowledged[(p_id, num_dup)]
            elapsed_time = globals.systime - sent_time
            # if the unacknowledge packet has timed out, move it from
            #   unacknowleged to timed out
            if elapsed_time > self.timeout:
                del self.not_acknowledged[(p_id, num_dup)]
                self.timed_out.append((p_id, num_dup))

            # if we have packets that have timed out, we want to retransmit these
            if len(self.timed_out) > 0:
                self.retransmit = True
            else:
                self.retransmit = False
        self.send_packet()
