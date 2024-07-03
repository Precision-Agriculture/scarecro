import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "weather_rack_433_in",
        "weather_rack_3_in",
        "wr3_power_in", 
        "aqi_in",
        "thunder_board_in",
        "aqi_in"
    ]
}
configuration_tester.run_test_configuration(system_config)