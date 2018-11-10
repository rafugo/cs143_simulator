import globals
from packet import Packet

# Something to think about- right now, we are considering an entire packet to
# be in the buffer until it has finished transmitting. I don't know if this is
# sufficient or if we need to free space in the buffer as we transmit the
# the packet. It seems like that might be more detailed than necessary, so for
# now I am leaving it as is, but especially if we notice unexpected packet loss
# or buffer size metrics later, perhaps we should reconsider.

class Link:
    def __init__(self, id, connection1, connection2, rate, delay, buffersize, \
                  cost):
        # note: self.links will be a dictionary of the form ID: link where ID
        # specifies the ID of the object that will be sending things along the
        # link.
        self.links = {connection1: HalfLink(id, connection2, rate, delay, \
                      buffersize, cost), connection2: HalfLink(id, connection1,\
                      rate, delay, buffersize, cost)}

    # Now when we call add_to_buffer() on a Link, we need to identify which of
    # its HalfLinks we should be adding the packet to and add it appropriately.
    def add_to_buffer(self, packet, sender):
        self.links[sender].add_to_buffer(packet)

    # Now, when we call send_packet() at every time step, we need to try to
    # send a packet on both of the HalfLinks corresponding to the Link
    def send_packet(self):
        for link in self.links.values():
            link.send_packet()

# This class will represent one direction of the Link. (i.e. all packets
# travelling across a given HalfLink will be going to the same destination).
class HalfLink:
    def __init__(self, id, destination, rate, delay, buffersize, cost):
        self.id = id
        # Converts the link rate from Mbps to bps
        self.rate = rate * 10^6
        # Converts the propagation delay from ms to s
        self.delay = delay * 10^(-3)
        # Converts the buffer size from KB to b
        self.buffersize = buffersize * 8 * (10**4)
        self.buffer = []
        self.destination = destination
        self.cost = cost
        # The first time we should try to send a packet is at the next time step.
        self.next_packet_send_time = globals.systime + globals.dt
        # A list representing the packets that have been sent by this HalfLink
        # but have not yet reached their destination.
        self.packets_in_transmission = []
        # A list representing the times that the packets that are still in
        # transmission should be arriving at their destination.
        self.packet_arrival_times = []

    def add_to_buffer(self, packet):
        """This function will try to add the Packet packet to the buffer. It
        will only add packet to the buffer if there is still space in the
        buffer for it. Otherwise, the packet will be dropped."""
        
        first_pack = False
        # need to know whether it is the first packet added
        if (len(self.buffer) == 0):
            first_pack = True

        if (packet.get_size() <= self.buffersize):
            self.buffersize = self.buffersize - packet.get_size()
            self.buffer.append(packet)

        else:
            # here we should update the metrics to indicate we dropped a packet
            print('packet dropped')
            return

        # if there is only one item in the buffer and we just added it, then
        # we need to update the time to start sending the next packet, which
        # will be the next timestep.
        #
        # Note that it takes the rate * 1 / pack_size to "dequeue"
        if (first_pack):
            self.next_packet_send_time = \
                globals.systime + self.rate * (1 / packet.get_size())


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

                # If we have finished transmitting the packet in the last dt,
                # we should remove the packet at the beginning of the buffer
                # and add it to the packets_in_transmission list of packets
                # as well as adding the time it should arrive at its destination
                # to the list of packet_arrival_times. We will also need to
                # update the time to send the next packet.
                if (self.next_packet_send_time <= globals.systime):
                    packet_to_send = self.buffer.pop(0)
                    current_packet_size = packet_to_send.get_size()
                    self.buffersize = self.buffersize + current_packet_size

                    # append the packet to the transmission
                    self.packets_in_transmission.append(packet_to_send)
                    self.packet_arrival_times.append(globals.systime + self.delay)
                    
                    # get the next earliest time we can send the next packet
                    if (len(self.buffer) > 0):
                        next_packet_size = self.buffer[0].get_size()
                        self.next_packet_send_time = \
                            globals.systime + self.rate * (1 / packet.size())

                    else:
                        self.next_packet_send_time = \
                            self.next_packet_send_time + globals.dt

        # If there are no packets in transmission, we don't need to check if
        # any would have arrived at their destination during the last dt.
        if (len(self.packet_arrival_times) > 0):
            # If the time has passed the arrival time at the front of the list
            # of packet_arrival_times, we should remove the first item of the
            # list of packet_arrival_times, as well as the corresponding first
            # element of the list of packets_in_transmission and we should send
            # that packet to its destination.
            if (self.packet_arrival_times[0] <= globals.systime):

                # pop the packet and arrival time
                packet_to_send = self.packets_in_transmission.pop(0)
                self.packet_arrival_times.pop(0)

                # deliver it
                receiver = globals.idmapping[self.destination]
                receiver.receive_packet(packet_to_send)

                print("packet delivered")
