# This is the main script that runs the simulator class and holds all
# the variables.
import globals # this will have to be called at the beginning of every file
from simulator import Simulator

# initialize all the global variables
globals.initialize()

# I need the time to start at 0.
#globals.systime += 1

# create the simulator with the given filename
sim = Simulator('router_test.json')
sim.run()
print("ran")
sim.rt_init_test()
sim.plot_metrics()
