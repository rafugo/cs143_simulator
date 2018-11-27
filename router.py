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

    def recieve_packet(self, packet, linkid):

        # Preform different actions depending on what type of packet is sent to the router
        if (packet.handshake_flag):
            # Send back an awknoledgement packet if it recieves a handshake
            data = self.id + " " + globals.systime
            ack = Packet(self.id, packet.source, None, 0, "handshake_ack", False, False, True, data = data)

            # Add the acknowledgement packet to the buffer on the link that sent the data
            linkid.add_to_buffer(self.id, ack)

        elif(packet.handshake_ack_flag):
            # split up the data from the acknowledgement packet
            router_details = packet.data.split(" ")

            # Determine the Link Cost Here (Using Link_Delay and Transmit_Time):
            cur_time = globals.systime
            transmit_time = cur_time - router_details[1]
            link_delay = linkid.delay
            link_cost = link_delay + transmit_time


            # Update routing table with new cost information
            self.routing_table[router_details[0]] = [linkid, link_cost]


        elif(packet.routing_table_flag):
            # calculate the new routing table based on the old one
            calc_routing_table(packet.data)

        else:
            foward_packet(packet)
            





    # Function to manage forwarding packets along the routing table
    def foward_packet(self, packet):
        link_path = routing_table.get(packet.destinationid)[0]

        link_path.add_to_buffer(packet)




    # Send handshake packets to initialize data to adjacent routers
    def init_routing_table(self):

        # Define the handshake packet with the router id as its data
        handshake_packet = Packet(self.id, None, None, 0, "handshake", False, True, False, data = (self.id))

        # send out the handshake packet along every adjacent link
        for l in self.links:
            l.add_to_buffer(handshake_packet)



        


    # this takes the current routing table that our router has and
    # an external routing table and then calculates the new routing table from those values
    #
    def calc_routing_table(self, table_2):
        # 1) Determine Cost of link between "self" router and table_2 router, and the Link ID that it was sent on
        updated = False
        con_link_id = table2.get(router_id)[0]
        cost_between = table_2.get(router_id)[1]


        # Add link cost to all cost values in table_2 routing table
        for key in table_2:
            table_2[key][1] += cost_between

        for key in self.routing_table:


        # For each key in table_2, check if it is in the routing table or has a smaller value than the current path
        for key in table_2:
            t2_cost = table_2.get(key)[1]
            rt_cost = self.routing_table.get(key, [0, "not_in"])[1]

            # if the destination is currently not in the routing table
            if (rt_cost == "not_in"):
                self.routing_table[key] = [con_link_id, t2_cost]

            # If the destination is in the current routing table but table_2 provides a quicker route
            elif (t2_cost < rt_cost):
                self.routing_table[key] = [con_link_id, t2_cost]
                updated = True

        # If we updated our routing table, send out our new routing table as a packet to all neighboring routers












        


        # If the routing









