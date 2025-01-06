
import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "gateway_stats_in", 
        "cloud_mqtt_send_immediate" 
    ],
    "tasks": [
        "check_connection",
        "handle_connection_change", 
    ]
}
configuration_tester.run_test_configuration(system_config)


#Kill the wifi on this test 
#And see if it reboots after a few minutes 