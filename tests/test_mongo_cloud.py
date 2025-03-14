
import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "datagator_mqtt_in",
        "datagator_ota_mqtt_in",
        "datagator_basic_sensors_in",
        "mongo_cloud_immediate",
        "gateway_stats_in",
        #"weather_rack_433_in"
    ]
}
configuration_tester.run_test_configuration(system_config)