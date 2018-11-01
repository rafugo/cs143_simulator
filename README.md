# cs143_simulator


Link:
-	ID
-	Rate
-	Delay
-	Buffer
-	Conn1
-	Conn2
-	Static cost
TODO:
-	Has to be able to transfer packets 
-	Reno and fast models.

Host:
-	IP
-	1 link ID 
TODO:
-	Send packets
-	Receive packets
-	Send acknowledgements 
-	Receive acknoweledgements

Router:
-	IP
-	Routing Table
TODO:
-	Know where other routers are
-	Update routing table

Packet:
-	Size
-	Where from 
-	Where to
-	How many total |sequence|
-	number in sequence 
-	acknowledgement flag

Flow:
-	ALG being used
-	ID
-	Source
-	Destination
-	Data amount
-	Flow start time

Track:
-	link rate
-	buffer occupancy
-	packet loss
-	flow rate
-	window size
-	packet delay 
-	per host: send/receive
-	per flow: send/receive
-	packet roundtrip/delay
