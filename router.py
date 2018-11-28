from packet import Packet
import globals

class Router:
    def __init__(self, id, ip, links):
        self.id = id
        self.ip = ip
        self.links = links
        self.routing_table = {self.id: ['None', 0]}

        # this is used to keep track of how many handshake acknowledgements are
        # received, so that we know when our routing table is done
        self.handshakes_acked = 0



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
            data = self.id + " " + str(globals.systime)
            ack = Packet(self.id, None, packet.get_source(), None, globals.HANDSHAKEACK, data = data)
            # print ("HANDSHAKE RECIEVED")
            # Add the acknowledgement packet to the buffer on the link that sent the data

            globals.idmapping['links'][linkid].add_to_buffer(ack, self.id)


        elif(packet.is_handshake_ack()):

            print("handshake ack received by " + self.id)

            # split up the data from the acknowledgement packet
            router_details = packet.get_data().split(" ")

            # Determine the Link Cost Here (Using Link_Delay and Transmit_Time):
            cur_time = globals.systime
            transmit_time = cur_time - float(router_details[1])
            link_delay = globals.idmapping['links'][linkid].get_delay()
            link_cost = link_delay + transmit_time
            # print (link_delay)

            # get the old_cost, the old cost is 0 if it didnt exist
            old_cost = self.routing_table.get(router_details[0], [0, 0])[1]
            # Update routing table with new cost information
            difference = old_cost - link_cost

            self.routing_table[router_details[0]] = [linkid, link_cost]

            for key in self.routing_table:
                if (self.routing_table[key][0] == linkid and key != router_details[0]):
                    oldval = self.routing_table[key][1]
                    self.routing_table[key] = [linkid, oldval - difference]


            # our handshake was acknowledged
            self.handshakes_acked += 1

            # if there are no more outstanding handshakes, send out the
            # routing table to other routers
            if self.handshakes_acked == len(self.links):
                self.send_routing_table()
                self.handshakes_acked = 0

        elif(packet.is_routing()):

            # print("Router " + self.id + " received a routing table from " + packet.get_source())
            # calculate the new routing table based on the old one
            self.calc_routing_table(packet.data)

        else:
            self.forward_packet(packet)


    # Function to manage forwarding packets along the routing table
    def forward_packet(self, packet):
        print("-----------------------------Router " + self.id + " is forwarding packet " + str(packet.get_packetid()) + "--------------------------------")
        print (self.routing_table)
        print (packet.get_destination())

        link_path = self.routing_table.get(packet.get_destination())[0]

        # print()
        # print(self.id)
        # print(packet.get_destination())
        # print(self.routing_table)
        globals.idmapping['links'][link_path].add_to_buffer(packet, self.id)

    def send_routing_table(self):
        # print ("ROUTING TABLE SENT")
        for l in self.links:
                # print("sending routing table from " + self.id + " to " + entry)
                # make our packet
                routing_table_packet = \
                    Packet(self.id, None, None, None, globals.ROUTINGPACKET, data = self.routing_table)

                l.add_to_buffer(routing_table_packet, self.id)


    # this gets called to do the dynamic routing
    def recalculate_routing_table(self):
        self.handshakes_acked = 0
        self.init_routing_table()

    # Send handshake packets to initialize data to adjacent routers
    def init_routing_table(self):
        # Define the handshake packet with the router id as its data
        handshake_packet = Packet(self.id, None, None, None, globals.HANDSHAKEPACKET, data = (self.id))

        # send out the handshake packet along every adjacent link
        for l in self.links:
            l.add_to_buffer(handshake_packet, self.id)


    # this takes the current routing table that our router has and
    # an external routing table and then calculates the new routing table from those values
    #
    def calc_routing_table(self, table_2_actual):
        # print (self.id)
        # make a copy of the object so we dont modify it
        table_2 = table_2_actual.copy()
        # print ("table2", table_2, "recieved by", self.id)


        # 1) Determine Cost of link between "self" router and table_2 router, and the Link ID that it was sent on
        updated = False
        router_id = self.id
        con_link_id = table_2.get(router_id)[0]
        cost_between = table_2.get(router_id)[1]


        # Add link cost to all cost values in table_2 routing table
        for key in table_2:

            table_2[key] = [table_2[key][0], table_2[key][1] + cost_between]


        # For each key in table_2, check if it is in the routing table or has a smaller value than the current path
        for key in table_2:
            t2_cost = table_2.get(key)[1]
            rt_cost = self.routing_table.get(key, [0, "not_in"])[1]
            # print("self.routing_table.get(key) " + str(self.routing_table.get(key, [0, "not_in"])[1]))



            # if the destination is currently not in the routing table
            if (rt_cost == "not_in"):
                self.routing_table[key] = [con_link_id, t2_cost]
                updated = True

            # If the destination is in the current routing table but table_2 provides a quicker route
            elif (t2_cost < rt_cost):

                self.routing_table[key] = [con_link_id, t2_cost]
                updated = True

        # If we updated our routing table, send out our new routing table as a packet to all neighboring routers
        # BY: RAFA: Yeah, im currently just making the whole system send out the tables every 5 seconds
        if (updated):

            self.send_routing_table()
