# This is the main script that runs the simulator class and holds all
# the variables.
import globals # this will have to be called at the beginning of every file
from simulator import Simulator

# initialize all the global variables
globals.initialize()

# create the simulator with the given filename
sim = Simulator('test_case0.json')
sim.run()
print("ran")
sim.plot_metrics()
