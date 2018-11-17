import globals
from packet import Packet
from link import Link

class Host:
    def __init__(self, hostid, ip, linkid):
        self.id = hostid
        self.ip = ip
        self.linkid = linkid

    # sends the packet by adding (or attempting to add) the packet the link
    # buffer
    def send_packet(self, p):
        # get the actual link object
        connected_link = globals.idmapping['links'][self.linkid]

        # add the packet to the link buffer
        connected_link.add_to_buffer(p, self.id)
        pass

    # this is in charge of sending acknowledgements of packets received
    # (as well as notifying the correct flow about the packet)
    def receive_packet(self, p):
        # TODO:

        # check whether packet or acknowledgement

        # if packet, send ack to the source of the packet

        # if ack, call corresponding flow's `process_ack(p)`

        print(p.get_data())

    # TODO:
    #      - send packets
    #      - receive packets
    #      - send acknowledgements
    #      - reciee acknowledgements
