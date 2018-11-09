import globals
from packet import Packet

class Link:
    def __init__(self, id, connection1, connection2, rate, delay, buffersize):
        global t
        global dt
        self.id = id
        self.rate = rate
        self.delay = delay
        self.buffersize = buffersize
        self.buffer = []
        self.connections = [connection1, connection2]
        self.cost = cost
        self.next_packet_send_time = t + dt

    def add_to_buffer(self, packet, senderID):
        global t
        global dt
        # Checks that we have space in the buffer to add another packet.
        # Note: this makes the assumption that buffersize is in units of the
        #       size of each tuple in the buffer list. It might be simpler to
        #       keep track of the capacity of the buffer (in Mb or a similar
        #       unit) and the total size of the buffer contents in the same unit
        if (len(self.buffer) < buffersize):
            self.buffer.append((packet, senderID == connections[0]))
        # If we just added the (packet, direction) tuple to an empty queue, then
        # we need to update self.next_packet_send_time to be the sum of the
        # current time and self.delay.
        if (len(buffer) == 1):
            self.next_packet_send_time = t + self.delay

        # RAFA: i dont think we need this else statement. We shouldnt be
        # changing the next_packet_send_time unless it's the first packet
        # or we just sent a packet. (I didnt change anything though)
        else:
            self.next_packet_send_time = self.next_packet_send_time + dt


    def send_packet(self):
        global t
        global dt
        # If we are at or have passed the time at which we should send the next
        # packet, we should try to send the next packet.
        if (self.next_packet_send_time <= t):
            # If there is nothing currently in the buffer, we have nothing to
            # send at this time.
            if (len(self.buffer) == 0):
                self.next_packet_send_time = self.next_packet_send_time + dt
            #else:
                # 1) find the object the packet is to going to
                # 2) send the packet to that object.
                # 3) Note that the packet should arrive after the propagation
                #    delay. IDEA: keep track of two more things- the time that
                #    the message stops transmitting and a list of (packet, dir, time)
                #    tuples which will indicate what time a packet should arrive
                #    at the connection in the specified direction.
        
