import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "libcamera_in"
    ]
}
configuration_tester.run_test_configuration(system_config)