import configuration_tester
system_config = {
    "id": "test_device",
    "addresses": [
        "weather_rack_433_in",
        "bmp280_in",
        "renogy_ble_in",
        "kkm_ble_in",
        "gateway_stats_in",
        "datagator_inbound_sensor",
        "libcamera_in",
        "mongo_local_immediate",
        "cloud_mqtt_receive", 
        "cloud_mqtt_send",
        "s3_upload"
    ],
    "tasks": [
        "check_connection",
        "handle_connection_change",
        "handle_request_for_recovery_data",
        "clean_camera",
        "clean_database",
        "download_new_firmware",
    ]
}
configuration_tester.run_test_configuration(system_config)