import globals
from packet import Packet
from link import Link

class Host:
    def __init__(self, hostid, ip, linkid):
        self.id = hostid
        self.ip = ip
        self.linkid = linkid

        # NOTE: this is the dictionary of flows to packets seen 
        # say there are 3 flows
        #       'flow1id' : [0, 1, 2, 3]
        #       'flow2id' : [0, 1, 2, 3, 4, 6, 7, 8, 9]
        #       'flow3id' : [0, 1]

        self.flow_packets_seen = {}

    # sends the packet by adding (or attempting to add) the packet the link
    # buffer
    def send_packet(self, p):
        # get the actual link object
        connected_link = globals.idmapping['links'][self.linkid]

        # add the packet to the link buffer
        connected_link.add_to_buffer(p, self.id)


    # this is in charge of sending acknowledgements of packets received
    # (as well as notifying the correct flow about the packet)
    def receive_packet(self, p, linkid):
        
        # needs to keep track of what flows it's a part of
        flowid = p.get_flowid();

        # if it's a handshake packet
        if (p.get_packet_type() == globals.HANDSHAKEPACKET):
            # send handshake back
            data = self.id + " " + str(globals.systime)
            ack = Packet(self.id, None, p.get_source(), None, \
                            globals.HANDSHAKEACK, data = data)

            self.send_packet(ack)
            
            print("handshake acknowledgement sent from " + self.id)


        # check what flow the packet pertains to



        # needs to give any acknowledgements to appropriate flows

        # needs to send acknowledgements for packets it receives
        # if it's a packet without 



        print(p.get_data())

    # TODO:
    #      - send packets
    #      - receive packets
    #      - send acknowledgements
    #      - reciee acknowledgements
