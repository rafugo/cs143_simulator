# this file will store the global variables yay!
# just import the globals file and access like this:
#       `globals.systime`
#
# worth noting that globals.initialize() only has to be called in the main
# function, and then anything that is created inside of the main function will
# have access to these variables.
#
# for testing purposes, you can initialize it inside your class, but please make
# sure to delete it afterwards as it RESETS THE TIME TO 0!!!!!
from host import Host
from link import Link
from packet import Packet

def initialize():
    # the time for the whole system
    global systime
    systime = 0

    # the time increment settings
    global dt
    dt = 1 * (10**-4)

    # the type: {id : object} mapping of the objects in the network
    global idmapping
    idmapping = {
        'hosts' : {},

        'links' : {},

        'routers' : {},

        'flows' : {}
    }

    global statistics
    statistics = {}

    global LINKRATE
    LINKRATE = "link rate"

    global BUFFEROCCUPANCY
    BUFFEROCCUPANCY = "buffer occupancy"

    global PACKETLOSS
    PACKETLOSS = "packet loss"

    global LINKMETRICS
    LINKMETRICS = [LINKRATE, BUFFEROCCUPANCY, PACKETLOSS]

    global PACKETSIZE
    PACKETSIZE = 1024*8

    global ACKSIZE
    ACKSIZE = 64*8

    global HANDSIZE
    HANDSIZE = 64 * 8

    global STANDARDPACKET
    STANDARDPACKET = 'standard_packet'

    global ACKPACKET
    ACKPACKET = 'ack_packet'

    global ROUTINGPACKET
    ROUTINGPACKET = 'routing_packet'

    global SYNPACKET
    HANDSHAKEPACKET = 'handshake_packet'

    global SYNACK
    HANDSHAKEACK = 'handshake_ack'
