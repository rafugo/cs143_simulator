import globals
from host import Host
from link import Link
from packet import Packet

class Simulator:
    # I'm not actually sure that the things that we thought would be fields of
    # the simulator class should be. I think we need them to be global variables,
    # and in order to do that I believe that they have to be declared outside of
    # a class, but I'm really not sure. Or we can pass the simulator itself as
    # and argument to pretty much everything else and use it as a context.

    def __init__(self, filename):
        self.filename = filename

    def run(self):
        # for now, just make two hosts and a link to connect them, and then
        # try to send a packet

        host0 = Host("H0", "L01")
        globals.idmapping["H0"] = host0

        host1 = Host("H1", "L01")
        globals.idmapping["H1"] = host1

        link01 = Link("L01", "H0", "H1", 100, 5, 1000, 9)
        globals.idmapping["L01"] = link01

        # make a packet
        packet0 = Packet("H0", "0", "H1", 0, 1, False, data = '143 rox!')

        host0.send_packet(packet0)
        link01.send_packet()

        globals.systime = 7
        link01.send_packet()

        for i in range(100000):
            link01.send_packet()
            globals.systime += globals.dt

    def plot_metrics(self):
        #TODO
        pass
