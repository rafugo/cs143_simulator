# This is the main script that runs the simulator class and holds all
# the variables.
import globals # this will have to be called at the beginning of every file
from simulator import Simulator

# initialize all the global variables
globals.initialize()
globals.systime += 1

# create the simulator with the given filename
sim = Simulator('input_file.json')
sim.run()
#sim.rt_init_test()
