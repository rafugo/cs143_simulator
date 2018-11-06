class Flow:
    def __init__(self, id, source, destination, amount, start, congestioncontrol):
        self.id = id
        self.source = source
        self.destination = destination
        self.amount = amount
        self.start = start
        self.packets = []
        self.congestioncontrol = congestioncontrol

        # TODO:
        #       - add other fields as necessary for the implementation of
        #         congestion control algorithms.

    # TODO: implement congestion control.
