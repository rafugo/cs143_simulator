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
    dt = 1

    # the id : object mapping of the objects in the network
    global idmapping
    idmapping = {}