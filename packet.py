import globals

class Packet:
    # Note: As more packet types are necessary, feel free to add more type codes
    #       here. If you do this, make sure that the ack_flag and size fields
    #       are still set appropriately.
    def __init__(self, sourceid, flowid, destinationid, number_in_sequence, \
                 packet_type, data = ''):
        """This function initializes a packet object. Input arguments:
                - sourceid : the string id of the source of the packet
                - flowid : the string id of the flow the packet is associated
                           with
                - destinationid : the string ID of the packet's destination
                - number_in_sequence : the number of the packet in its sequence
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
        self.number_in_sequence = number_in_sequence
        self.data = data
        self.packet_type = packet_type
        self.size = 0

        # sets the acknowledgement flag to be true if the packet is either a
        # normal acknowledgment or a handshake acknoweledgement packet.
        self.ack_flag = (packet_type == 1 or packet_type == 2)

        # set the packet size in bits according to its type.
        if packet_type == 1 or packet_type == 2:
            self.size = globals.ACKSIZE
        elif packet_type == 3:
            self.size = globals.HANDSIZE
        else:
            self.size = globals.PACKETSIZE

    def is_ack(self):
        return self.ack_flag

    def get_flow(self):
        return self.flow

    def get_source(self):
        return self.source

    def get_destination(self):
        return self.destination

    def get_packet_type(self):
        return self.packet_type

    def get_data(self):
        return self.data

    def get_size(self):
        return self.size

    def is_handshake(self):
        return (self.packet_type == 3)

    def is_handshake_ack(self):
        return (self.packet_type == 2)
