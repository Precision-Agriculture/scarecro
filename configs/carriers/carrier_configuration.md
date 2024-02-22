## Carrier Configuration
Carriers are configured with carrier specific information that
will vary substantially by the particular carrier. 

Carriers are going to have to figure out how to perform the processing functions for a given thing? 
Or could give them an interface through state? 


All carrier object source code classes should have the following functions:

init() - the initialization function, which takes in the configuration of the carrier as well as all addresses that use the carrier, and message definitons that use the addresses 

And, depending on functionality, have one or more of these functions 

send() - a function that takes in a packaged message and an address, and sends the message to the address

receive() - a function that takes in the message(s) and an address(es), and is able to recieve the message and package it before placing into the message table 

