class Packet:
    # TODO: figure out how to represent data, most notably being the routing
    #       tables which must be communicated between the routers.
    def __init__(self, source, destination, numberinsequence, sequencesize, ackflag, data = ''):
        self.source = source
        self.destination = destination
        self.numberinsequence = numberinsequence
        self.sequencesize = sequencesize
        self.ackflag = ackflag
        self.data = data
