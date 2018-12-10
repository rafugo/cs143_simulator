# This is the main script that runs the simulator class and holds all
# the variables.
import sys 
import globals 
import time
# supressing warnings about time clock being deprecated for high versions of Python
import warnings
warnings.filterwarnings("ignore")
from simulator import Simulator

now = time.clock()
# initialize all the global variables
globals.initialize()

#without smoothing of buffer size: 422.254539 seconds
# create the simulator with the given filename
if (len(sys.argv) < 2):
    sys.exit("Please include the input file as an argument.\n example: \
        python3 main.py test_case1.json")
try:
    sim = Simulator(sys.argv[1])
except:
    sys.exit("Please check the format of your input file.")
sim.run()
print("The simulation finished.")
sim.plot_metrics()
# sim.test_dijkstra()
end = time.clock()
elapsed = end - now
print("TIME ELAPSED: ")
print(elapsed)
