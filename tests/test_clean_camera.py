import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "picamera_in"
    ],
    "tasks": [
        "clean_camera"
    ]
}
configuration_tester.run_test_configuration(system_config)