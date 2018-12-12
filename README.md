# CS/EE 143: Communication Networks Project
Rafael Fueyo-Gomez, Cortland Perry, Kelsi Riley, Sakthi Vetrivel

To run this simulator, first ensure that you have python3 and matplotlib installed. Then, clone the git repo, and enter the directory of the project. To run the simulator, run

```console
$ python3 main.py [INPUT_FILE] [RUNTIME_IN_SECONDS]
````

The project includes the input files for the provided test cases as well as a custom test case. These input files are specific to the congestion control algorithm you'd like to use. For example, to run the simulator for Test Case 2 using TCP Reno for 30 seconds, run:

```console
$ python3 main.py test_case2_reno.json 30
````
