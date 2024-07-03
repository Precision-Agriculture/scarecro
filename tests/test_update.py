import configuration_tester
system_config = {
    "id": "test_device",
    "tasks":[
        "update_system_task"
    ]
}
configuration_tester.run_test_configuration(system_config)