import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "renogy_ble_in",
        "weather_rack_433_in",
        "bmp280_in",
        "blynk_out",
        
    ]
}
configuration_tester.run_test_configuration(system_config)

