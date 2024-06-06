## Carrier Configuration
Carriers are configured with carrier specific information that
will vary substantially by the particular carrier. 

Carriers are going to have to figure out how to perform the processing functions for a given thing? 
Or could give them an interface through state? 

source: python source code file name where the carrier will be implemented. 

All carrier object source code classes should have the following functions:

init() - the initialization function, which takes in the configuration of the carrier as well as all addresses that use the carrier, and message definitons that use the addresses 

And, depending on functionality, have one or more of these functions 

send() - a function that takes in a list of addresses, the duration, (and an optional list of entry ids), grabs the messages corresponding to those addresses (optionally filtered by entry id), and sends them. 

receive() - a function that takes in the address(es) names, duration, and is able to recieve the message(s) and package it before placing into the message table 


A specific carrier source code definition should include: 

* What durations, if any, a send/receive function is defined with 

* Which arguments are necessary and which are optional in the config. Optional defaults if necessary. Kinds of values the arguments can take 

* what form of message the carrier passes 
to the handler 


