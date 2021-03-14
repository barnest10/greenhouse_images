Get images from IP camera and upload to Google Drive

positional arguments:
  data                  JSON File with camera details making it easy to add multiple cameras

Example) 
[ 
    { 
        "username": "user",
        "password": "password",
        "ip_address": "ip address",
        "name": "camera name",
        "still_url": "url for still image",
        "parents":[list of Google Drive parent ids],
        "local_directory: "local directory to  store image" 
    }
]

optional arguments:
  -h, --help            show this help message and exit
  --credentials CREDENTIALS, -c CREDENTIALS
                        Google Service Account JSON
  --delete, -D          delete local file after upload to Drive