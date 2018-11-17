import globals

class Packet:
    # TODO: figure out how to represent data, most notably being the routing
    #       tables which must be communicated between the routers.
    def __init__(self, sourceid, flowid, destinationid, number_in_sequence, packet_type, ack_flag, data = ''):
        self.sourceid = sourceid
        self.flowid = flowid
        self.destinationid = destinationid
        self.number_in_sequence = number_in_sequence
        self.ack_flag = ack_flag
        self.data = data
        self.packet_type = packet_type
        self.size = 0

        # set the packet size in bits
        if ack_flag:
            self.size = globals.ACKSIZE
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
