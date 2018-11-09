import packet import Packet

class Host:
    def __init__(self, id, linkid):
        self.id = id
        self.linkid = linkid

    # sends the packet by adding (or attempting to add) the packet the link
    # buffer
    def send_packet(Packet p):
        # TODO: get a function that translates linkid to a link object, 
        # then call add_to_buffer on that link

    # this is in charge of sending acknowledgements of packets received
    # (as well as notifying the correct flow about the packet)
    def receive_packet(Packet p):
        # TODO:

        # check whether packet or acknowledgement

        # if packet, send ack to the source of the packet

        # if ack, call corresponding flow's `process_ack(p)`

    # TODO:
    #      - send packets
    #      - receive packets
    #      - send acknowledgements
    #      - reciee acknowledgements
