import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "cloud_mqtt_receive_all"
    ],
    "tasks": [
        
    ]
}
configuration_tester.run_test_configuration(system_config)