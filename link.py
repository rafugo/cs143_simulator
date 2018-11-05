class Link:
    def __init__(self, id, connection1, connection2, rate, delay, buffersize):
        self.id = id
        self.rate = rate
        self.delay = delay
        self.buffersize = buffersize
        self.buffer = []
        self.connections = [connection1, connection2]
        # TODO:
        #       - represent static cost of link.

    # TODO: implement packet sending functionality
