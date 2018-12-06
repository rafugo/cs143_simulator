# This is the main script that runs the simulator class and holds all
# the variables.
import globals # this will have to be called at the beginning of every file
import time
from simulator import Simulator

now = time.clock()
# initialize all the global variables
globals.initialize()

#without smoothing of buffer size: 422.254539 seconds
# create the simulator with the given filename
sim = Simulator('test_case1.json')
sim.run()
print("The simulation finished.")
sim.plot_metrics()
# sim.test_dijkstra()
end = time.clock()
elapsed = end - now
print("TIME ELAPSED: ")
print(elapsed)
