import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "libcamera_in",
        "s3_upload"
    ]
}
configuration_tester.run_test_configuration(system_config)