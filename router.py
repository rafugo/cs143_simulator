class Router:
    def __init__(self, id, ip, links):
        self.id = id
        self.ip = ip
        self.links = links
        self.routing_table = {}



    # TODO:
    #       - implement algorithm for routers to discover each other and
    #         communicate routing tables.
    #       - recieve and correctly route (send) packets.

    # Cortland- Here, you accessed the elements stored in the packets (i.e.
    # packet.handshake_flag, packet.source, packet.data, etc.). We should not
    # access these fields directly. Instead, I have created functions in the
    # packet class to retrieve these values for you to avoid directly accessing
    # them. In the future, if you want to access something stored in a packet or
    # link, just use or create functions to access them in their class definition
    # and use that. I did this as much as I could. Eventually, I reached a part
    # of your code that tries to access packet.routing_table_flag, which I don't
    # believe exists, so I just commented out that part for now.
    def receive_packet(self, packet, linkid):

        # Preform different actions depending on what type of packet is sent to the router
        if (packet.is_handshake()):
            # Send back an awknoledgement packet if it recieves a handshake
            data = self.id + " " + globals.systime
            ack = Packet(self.id, None, packet.get_source(), None, 2, data = data)

            # Add the acknowledgement packet to the buffer on the link that sent the data
            linkid.add_to_buffer(self.id, ack)

        elif(packet.is_handshake_ack()):
            # split up the data from the acknowledgement packet
            router_details = packet.get_data().split(" ")

            # Determine the Link Cost Here (Using Link_Delay and Transmit_Time):
            cur_time = globals.systime
            transmit_time = cur_time - router_details[1]
            link_delay = linkid.get_delay()
            link_cost = link_delay + transmit_time


            # Update routing table with new cost information
            self.routing_table[router_details[0]] = [linkid, link_cost]


        '''elif(packet.routing_table_flag):
            # calculate the new routing table based on the old one
            calc_routing_table(packet.data)

        else:
            link_path = routing_table.get(packet.destinationid)[0]

            link_path.add_to_buffer(packet)
        '''





    def foward_packet(self, packet):




    # Send handshake packets to initialize data to adjacent routers
    def init_routing_table(self):

        # Define the handshake packet with the router id as its data
        handshake_packet = Packet(self.id, None, None, None, 3, data = (self.id))

        # send out the handshake packet along every adjacent link
        for l in self.links:
            l.add_to_buffer(handshake_packet)






    # this takes the current routing table that our router has and
    # an external routing table and then calculates the new routing table from those values
    #
    def calc_routing_table(self, table_2):
        pass 
        # 1) Determine Cost of link between "self" router and table_2 router, and the Link ID that it was sent on

        # 2) Add cost to every cost value in the table_2 routing table

        #



        # If the routing
