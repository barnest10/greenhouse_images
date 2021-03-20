import os

#get image list in dir
mypath = "C:\\ffmpeg\\camera_test\\greenhouse_cam_0"
onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
os.chdir(mypath)
for file in onlyfiles:
    short_file = file.replace("(", "").replace(")","").replace(" ", "-")
    if len(short_file.split("-")[2].split(".")[0]) == 2:
        newFile="cam-0-0{}.jpg".format(short_file.split("-")[2].split(".")[0])
    elif len(short_file.split("-")[2].split(".")[0]) == 1:
        newFile= "cam-0-00{}.jpg".format(short_file.split("-")[2].split(".")[0])
    else:
        newFile=short_file
    os.rename(file, newFile)