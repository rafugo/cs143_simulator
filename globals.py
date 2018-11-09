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
def initialize():
    # the time for the whole system
    global systime
    systime = 0

    # the time increment settings
    global dt
    dt = 1
