
import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "datagator_mqtt_in",
        "datagator_ota_mqtt_in",
        "datagator_basic_sensors_in",
        "gateway_stats_in",
        "cloud_mqtt_send_immediate",
        #"printer_send_immediate"
    ]
}
configuration_tester.run_test_configuration(system_config)