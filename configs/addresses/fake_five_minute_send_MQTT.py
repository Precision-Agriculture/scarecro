address = {
    "inheritance":[],
    "handler": "$msg_type",
    "handler_function": "process",
    "send_or_receive": "send",
    "carrier": "fake_message_listener",
    "duration": 300,
    "additional_info": {
        "topic": "$msg_type",
        "connection": "HERE"
    } 
}
