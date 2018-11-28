import globals

class Packet:
    # Note: As more packet types are necessary, feel free to add more type codes
    #       here. If you do this, make sure that the ack_flag and size fields
    #       are still set appropriately.
    def __init__(self, sourceid, flowid, destinationid, packetid, \
                 packet_type, data = ''):
        """This function initializes a packet object. Input arguments:
                - sourceid : the string id of the source of the packet
                - flowid : the string id of the flow the packet is associated
                           with
                - destinationid : the string ID of the packet's destination
                - packetid : the number of the packet in its sequence
                - packet_type : a string idetifying the type of the packet,
                                (found in globals).
                    STANDARDPACKET: a normal packet
                    ACKPACKET: an acknowledgement packet
                    ROUTINGPACKET: a routing table packet
                    SYNPACKET: a synchronization packet
                    SYNACK: a synchronization packet acknowledgement
                - data : the data to be sent in the packet"""
        self.sourceid = sourceid
        self.flowid = flowid
        self.destinationid = destinationid
        self.packetid = packetid
        self.data = data
        self.packet_type = packet_type
        self.size = 0

        # sets the acknowledgement flag to be true if the packet is either a
        # normal acknowledgment or a handshake acknoweledgement packet.
        self.ack_flag = (packet_type == globals.ACKPACKET or packet_type == globals.HANDSHAKEACK)

        # set the packet size in bits according to its type.
        if packet_type == globals.ACKPACKET or packet_type == globals.HANDSHAKEACK:
            self.size = globals.ACKSIZE
        elif packet_type == globals.HANDSHAKEPACKET:
            self.size = globals.HANDSIZE
        else:
            self.size = globals.PACKETSIZE

    def is_ack(self):
        return self.ack_flag

    def get_flowid(self):
        return self.flowid

    def get_source(self):
        return self.sourceid

    def get_destination(self):
        return self.destinationid

    def get_packet_type(self):
        return self.packet_type

    def get_data(self):
        return self.data

    def get_size(self):
        return self.size

    def get_packetid(self):
        return self.packetid

    def is_handshake(self):
        return (self.packet_type == globals.HANDSHAKEPACKET)

    def is_handshake_ack(self):
        return (self.packet_type == globals.HANDSHAKEACK)

    def is_routing(self):
        return (self.packet_type == globals.ROUTINGPACKET)
