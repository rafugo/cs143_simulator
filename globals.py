# This file stores all global variables used within the simulator.
from host import Host
from link import Link
from packet import Packet

def initialize():
    # Time for the whole system
    global systime
    systime = 0

    # Time increment settings, with dt = 0.0001
    global dt
    dt = 1 * (10**-4)

    # Type: {id : object} mapping of the objects in the network
    global idmapping
    idmapping = {
        'hosts' : {},

        'links' : {},

        'routers' : {},

        'flows' : {}
    }


    # Conversion constants.
    global MEGABITSTOBITS
    MEGABITSTOBITS = 10**6

    global BITSTOMEGABITS
    BITSTOMEGABITS = 10**(-6)

    global MSTOS
    MSTOS = 10**(-3)

    global STOMS
    STOMS = 10**3

    global KILOBITSTOBITS
    KILOBITSTOBITS = 10**(3)

    global BITSTOKILOBITS
    BITSTOKILOBITS = 10**(-3)

    global PRESENTATIONMODE
    PRESENTATIONMODE = True

    global SMOOTH
    SMOOTH = True

    global statistics
    statistics = {}

    global LINKRATE
    LINKRATE = "link rate"

    global BUFFEROCCUPANCY
    BUFFEROCCUPANCY = "buffer occupancy"

    global HALFLINKMETRICS
    HALFLINKMETRICS = [LINKRATE, BUFFEROCCUPANCY]

    global PACKETLOSS
    PACKETLOSS = "packet loss"

    global LINKMETRICS
    LINKMETRICS = [PACKETLOSS]

    global FLOWRATE
    FLOWRATE = "flow rate"

    global FLOWRTT
    FLOWRTT = "flow RTT"

    global WINDOWSIZE
    WINDOWSIZE = "window size"

    global FLOWMETRICS
    FLOWMETRICS = [WINDOWSIZE, FLOWRATE, FLOWRTT]

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

    global HANDSHAKEPACKET
    HANDSHAKEPACKET = 'handshake_packet'

    global HANDSHAKEACK
    HANDSHAKEACK = 'handshake_ack'

    global SYNPACKET
    SYNPACKET = "syn_packet"

    global SYNACK
    SYNACK = "syn_ack"

    global PACKETHEADERSIZE
    PACKETHEADERSIZE = 20 * 8
