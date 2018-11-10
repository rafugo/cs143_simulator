import globals
from packet import Packet

class Link:
    def __init__(self, id, connection1, connection2, rate, delay, buffersize, \
                  cost):
        # note: self.links will be a dictionary of the form ID: link where ID
        # specifies the ID of the object that will be sending things along the
        # link.
        self.links = {connection1: HalfLink(id, connection2, rate, delay, \
                      buffersize, cost), connection2: HalfLink(id, connection1,\
                      rate, delay, buffersize, cost)}

    def add_to_buffer(self, packet, sender):
        self.links[sender].add_to_buffer

    def send_packet(self):
        for link in self.links.values():
            link.send_packet

class HalfLink:
    def __init__(self, id, destination, rate, delay, buffersize, cost):
        self.id = id
        # Converts the link rate from Mbps to bps
        self.rate = rate * 10^6
        # Converts the propagation delay from ms to s
        self.delay = delay * 10^(-3)
        # Converts he buffer size from KB to b
        self.buffersize = buffersize * 8 * 10^4
        self.buffer = []
        self.destination = destination
        self.cost = cost
        self.next_packet_send_time = globals.systime + globals.dt
        self.packets_in_transmission = []
        self.packet_arrival_times = []

    def add_to_buffer(self, packet):
        is_ack = packet.is_ack()

        if (is_ack and ACKSIZE >= self.buffersize):
            self.buffersize = self.buffersize - ACKSIZE
            self.buffer.append(packet)
        elif ((not is_ack) and PACKETSIZE >= self.buffersize):
            self.buffersize = self.buffersize - PACKETSIZE
            self.buffer.append(packet)

        if (len(self.buffer) == 1):
            self.next_packet_send_time = globals.systime + globals.dt


    def send_packet(self):
        # If we are at or have passed the time at which we should send the next
        # packet, we should try to send the next packet.
        if (self.next_packet_send_time <= globals.systime):
            # If there is nothing currently in the buffer, we have nothing to
            # send at this time.
            if (len(self.buffer) == 0):
                self.next_packet_send_time = \
                    self.next_packet_send_time + globals.dt

            # Otherwise, we should work on sending the packet at the front of
            # the buffer.
            else:
                is_ack = self.buffer[0].is_ack()
                current_packet_size = PACKETSIZE
                if (is_ack):
                    current_packet_size = ACKSIZE

                # If we have finished transmitting the packet in the last dt,
                # we should remove the packet at the beginning of the buffer
                # and add it to the packets_in_transmission list of packets
                # as well as adding the time it should arrive at its destination
                # to the list of packet_arrival_times. We will also need to
                # update the time to send the next packet.
                if (self.next_packet_send_time + self.rate * current_packet_size <= globals.systime):
                    packet_to_send = self.buffer.pop()
                    self.packets_in_transmission.append(packet_to_send)
                    self.packet_arrival_times.append(globals.systime + self.delay)
                    self.next_packet_send_time = self.next_packet_send_time + globals.dt

        # If there are no packets in transmission, we don't need to check if
        # any would have arrived at their destination during the last dt.
        if (len(packet_arrival_times) > 0):
            # If the time has passed the arrival time at the front of the list
            # of packet_arrival_times, we should remove the first item of the
            # list of packet_arrival_times, as well as the corresponding first
            # element of the list of packets_in_transmission and we should send
            # that packet to its destination.
            if (packet_arrival_times[0] <= globals.systime):
                reciever = globals.idmapping[self.destination]
                packet_to_send = self.packets_in_transmission.pop()
                self.next_packet_send_time.pop()
                reciever.recieve_packet(packet_to_send)
