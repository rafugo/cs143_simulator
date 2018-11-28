import globals
from packet import Packet

class Link:
    def __init__(self, linkid, connection1, connection2, rate, delay, buffersize, track1=True, track2=True):
        """This function initializes new link objects
           INPUT ARGUMENTS-
               linkid : The string ID of the link being constructed
               connection1 : The string ID of the object connected to one side
                             of the link
               connection2 : The string ID of the object connected to the other
                             side of the link.
               rate : The link rate of the link (in Mbps)
               delay : The propagation delay of the link (in ms)
               buffersize : The size of the buffer for this link in KB.
               track1 : A boolean value specifying whether or not the half link
                        should be tracked in the connection1 -> connection2
                        direction
               track2 : A boolean value specifying whether or not the half link
                        should be tracked in the connection2 -> connection1
                        direction
           Note- I assume here that if we are tracking either of the half links
                 associated with a link, we will also track the link. I don't
                 know if this is necessarily the case, but it seems like a
                 reasonable assumption.
           FIELDS-
               links : A dictionary with entries of the form ID : half link,
                       where ID specifies the ID of the object that will be
                       be sending things along that half link.
               buffercapacity : The total capacity of the link's buffer (in bits)
               delay : The propagation delay of the link (in s)
               id : The string ID of the link """
        buffer = buffersize * 8 * (10**4)
        self.links = {connection1: HalfLink(linkid, connection1, connection2, rate, delay, buffer, track1),  \
                      connection2: HalfLink(linkid, connection2, connection1, rate, delay, buffer, track2)}
        self.bufferavailable = buffer
        self.buffercapacity = buffer
        self.delay = delay * 10 ** (-3)
        self.id = linkid
        self.droppedpackets = 0
        self.track = (track1 or track2)
        if (self.track):
            for m in globals.LINKMETRICS:
                globals.statistics[linkid+":"+m] = {}

    def get_delay(self):
        return self.delay

    def add_to_buffer(self, packet, sender):
        """This function adds a packet to the buffer on the appropriate side of
           the link if possible, dropping it if there is insufficient space left
           in the buffer. It also updates the global tracking of buffer occupancy
           and packet lossas necessary. """
        # Added will store the number of bits added to the buffer.
        added= self.links[sender].add_to_buffer(packet)

        # Updates the variable storing the amount of available space in the
        # link's buffer to reflect that we added "added" bits to the buffer.
        self.bufferavailable = self.bufferavailable - added

        # If added is 0, we added 0 bytes to the link buffer, so the packet was
        # dropped.
        if (added == 0):
            self.droppedpackets = self.droppedpackets + 1
            # If we are tracking packet loss, it updates the dictionary associated
            # with this link's packet loss metrics.
            if (globals.PACKETLOSS in globals.LINKMETRICS):
                current = globals.statistics[self.id + ":" + globals.PACKETLOSS]
                current[globals.systime] = self.droppedpackets
                globals.statistics[self.id + ":" + globals.PACKETLOSS] = current

    def send_packet(self):
        """This function will try to send a packet on both of the half links
           corresponding to the Link."""
        totaloccupancy = 0
        for link in self.links.values():
            totaloccupancy = totaloccupancy + link.send_packet()

        self.bufferavailable = self.bufferavailable + totaloccupancy

# This class will represent one direction of the Link. (i.e. all packets
# travelling across a given HalfLink will be going to the same destination).
class HalfLink:
    def __init__(self, id, source, destination, rate, delay, buffersize, track=True):
        self.id = id
        # Converts the link rate from Mbps to bps
        self.rate = rate * 10 ** 6
        # Converts the propagation delay from ms to s
        self.delay = delay * 10 ** (-3)
        # Converts the buffer size from KB to b
        # Note: we divide the buffersize by two because each half link only
        #       has half the capactiy of the total buffer.
        self.buffercapacity = buffersize
        self.buffersize = 0
        self.buffer = []
        self.source = source
        self.destination = destination
        self.cost = 0
        # The first time we should try to send a packet is at the next time step.
        self.next_packet_send_time = globals.systime + globals.dt
        # A list representing the packets that have been sent by this HalfLink
        # but have not yet reached their destination.
        self.packets_in_transmission = []
        # A list representing the times that the packets that are still in
        # transmission should be arriving at their destination.
        self.packet_arrival_times = []

        self.track = track
        self.lrwindow = 5000 * globals.dt
        self.lrsteps = []
        self.lrsum = 0.0

        if track:
            for m in globals.HALFLINKMETRICS:
                globals.statistics[id+":"+source+"->"+destination+":"+m] = {}

    def get_buffer_size(self):
        return self.buffersize

    def get_destination(self):
        return self.destination

    def get_source(self):
        return self.source

    def add_to_buffer(self, packet):
        """This function will try to add the Packet packet to the buffer. It
        will only add packet to the buffer if there is still space in the
        buffer for it. Otherwise, the packet will be dropped."""
        first_pack = False
        # need to know whether it is the first packet added
        if (len(self.buffer) == 0):
            first_pack = True

        if (packet.get_size() + self.buffersize <= self.buffercapacity):
            self.buffersize = self.buffersize + packet.get_size()
            #print("Buffer size %d", self.buffersize, "time:", globals.systime, "flow:", packet.get_flowid())
            self.buffer.append(packet)
        else:
            return 0

        # if there is only one item in the buffer and we just added it, then
        # we need to update the time to start sending the next packet, which
        # will be the next timestep.
        #
        # Note that it takes the 1 / rate * pack_size to "dequeue"
        if (first_pack):
            self.next_packet_send_time = \
                globals.systime + (1 / self.rate) * (packet.get_size())

        if (self.track and globals.BUFFEROCCUPANCY in globals.HALFLINKMETRICS):
            globals.statistics[self.id+":"+self.source+"->"+self.destination+":"+globals.BUFFEROCCUPANCY][globals.systime] = self.buffersize

        return packet.get_size()


    def send_packet(self):
        amountfreed = 0
        bitstransmitted = 0
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
                packet_to_send = self.buffer.pop(0)
                amountfreed = packet_to_send.get_size()
                self.buffersize = self.buffersize - amountfreed

                # time represents the amount of time in the previous dt that we
                # were transmitting.
                time = self.next_packet_send_time - (globals.systime - globals.dt)
                # bitstransmitted represents the number of bits that were
                # transmitted in the previous dt
                bitstransmitted = time * self.rate


                # append the packet to the transmission
                self.packets_in_transmission.append(packet_to_send)
                self.packet_arrival_times.append(globals.systime + self.delay)

                # get the earliest time we can send the next packet
                if (len(self.buffer) > 0):
                    next_packet_size = self.buffer[0].get_size()
                    self.next_packet_send_time = globals.systime + \
                        next_packet_size * (1/self.rate)

                # the buffer is empty so we will just set the time to try to
                # send the next packet to be the next time step.
                else:
                    self.next_packet_send_time = self.next_packet_send_time + \
                                                 globals.dt

        #in one of two cases: either buffer is empty or we used link to capacity
        # in last dt.
        else:
            if (len(self.buffer) != 0):
                time = globals.dt
                bitstransmitted = time * self.rate
            else:
                print("buffer is empty and the next_packet_send_time is wrong!")

        # Checks if we are tracking this halflink and if we are tracking the
        # link rate of halflinks.
        if ((self.track) and (globals.LINKRATE in globals.HALFLINKMETRICS)):
            rate = 0
            if(globals.systime < self.lrwindow):
                if (globals.systime != 0):
                    self.lrsteps.append(bitstransmitted)
                    #self.lrsum = self.lrsum + bitstransmitted
                    rate = sum(self.lrsteps)/globals.systime
                    if (rate < 0):
                        pass
                        #print("havent reached window size, but negative link rate")

                # when the time is 0, we will just set the rate to be 0.
                else:
                    pass
            else:
                remove = self.lrsteps.pop(0)
                self.lrsteps.append(bitstransmitted)
                #self.lrsum = self.lrsum - remove + bitstransmitted
                rate = sum(self.lrsteps)/self.lrwindow
                """if (rate < 0):
                    print("negative link rate")
                    if (self.lrsum < 0):
                        print("negative sum")
                        print("removed: ", remove, "sum: ",sum(self.lrsteps))
                    else:
                        print("negative window")
                else:
                    print("not negative yet")"""
            key = self.id + ":" + self.source + "->" + self.destination + ":" \
                  + globals.LINKRATE
            dict = globals.statistics[key][globals.systime] = rate

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
                dest_type = ''
                # if first letter is an H
                if self.destination[0] == 'H':
                    dest_type = 'hosts'
                else:
                    dest_type = 'routers'

                receiver = globals.idmapping[dest_type][self.destination]
                receiver.receive_packet(packet_to_send, self.id)

                print("packet delivered")


        # use linkused here for tracking purposes
        return amountfreed
