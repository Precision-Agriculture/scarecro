# Handlers Configurations
Handlers handle incoming and outgoing messages, including performing additional processing as necessary. 

Handler configurations should point to the handler source code they reference ,
"source" -- 


Handlers should have:

An init function, which takes in relevant:
config dict
send address dict
receive address dict
message config dict 

one or more processing functions, which take in message type and a list of messages
and return a list of messages 


Handlers (self.handlers)

"addresses":

"content": 

"object": 