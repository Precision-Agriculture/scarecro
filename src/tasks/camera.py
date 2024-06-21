import time 
import os 
import logging 

class Camera:
    """
    This is the task super class. 
    Tasks may import most other modules (as well as other tasks)
    to run period system functionality. Sub classes may
    add functionality.
    """
    def __init__(self, config={}):
        """
        Initializes the task with configuration provided 
        """
        self.config = config.copy()
        self.duration = self.config.get("duration", )
        print("Initializing a Camera Class") 
        #Config needs a folder where pictures should be stored
        #And a possible S3 upload, maybe? 
        #Not sure what else --- ??? 
        #Maybe a resolution? Maybe not? 

    def take_picture(self):
        pass 
      

        

def return_object(config):
    return Camera(config)


def init(init_info):
    return {}

def test(init_info, process_info):
    try:
        base_path ="/home/pi/scarecro/pi_camera_images/"
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        capture_string = base_path + "skycamera.jpg"
        command = "libcamera-still -t 5000 –autofocus –width 4626 –height 3472 -o "+capture_string
        os.system(command)
        return True
    except Exception as e:
        logging.error("Could not test SkyCamPi", exc_info=True)
        return False

#PiHawk 


# def process(message, process_info):
#     logging.info("Taking Pi Hawk Eye picture")
#     try:
#         time.sleep(2)

#         #Help from here: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists-2/
#         base_path ="/home/pi/scarecro/pi_camera_images/"
#         if not os.path.exists(base_path):
#             os.makedirs(base_path)

#         cameraID = "SkyCamPi" #Probably want to change to unique Id - likely gateway ID. 
        
#         # put together the file name
#         fileDate = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#         fileDay = datetime.datetime.now().strftime("%Y-%m-%d")

#         singlefilename =cameraID+"_1_"+fileDate+".jpg"
#         dirpathname=base_path + cameraID+ "/"+fileDay

#         os.makedirs(dirpathname, exist_ok=True)
#         os.makedirs(base_path, exist_ok=True)
#         filename = dirpathname+"/"+singlefilename

#         command = "libcamera-still -t 5000 –autofocus –width 4626 –height 3472 -o "+filename
#         os.system(command)
 
#     except Exception as e:
#             logging.error("Could not take Pi Hawk Eye Picture", exc_info=True)
#     return {}


#Picamera 

# def init(init_info):
#     return {}

# def test(init_info, process_info):
#     try:
#         camera = picamera.PiCamera()
#         base_path ="/home/pi/scarecro/pi_camera_images/"
#         if not os.path.exists(base_path):
#             os.makedirs(base_path)
#         capture_string = base_path + "skycamera.jpg"
#         camera.capture(capture_string)
#         camera.close()
#         return True
#     except Exception as e:
#         logging.error("Could not test picamera", exc_info=True)
#         return False

# def process(message, process_info):
#     logging.info("Taking picamera picture")
#     camera = picamera.PiCamera()
#     camera.exposure_mode = "auto"
#     try:
#         #MARKED - need to replace this!
#         #camera.rotation = config.Camera_Rotation
#         camera.resolution = (1920, 1080)
#         # Camera warm-up time
#         time.sleep(2)

#         #Help from here: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists-2/
#         base_path ="/home/pi/scarecro/pi_camera_images/"
#         if not os.path.exists(base_path):
#             os.makedirs(base_path)

#         capture_string = base_path + "skycamera.jpg"
#         camera.capture(capture_string)

#         # now add timestamp to jpeg
#         pil_im = Image.open(capture_string)
      
#         # Save the image - change these 
#         #pil_im.save('dash_app/assets/skycamera.jpg', format= 'JPEG')
#         #pil_im.save('pi_camera_images/skycamera.jpg', format= 'JPEG')
#         #pil_im.save('pi_camera_images/skycameraprocessed.jpg', format= 'JPEG')

#         cameraID = "SkyCamPi" #Probably want to change to unique Id - likely gateway ID. 
#         currentpicturefilename = base_path+cameraID+".jpg"
        
#         # put together the file name
#         fileDate = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#         fileDay = datetime.datetime.now().strftime("%Y-%m-%d")

#         singlefilename =cameraID+"_1_"+fileDate+".jpg"
#         dirpathname=base_path + cameraID+ "/"+fileDay

#         os.makedirs(dirpathname, exist_ok=True)
#         os.makedirs(base_path, exist_ok=True)
#         filename = dirpathname+"/"+singlefilename


#         pil_im.save(filename, format= 'JPEG')
#         #FileSize =os.path.getsize(currentpicturefilename)
#         #If we ever want to export this data later. 
#         new_dict = {}
#         new_dict["cameraID"] = cameraID
#         new_dict["picturename"] = singlefilename
#         #new_dict["picturesize"] = FileSize
#         new_dict["messageID"] = 1
#         new_dict["resends"] = 0
#         new_dict["resolution"] = 0
 
#     except Exception as e:
#             logging.error("Could not take SkyCam Picture", exc_info=True)
#     finally:
#         try:
#             camera.close()
#         except Exception as e:
#             logging.error("SkyCam Close Failed", exc_info=True)
#     return {}

