class Router:
    def __init__(self, id, ip, links):
        self.id = id
        self.ip = ip
        self.links = links
        # TODO:
        #       - each router needs a routing table.
        
    # TODO:
    #       - implement algorithm for routers to discover each other and
    #         communicate routing tables.
    #       - recieve and correctly route (send) packets.
