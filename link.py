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
               id : The string ID of the link
               droppedpackets : The number of packets that have been dropped
               track : A boolean value indicating if this link is being
                       tracked."""
        # buffer is the size of the buffer in bits (buffersize is in KB)
        buffer = buffersize * 8 * globals.KILOBITSTOBITS
        self.links = {connection1: HalfLink(linkid, connection1, connection2, rate, delay, buffer, track1),  \
                      connection2: HalfLink(linkid, connection2, connection1, rate, delay, buffer, track2)}
        # converts delay from ms to s
        self.delay = delay * globals.MSTOS
        self.id = linkid

        # variables for metric tracking
        self.droppedpackets = 0
        self.track = (track1 or track2)
        # sets up the dictionaries to track all necessary statistics for this
        # link
        if (self.track):
            for m in globals.LINKMETRICS:
                globals.statistics[linkid+":"+m] = {}


    def get_delay(self):
        return self.delay


    def get_effective_rate(self, sender):
        return self.links[sender].get_effective_rate()


    def add_to_buffer(self, packet, sender):
        """This function adds a packet to the buffer on the appropriate side of
           the link if possible, dropping it if there is insufficient space left
           in the buffer. It also updates the global tracking of buffer occupancy
           and packet lossas necessary. """
        # Added will store the number of bits added to the buffer.
        added= self.links[sender].add_to_buffer(packet)

        # If added is 0, we added 0 bytes to the link buffer, so the packet was
        # dropped.
        if (added == 0):
            self.droppedpackets = self.droppedpackets + 1

        # If we are tracking this link and one of the metrics we are tracking
        # is packet loss, it updates the dictionary associated with this
        # link's packet loss metrics.
        if (added == 0) and (self.track and globals.PACKETLOSS in globals.LINKMETRICS):
            key = self.id + ":" + globals.PACKETLOSS
            globals.statistics[key][globals.systime] = self.droppedpackets
            # If the previous time was valid, update the dictionary to show
            # how many packets had been dropped at the previous time step.
            if (globals.systime > 0):
                globals.statistics[key][globals.systime-globals.dt] = self.droppedpackets -1


    def send_packet(self):
        """This function will try to send a packet on both of the half links
           corresponding to the Link."""
        for link in self.links.values():
            link.send_packet()


    def update_link_statistics(self):
        for link in self.links.values():
            link.update_link_statistics()



# This class will represent one direction of the Link. (i.e. all packets
# travelling across a given HalfLink will be going to the same destination).
class HalfLink:
    def __init__(self, id, source, destination, rate, delay, buffersize, track=True):
        """This function initializes new half-link objects
           INPUT ARGUMENTS-
               linkid : The string ID of the link being constructed
               source : The string ID of the object that will be sending packets
                        along this half link
               destination : The string ID of the object that will be recieving
                             packets along this half link
               rate : The link rate of the link (in Mbps)
               delay : The propagation delay of the link (in ms)
               buffersize : The size of the buffer for this link in bits.
               track : A boolean value specifying whether or not the half link
                       should have its metrics tracked
           FIELDS-
               id : The string ID of the link
               rate : The maximum link rate of the link (in bps)
               delay : The propagation delay of the link (in s)
               buffercapacity : The total capacity of the link's buffer (in bits)
               buffersize : The number of bits currently being held in the
                            link's buffer
               buffer : A list of the packets currently in the buffer
               source : The string ID of the object which sends things along
                        this link
               destination : The string ID of the object which recieves things
                             along this link
               next_packet_send_time : The time that we should send (or try to
                                       send) the next packet. If the buffer is
                                       nonempty, this will be the time that
                                       the packet in front of the buffer will
                                       finish transmitting and leave the buffer.
               packets_in_transmission : A list of packets currently propagating
                                         down the link
               packet_arrival_times : A list of the times that the corresponding
                                      packets in packets_in_transmission should
                                      arrive at their destination
               track : A boolean value indicating if this link is being tracked.
               lrwindow : The size of the window (in seconds) over which we are
                          computing link rate for the link rate statistics
               lrsteps : A list of the number of bits which were sent along the
                         link in various timesteps (where the first item represents
                         the earliest time step and the last represents the most
                         recent)
               cost : The cost of this link?
            NOTE- I am not sure whether or not we need cost here at all, as it
                  appears to never be used."""
        self.id = id
        # Converts the link rate from Mbps to bps
        self.rate = rate * globals.MEGABITSTOBITS
        # Converts the propagation delay from ms to s
        self.delay = delay * globals.MSTOS
        self.buffercapacity = buffersize
        self.buffersize = 0
        self.buffer = []
        self.source = source
        self.destination = destination
        self.cost = 0


        #print("BUFFER CAPACITY:")
        #print(buffersize)

        # The first time we should try to send a packet is at the next time step.
        self.next_packet_send_time = globals.systime + globals.dt
        self.packets_in_transmission = []
        self.packet_arrival_times = []

        # Variables for metric tracking
        self.track = track
        self.lrwindow = 15000 * globals.dt
        self.lrsteps = []
        self.buffersteps = []
        self.bufferwindow = 1 * globals.dt
        self.effectiverate = 0
        # If we are tracking this half link, we set up dictionaries for all of
        # its metrics which we are tracking.
        if track:
            for m in globals.HALFLINKMETRICS:
                globals.statistics[id+":"+source+"->"+destination+":"+m] = {}


    def add_to_buffer(self, packet):
        """This function will try to add the Packet packet to the buffer. It
        will only add packet to the buffer if there is still space in the
        buffer for it. Otherwise, the packet will be dropped."""
        # If the buffer is currently empty, the we should send the next packet
        # (i.e. this packet) as soon as it finishes transmitting (which will take
        # time sizeofpacket/transmissionrate)
        if (len(self.buffer) == 0):
            self.next_packet_send_time = globals.systime + (packet.get_size()/self.rate)

        # Checks that there is room to add the packet to the buffer
        if (packet.get_size() + self.buffersize <= self.buffercapacity):
            self.buffersize = self.buffersize + packet.get_size()
            #print("Buffer size %d", self.buffersize, "time:", globals.systime, "flow:", packet.get_flowid())
            self.buffer.append(packet)
        # if there isn't room in the buffer, we return 0 to indicate that the
        # packet was dropped.
        else:
            #print("Dropped packet with buffer size:")
            #print(self.buffersize)
            return 0

        # If we are tracking this link and we are tracking buffer occupancy
        # statistics, we will update the corresponding dictionary accordingly.
        if (self.track and globals.BUFFEROCCUPANCY in globals.HALFLINKMETRICS) and (not globals.SMOOTH):
            key = self.id+":"+self.source+"->"+self.destination+":"+globals.BUFFEROCCUPANCY
            globals.statistics[key][globals.systime] = self.buffersize
            if (globals.systime > 0) and not (globals.systime-globals.dt in globals.statistics[key].keys()):
                globals.statistics[key][globals.systime-globals.dt] = self.buffersize - packet.get_size()

        # returns the size of the packet that was succesfully added to the
        # buffer.
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

            # Otherwise, It's time to send the packet at the front of the buffer
            else:
                packet_to_send = self.buffer.pop(0)
                amountfreed = packet_to_send.get_size()
                # Updates buffersize to reflect that we removed the packet
                # at the front of the buffer from the buffer.
                self.buffersize = self.buffersize - amountfreed

                if (self.track and globals.BUFFEROCCUPANCY in globals.HALFLINKMETRICS) and (not globals.SMOOTH):
                    key = self.id+":"+self.source+"->"+self.destination+":"+globals.BUFFEROCCUPANCY
                    globals.statistics[key][globals.systime] = self.buffersize
                    if (globals.systime > 0) and not (globals.systime-globals.dt in globals.statistics[key].keys()):
                        globals.statistics[key][globals.systime-globals.dt] = self.buffersize + amountfreed

                # Time represents the amount of time in the previous dt that we
                # were transmitting. (i.e. between the previous systime and the
                # current)
                time = self.next_packet_send_time - (globals.systime - globals.dt)
                # bitstransmitted represents the number of bits that were
                # transmitted in the previous dt
                bitstransmitted = time * self.rate

                # Now we need to add the packet that we removed from the
                # buffer to the lists that keep track of the propegation of the
                # packets.
                self.packets_in_transmission.append(packet_to_send)
                self.packet_arrival_times.append(globals.systime + self.delay)

                # If there are still packets in the buffer, update the time
                # to send the next packet to be when it would finish transmitting
                if (len(self.buffer) > 0):
                    next_packet_size = self.buffer[0].get_size()
                    self.next_packet_send_time = globals.systime + \
                        next_packet_size * (1/self.rate)

                # the buffer is empty so we will just set the time to try to
                # send the next packet to be the next time step.
                else:
                    self.next_packet_send_time = self.next_packet_send_time + \
                                                 globals.dt

        # in one of two cases: either buffer is empty or we used link to capacity
        # in last dt.
        else:
            if (len(self.buffer) != 0):
                time = globals.dt
                bitstransmitted = time * self.rate
            else:
                print("buffer is empty and the next_packet_send_time is wrong!")

        # If we are tracking this link and we are tracking link rate for half
        # links, we compute the link rate and update the statistics disctionary
        # appropriately.
        if ((globals.LINKRATE in globals.HALFLINKMETRICS)):
            rate = 0
            self.lrsteps.append(bitstransmitted)
            if(globals.systime <= self.lrwindow):
                if (globals.systime != 0):
                    rate = sum(self.lrsteps)/(globals.systime + globals.dt)
                # when the time is 0, we will just set the rate to be 0.
                else:
                    pass
            else:
                self.lrsteps.pop(0)
                rate = sum(self.lrsteps)/self.lrwindow
            self.effectiverate = rate
            if (self.track):
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
                dest_type = ''
                if self.destination[0] == 'H':
                    dest_type = 'hosts'
                else:
                    dest_type = 'routers'
                receiver = globals.idmapping[dest_type][self.destination]
                receiver.receive_packet(packet_to_send, self.id)

        return amountfreed


    def update_link_statistics(self):
        if (self.track and globals.BUFFEROCCUPANCY in globals.HALFLINKMETRICS) and globals.SMOOTH:
            avgocc = 0
            if(globals.systime <= self.bufferwindow):
                if (globals.systime != 0):
                    self.buffersteps.append(self.buffersize)
                    avgocc = sum(self.buffersteps)*(globals.dt/(globals.systime))
                # when the time is 0, we will just set the rate to be 0.
                else:
                    pass
            else:
                self.buffersteps.pop(0)
                self.buffersteps.append(self.buffersize)
                avgocc = sum(self.buffersteps)/self.bufferwindow
            key = self.id + ":" + self.source + "->" + self.destination + ":" \
                  + globals.BUFFEROCCUPANCY
            dict = globals.statistics[key][globals.systime] = avgocc * globals.dt


    def get_effective_rate(self):
        return self.effectiverate


    def get_buffer_size(self):
        return self.buffersize


    def get_destination(self):
        return self.destination


    def get_source(self):
        return self.source
