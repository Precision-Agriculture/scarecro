import sys
import time 
sys.path.append("../scarecro")
import logging 
import system_object
#Get the system config
import src.system.system as system_class 
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')


system_config = {
    "id": "test_device",
    "addresses": [
        "libcamera_in"
        "s3_upload",
    ],
}

configuration_tester.run_test_configuration(system_config)