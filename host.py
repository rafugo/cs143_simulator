import globals
from packet import Packet
from link import Link

# This class simulates the behavior of a host in our network
class Host:
     """
    This function initializes a host object. Input arguments:
        - hostid : the string id of the host object
        - linkid : the id of the link associated with the host

        Attributes :
        - ip : ip address associated with the host
        - flow_packets_seen : dictionary of flows to packets seen
    """
    def __init__(self, hostid, linkid):
        self.id = hostid
        self.ip = 0
        self.linkid = linkid

        # NOTE: this is the dictionary of flows to packets seen
        # say there are 3 flows
        #       'flow1id' : [0, 1, 2, 3]
        #       'flow2id' : [0, 1, 2, 3, 4, 6, 7, 8, 9]
        #       'flow3id' : [0, 1]
        self.flow_packets_seen = {}

    # Sends the packet by adding (or attempting to add) the packet the link
    # buffer
    def send_packet(self, p):
        # Get the actual link object
        connected_link = globals.idmapping['links'][self.linkid]
        connected_link.add_to_buffer(p, self.id)
    
    # Sends acknowledgements of packets received and notifies the correct flow
    def receive_packet(self, p, linkid):
        # Keep track of what flows it's a part of
        flowid = p.get_flowid()
        # If it's a handshake packet
        if (p.get_packet_type() == globals.HANDSHAKEPACKET):
            # Send handshake back
            data = self.id + " " + str(globals.systime)
            ack = Packet(self.id, None, p.get_source(), None, \
                            globals.HANDSHAKEACK, data = data)
            self.send_packet(ack)

        # If it's a standard packet, it's from a flow
        elif (p.get_packet_type() == globals.STANDARDPACKET):
            # If we've already seen the flow before, add to its dict
            if flowid in self.flow_packets_seen.keys():
                # If the packet is a new packet, add it in the right spot
                if p.get_packetid() not in self.flow_packets_seen[flowid]:
                    self.flow_packets_seen[flowid].append(p.get_packetid())
                    self.flow_packets_seen[flowid] = sorted(self.flow_packets_seen[flowid])
                # Otherwise, do nothing

            # Otherwise, it's a new flow and we need to add it to the dict
            else:
                self.flow_packets_seen[flowid] = [p.get_packetid()]

            # Now we need to send an ack back!
            # So, we need to find the smallest number that has not been
            # received in the sequence
            packetid_needed = -1
            packets_gotten = self.flow_packets_seen[flowid]
            for i in range(len(packets_gotten)):
                # If we have seen a packet id and the next one has also been
                # seen, then update the packet_needed
                if packetid_needed + 1 == packets_gotten[i]:
                    packetid_needed += 1
                else:
                    break
            # We now have the smallest value that is missing consecutively
            # Time to send the ack packets
            ack = Packet(self.id, flowid, p.get_source(), p.get_packetid(), \
                            globals.ACKPACKET, data = packetid_needed + 1)
            self.send_packet(ack)

        # If it's an acknowledgement, let the flow know we received it
        elif (p.get_packet_type() == globals.ACKPACKET):
            flowid = p.get_flowid()
            flow = globals.idmapping['flows'][flowid]
            # Process the acknowledgement
            flow.process_ack(p)
