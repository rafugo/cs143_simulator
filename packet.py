import globals

class Packet:
    # TODO: figure out how to represent data, most notably being the routing
    #       tables which must be communicated between the routers.
    def __init__(self, sourceid, flowid, destinationid, number_in_sequence, sequence_size, ack_flag, data = ''):
        self.sourceid = sourceid
        self.flowid = flowid
        self.destinationid = destinationid
        self.number_in_sequence = number_in_sequence
        self.sequence_size = sequence_size
        self.ack_flag = ack_flag
        self.data = data

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

    def get_number_in_sequence(self):
        return self.number_in_sequence

    def get_sequence_size(self):
        return self.get_sequence_size

    def get_data(self):
        return self.data

    def get_size(self):
        return self.size
