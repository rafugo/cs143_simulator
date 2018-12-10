import globals

from host import Host
from link import Link
from packet import Packet
from router import Router

class Flow:
    def __init__(self, id, source, destination, amount,\
                    start, congestion_control, track=True):
        # current size of the window used for the congestion controller
        self.window_size = 1
        self.window_start = 0

        self.FR = -1

        self.rtt = 1
        self.rto = self.rtt
        self.id = id

        if source[0] == 'H':
            self.source = globals.idmapping['hosts'][source]
        else:
            self.source = globals.idmapping['routers'][source]
        if destination[0] == 'H':
            self.destination = globals.idmapping['hosts'][destination]
        else:
            self.destination = globals.idmapping['routers'][destination]

        # converts the amount of data from Megabytes to bits
        '''WHOA! PROBLEM'''
        self.amount = round(((amount *  globals.MEGABITSTOBITS) / globals.PACKETSIZE)) + 1

        # time at which the flow simulation starts, in s
        self.start = start
        self.synack_received = False
        self.min_timeout_time = .5      # in seconds

        self.setRTT = False
        self.state = "slow_start"
        # list of actual packets to be sent
        self.packets = []

        for i in range(self.amount):
            p = None
            p = Packet(self.source.id, self.id, self.destination.id, i, \
                globals.STANDARDPACKET, '')
            self.packets.append(p)


        # flag to demonstrate if the flow has all been sent
        self.done = False
        self.ssthresh = 10000
        # packets that have been sent but not acknowledged yet
        self.send_times = dict()
        # used to calculate RTT
        self.dup_count = dict()
        # congestion signals to keep track of
        self.duplicate_count = 0
        self.duplicate_packet = -2

        self.timeout_marker = 1000
        # the time we can next cut down the window size
        self.next_cut_time = 0
        # Variables for metric tracking
        self.track = track
        self.frwindow = 20000 * globals.dt
        self.frsteps = []
        self.rttwindow = 20000 * globals.dt
        self.rttsteps = []
        self.added = False
        self.successfullytransmitted = {}

        self.LastPacketBeforeLost = 0
        self.transmitted = []

        # If this flow is being tracked, we set up the dictionaries for all of
        # the metrics to be tracked.
        if (track):
            for m in globals.FLOWMETRICS:
                globals.statistics[id+":"+m] = {}

    def process_ack(self, p):
        #print("received ack with data ", p.data)
        #print("recieved ack for ", p.packetid)

        '''THIS ISNT GOING TO WORK'''
        '''if (p.packetid == self.amount - 1):
            self.done = True
            print("donzo")
            return'''
        # print(p.packetid)

        # check to see if this is a packet that has been sent multiple times
        if self.dup_count[p.packetid] < 2:
            if (p.packetid not in self.send_times):
                print(self.send_times)
            self.rtt = globals.systime - self.send_times[p.packetid]
            self.rto = max(self.min_timeout_time, 2 * self.rtt)
            '''before: self.rto = 2 * self.rtt'''
            #self.rto = max(self.min_timeout_time, 1.3 * self.rtt)
            self.timeout_marker = globals.systime + self.rto

        # check if it's a synack
        if (p.packetid == 0):
            # set the rtt
            # get send time from the packet data to calculate intial RTT
            #print(self.send_times)
            self.rtt = globals.systime - self.send_times[p.packetid]
            self.window_start += 1
            del self.send_times[p.packetid]

            self.setRTT = True
            self.synack_received = True
            # good to go ahead and start send packets from the flow now
            self.next_packet_send_time = globals.systime
            if ((self.track) and globals.FLOWRTT in globals.FLOWMETRICS) and (not globals.SMOOTH):
                key = self.id + ":" + globals.FLOWRTT
                globals.statistics[key][globals.systime] = self.rtt
            return

        # if we receive an ack for a packet, want to remove it from the list of unacked packets
        # need to remove the timed out packets from send_times
        '''I Removed this part, adding in for debugging'''
        '''remove = [k for k in self.send_times.keys() if k < p.data]
        for k in remove:
            del self.send_times[k]'''
        '''end of part i removed'''

        if (p.data == self.duplicate_packet):
            #print("Now seen ", self.duplicate_count, " duplicate ACKs in a row")
            self.duplicate_count = self.duplicate_count + 1
            # Checks if three duplicate ACKs have been recieved in a row
            '''if (self.duplicate_count == 3 and globals.systime >= \
                self.next_cut_time):'''
            '''What i had it as ^'''
            if (self.duplicate_count == 3 and globals.systime >= \
                self.next_cut_time and p.data in self.send_times.keys()):
                # Fast Retransmit Fast Recovery time!
                print("SEEN THREE DUP ACKS IN A ROW AT TIME", globals.systime)
                self.state = "fast_recovery"
                self.FR = self.duplicate_packet
                #print("sending packet ", self.duplicate_packet, " at ", globals.systime)

                # Retransmitting the missing packet.
                self.source.send_packet(self.packets[self.duplicate_packet])
                self.dup_count[self.duplicate_packet] += 1
                # Updating ssthresh and window_size appropriately.
                self.ssthresh = max(self.window_size / 2, 2)
                self.window_size = self.ssthresh + 3

                #print('window_size ', self.window_size)
                self.LastPacketBeforeLost = sorted(self.send_times.keys()).pop(0)
                self.state = "congestion_avoidance"
                #print(self.state)

                self.window_start = p.data
                self.next_cut_time = globals.systime + self.rto
            else:
                #window inflation
                self.window_size +=1

                '''changed to else. changing back to debug'''
                ''''''
        else:
            '''if(self.LastPacketBeforeLost != 0):
                if (p.data-1 != self.LastPacketBeforeLost):
                    pass
                    #print("We have arrived at a place we should not be. i am scared.")
                self.LastPacketBeforeLost = 0'''

            # reset our counter for duplicates if we have a new ACK
            '''if(self.duplicate_count > 0):
                self.window_size = self.ssthresh'''
            if(self.duplicate_count >= 3):
                self.window_size = self.ssthresh
            self.duplicate_count = 0
            self.duplicate_packet = p.data
            self.window_start = p.data
            #print("current window start ", self.window_start)

            if (self.window_size < self.ssthresh):
                self.state = "slow_start"
                self.window_size += 1
                #print('window_size ', self.window_size)

            else:
                self.state = "congestion_avoidance"
                self.window_size += 1/self.window_size
                #print('window_size ', self.window_size)

            # Time to do some metric tracking
            if (self.track and globals.FLOWRATE in globals.FLOWMETRICS):
                if p.packetid not in self.successfullytransmitted.keys():
                    self.successfullytransmitted[p.packetid] = 1
                    self.added = True
                    rate = 0
                    assert globals.systime >= self.start
                    if (len(self.frsteps) < self.frwindow/globals.dt):
                        self.frsteps.append(globals.PACKETSIZE)
                        if (globals.systime != self.start ):
                            rate = sum(self.frsteps)/(globals.systime - self.start)
                    else:
                        self.frsteps.pop(0)
                        rate = sum(self.frsteps)/(self.frwindow)

                    key = self.id + ":" + globals.FLOWRATE
                    #print("STORING FLOW RATE")
                    globals.statistics[key][globals.systime] = rate


    # gets called every dt
    def send_packets(self):
        # if we shouldn't do anything, leave
        if self.start >= globals.systime or self.done == True or \
            self.state == "fast_recovery":
            return

        # if we have timed out (not recently)
        if globals.systime >= self.timeout_marker:
            print("timeout with window_start: ", self.window_start, "at time ", globals.systime)
            self.window_size = 1
            if (globals.systime >= self.next_cut_time):
                self.ssthresh = max(self.window_size/2, 2)
                self.next_cut_time = globals.systime + self.rto*2

            self.state = 'slow_start'
            #self.next_cut_time = globals.systime + self.rto

            # need to resend window_start
            self.dup_count = dict()
            self.transmitted = []

            #something is wrong here.
            if (self.window_start in self.send_times.keys()):
                del self.send_times[self.window_start]

            self.rto = max(2 * self.rto, self.min_timeout_time)

            self.timeout_marker = globals.systime + self.rto


        # maybe we should update time out marker here???????????????
        # send everything in the window that has not been sent
        for i in range(self.window_start, min(round(self.window_start + self.window_size), len(self.packets))):
            if i not in self.transmitted:
                #print("sending ", i, " with window start ", self.window_start," and window size ", self.window_size)
                # update duplicate counter
                if i not in self.dup_count.keys():
                    self.dup_count[i] = 1
                else:
                    self.dup_count[i] += 1

                # update the sent time
                self.send_times[i] = globals.systime
                self.transmitted.append(i)

                # # send the packet
                self.source.send_packet(self.packets[i])

    def update_flow_statistics(self):
        #print("current state: ", self.state, " at time: ", globals.systime)
        if (not self.added) and (self.track and globals.FLOWRATE in globals.FLOWMETRICS):
            rate = 0
            self.frsteps.append(0)
            if (len(self.frsteps) < self.frwindow/globals.dt):
                if (globals.systime > self.start):
                    rate = sum(self.frsteps)/(globals.systime - self.start)
            else:
                self.frsteps.pop(0)
                rate = sum(self.frsteps)/(self.frwindow)

            key = self.id + ":" + globals.FLOWRATE
            #print("STORING FLOW RATE")
            globals.statistics[key][globals.systime] = rate

        if (self.track and globals.WINDOWSIZE in globals.FLOWMETRICS):
            key = self.id + ":" + globals.WINDOWSIZE
            globals.statistics[key][globals.systime] = self.window_size

        if  (self.track and globals.FLOWRTT in globals.FLOWMETRICS) and globals.SMOOTH:
            avgrtt = 0
            if (self.setRTT):
                self.rttsteps.append(self.rtt)
                if (len(self.rttsteps) < self.rttwindow/globals.dt) and globals.systime > 0:
                    avgrtt = sum(self.rttsteps)/(globals.systime) * globals.dt
                else:
                    self.rttsteps.pop(0)
                    avgrtt = sum(self.rttsteps)/(self.rttwindow) * globals.dt
                key = self.id + ":" + globals.FLOWRTT
                globals.statistics[key][globals.systime] = avgrtt

        self.added = False

    def completed(self):
        return self.done
