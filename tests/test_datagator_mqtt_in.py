import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "datagator_mqtt_in",
        "datagator_ota_mqtt_in",
        "datagator_basic_sensors_in"
    ]
}
configuration_tester.run_test_configuration(system_config)