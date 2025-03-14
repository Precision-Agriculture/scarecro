
import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "gateway_stats_in",
        #"weather_rack_433_in",
        "mongo_local_immediate"
    ]
}
configuration_tester.run_test_configuration(system_config)
