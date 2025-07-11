import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "gateway_stats_in",
        "cloud_mqtt_send_immediate"
    ]
}
configuration_tester.run_test_configuration(system_config)

