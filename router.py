class Router:
    def __init__(self, id, ip, links):
        self.id = id
        self.ip = ip
        self.links = links
        self.routing_table = []


        
    # TODO:
    #       - implement algorithm for routers to discover each other and
    #         communicate routing tables.
    #       - recieve and correctly route (send) packets.

    def recieve_packet(self, h, linkid):
        if (h.handshake_flag):
            # Do whatever needs to be done if the packet is receiving a handshake (send awknoledgement back)

        elif(h.handshake_ack_flag):
            # If router recieves a handshake awk add values to the routing table 

        # Other options can be routing table data, etc...





    # have location change ? who knows
    def init_routing_table(self):

        # we need to determine what this packet is
        handshake_packet = Packet()


        # send out the handshake packet along every adjacent link
        for l in self.links:
            l.add_to_buffer(self.ip, handshake_packet)


        


    # this function will run when sent a routing table
    def calc_routing_table():

        # If the routing