# This is the main script that runs the simulator class and holds all
# the variables.
import sys 
import globals 
import time
# Supressing warnings about time clock being deprecated for higher versions of Python3
import warnings
warnings.filterwarnings("ignore")
from simulator import Simulator

now = time.clock()
# Initialize all the global variables
globals.initialize()

# Create the simulator with the given filename
if (len(sys.argv) < 3):
    sys.exit("Please include the input file and run time as arguments.\n example: \
        python3 main.py test_case1.json 20")
try:
   val = int(sys.argv[2])
except ValueError:
   sys.exit("Please enter an integer value in seconds for the runtime")

if (val > 100):
    sys.exit("This runtime seems too large. \n Please enter an integer value in seconds for the runtime.")

sim = Simulator(sys.argv[1])
print("Starting simulation for", sys.argv[1], ", running for", sys.argv[2], "seconds.")
sim.run(val*10000)
print("The simulation finished.")
sim.plot_metrics2()
end = time.clock()
elapsed = end - now
print("TIME ELAPSED: ")
print(elapsed)
