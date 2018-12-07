import globals
from packet import Packet
from link import Link

class Host:
    def __init__(self, hostid, linkid):
        self.id = hostid
        self.ip = 0
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
        connected_link.add_to_buffer(p, self.id)


    # this is in charge of sending acknowledgements of packets received
    # (as well as notifying the correct flow about the packet)
    def receive_packet(self, p, linkid):

        # print("some packet received by host " + self.id)

        # needs to keep track of what flows it's a part of
        flowid = p.get_flowid();

        # if it's a handshake packet
        if (p.get_packet_type() == globals.HANDSHAKEPACKET):
            # send handshake back
            data = self.id + " " + str(globals.systime)
            ack = Packet(self.id, None, p.get_source(), None, \
                            globals.HANDSHAKEACK, data = data)

            self.send_packet(ack)

        # if it's a standard packet, it's from a flow
        elif (p.get_packet_type() == globals.STANDARDPACKET):
            if p.packetid == 169:
                print("++++++++++++++++++++++++++++++host has received 169 ", globals.systime)


            #print("standard packet received by " + self.id)
            # if we've already seen the flow before, add to its dict
            if flowid in self.flow_packets_seen.keys():

                # if the packet is a new packet, add it in the right spot
                if p.get_packetid() not in self.flow_packets_seen[flowid]:
                    self.flow_packets_seen[flowid].append(p.get_packetid())
                    self.flow_packets_seen[flowid] = sorted(self.flow_packets_seen[flowid])

                # otherwise do nothing

            # otherwise it's a new flow so we need to add it to the dict
            else:
                self.flow_packets_seen[flowid] = [p.get_packetid()]

            # now we need to send an ack back!
            # note that we need to find the smallest number that has not been
            # received in the sequence
            packetid_needed = -1
            packets_gotten = self.flow_packets_seen[flowid]

            for i in range(len(packets_gotten)):

                # if we have seen a packet id and the next one has also been
                # seen, then update it
                if packetid_needed + 1 == packets_gotten[i]:
                    packetid_needed += 1

                else:
                    break

            # we now have the smallest value that is missing consecutively
            # send the ack packet

            ack = Packet(self.id, flowid, p.get_source(), p.get_packetid(), \
                            globals.ACKPACKET, data = packetid_needed + 1)
            self.send_packet(ack)

        # if it's an acknowledgement, let the flow know we got one
        elif (p.get_packet_type() == globals.ACKPACKET):

            flowid = p.get_flowid()
            flow = globals.idmapping['flows'][flowid]

            # process the acknowledgement

            #print("ack given to flow "+flowid+" from host "+self.id)
            flow.process_ack(p)
