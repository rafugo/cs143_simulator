from packet import Packet
import globals

class Router:
    def __init__(self, id, links):
        self.id = id
        self.ip = 0
        self.links = links
        self.routing_table = {self.id: ['']}
        self.link_state_array = []
        # this is used to keep track of how many handshake acknowledgements are
        # received, so that we know when our routing table is done
        self.handshakes_acked = 0


    def receive_packet(self, packet, linkid):
        # Preform different actions depending on what type of packet is sent to the router
        if (packet.is_handshake()):
            # Send back an awknoledgement packet if it recieves a handshake
            data = self.id
            ack = Packet(self.id, None, packet.get_source(), None, globals.HANDSHAKEACK, data = data)
            # print ("HANDSHAKE RECIEVED")
            # Add the acknowledgement packet to the buffer on the link that sent the data
            globals.idmapping['links'][linkid].add_to_buffer(ack, self.id)

        elif(packet.is_handshake_ack()):

            self.receive_handshake_ack(packet, linkid)

        elif(packet.is_routing()):

            self.receive_link_state(packet.data)

        else:
            self.forward_packet(packet) 


    # Function to manage forwarding packets along the routing table
    def forward_packet(self, packet):
        link_path = self.routing_table.get(packet.get_destination())
        globals.idmapping['links'][link_path].add_to_buffer(packet, self.id)
        
    # Send the initial handshake packet to the adjacent routers and to determine which nodes are connected
    def send_handshake(self):
        # Define the handshake packet with the router id as its data
        handshake_packet = Packet(self.id, None, None, None, globals.HANDSHAKEPACKET, data = self.id)

        # send out the handshake packet along every adjacent link
        for l in self.links:
            l.add_to_buffer(handshake_packet, self.id)


    def recalc_link_state(self):
        # Updating the link_state_array

        


        for l in self.links:
            # make our packet
            for conn in self.link_state_array:
                if (l.id == conn[2]):
                    lin = globals.idmapping['links'][conn[2]]
                    conn[3] = lin.get_effective_rate(conn[0]) + lin.get_delay()



        self.send_link_state()


    # Send out our link state array to neighbors
    def send_link_state(self):
        for l in self.links:
            routing_table_packet = \
                Packet(self.id, None, None, None, globals.ROUTINGPACKET, data = self.link_state_array)

            l.add_to_buffer(routing_table_packet, self.id)

    # What to do when you recieve a handshake acknowledgement
    def receive_handshake_ack(self, packet, linkid):
        self.handshakes_acked += 1
        link = globals.idmapping['links'][linkid]
        other_router = packet.get_data().split(' ')[0]


        self.link_state_array.append([self.id, other_router, linkid, link.get_delay() + link.get_effective_rate(self.id)])
        self.link_state_array.append([other_router, self.id, linkid, link.get_delay() + link.get_effective_rate(other_router)])

        if self.handshakes_acked == len(self.links):
            # print ("sending link state array for router: ", self.id)
            self.recalc_link_state()
            self.handshakes_acked = 0

    def receive_link_state(self, state_array_actual):
        state_array = state_array_actual.copy()
        is_updated = False
        # print ("state array for router:, ", self.id, "is here: ", state_array)


    

        for value in state_array:
            if self.id in (value[0], value[1]):
                state_array.remove(value)

        for item in state_array:
            in_array = False
            for value in self.link_state_array:
                if (item[0], item[1]) == (value[0], value[1]):
                    if(self.id == 'R1' and item[0] == 'R2' and item[1] == 'R4'):
                        print ("item:", item[3])

                        print ("value", value[3])

                    in_array = True     
                    if(value[3] != item[3]):
                        value[3] = item[3]
                        print ("went in this")
                        is_updated = True

            if in_array == False:
                self.link_state_array.append(item)
                is_updated = True

        

            # print ("updated in recieve_link_state for router: ", self.id)
        self.run_dijkstra()
        if is_updated:

            self.send_link_state()






    def run_dijkstra(self):

        if(self.id == "R1"):
            print ("R1 state array Before: ", self.link_state_array)

        unvisited_nodes = []
        nodes = {}
        start_node = self.id
        seen_nodes = []

        # populate unvisited nodes list
        for item in self.link_state_array:
            unvisited_nodes.append(item[0])

        unvisited_nodes = list(set(unvisited_nodes))
        unvisited_nodes = sorted(unvisited_nodes)

        # initialize all nodes as infinity distance
        for item in unvisited_nodes:
            nodes[item] = [float('inf'), '']

        nodes[start_node] = [0, '']
        current_node = start_node
        seen_nodes.append(start_node)
  
        # while we have unvisited nodes
        while unvisited_nodes != []:

            # remove the node we are currently on
            unvisited_nodes.remove(current_node)

            
            # find the shortest path from that start node
            for item in self.link_state_array:
                if item[0] == current_node:
                    if(item[3] + nodes[current_node][0] < nodes[item[1]][0]):
                        if(nodes[current_node][1] == ''):
                            nodes[item[1]] = [item[3] + nodes[current_node][0], item[2]]
                        else:
                            nodes[item[1]] = [item[3] + nodes[current_node][0], nodes[current_node][1]]
                    if item[1] not in seen_nodes:
                        seen_nodes.append(item[1])

            if unvisited_nodes != []:
                for node in unvisited_nodes:
                    if node in seen_nodes:
                        current_node = node
                        break


        rt = {}
        for key in nodes:
            rt[key] = nodes.get(key)[1]

        self.routing_table = rt


        if(self.id == "R1"):
            print ("R1 routing table: ", self.routing_table)





