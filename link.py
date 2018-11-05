class Link:
    def __init__(self, id, rate, delay, buffersize):
        self.id = id
        self.rate = rate
        self.delay = delay
        self.buffersize = buffersize
        # TODO:
        #       - store the buffer
        #       - store information about what the link is connecting
        #       - represent static cost of link.

    # TODO: implement packet sending functionality
