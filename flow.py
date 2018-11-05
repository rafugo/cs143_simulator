class Flow:
    def __init__(self, id, source, destination, amount, start):
        self.id = id
        self.source = source
        self.destination = destination
        self.amount = amount
        self.start = start
        # TODO:
        #       - flow as a list of packets.
        #       - store congestion control algorithm to be used.
        #       - add other fields as necessary for the implementation of
        #         congestion control algorithms.

    # TODO: implement congestion control.
