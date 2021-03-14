#!/usr/bin/env python

from google.oauth2 import service_account
from googleapiclient.discovery import build, MediaFileUpload
import os
import requests
import datetime
import argparse
import sys
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVICE_ACCOUNT_FILE = 'credentials.json'

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_image(data):
    url = "https://{}{}".format(data['ip_address'], data['still_url'])
    file = requests.get(url, auth=(data['username'], data['password']), verify=False )
    
    return file

def generate_file(camera, file):
    if not os.path.exists(camera['local_directory']):
        print("{} does not exist".format(camera['local_directory']))
        sys.exit()

    file_name = "{}_{}.jpg".format(camera['name'], datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    file_path = "{}/{}".format(camera['local_directory'], file_name)
    with open(file_path, 'wb') as f:
        f.write(file.content)
    
    return file_path, file_name

def drive_upload(args, file_path, file_name, camera):
    credentials = service_account.Credentials.from_service_account_file(args.credentials, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    if service:
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        results = service.files().create(media_body=media, body={"name": file_name, "parents": camera['parents']}).execute()
    if results:
        return results
    else:
        return False

def main():
    parser = argparse.ArgumentParser(description='Get images from IP camera and upload to Google Drive')
    parser.add_argument('data',
                        help='''JSON File with camera details making it easy to add multiple cameras
                        Example)
                        [
                            {
                                "username": "user",
                                "password": "password",
                                "ip_address": "ip address",
                                "name": "camera name",
                                "still_url": "url for still image",
                                "parents":[list of Google Drive parent ids],
                                "local_directory: "local directory to store image"
                            }
                        ]
                         ''')
    parser.add_argument('--credentials', '-c', help="Google Service Account JSON" )
    parser.add_argument('--delete','-D', action="store_true", help="delete local file after upload to Drive")
    
    args = parser.parse_args() 
    
    if args.data:
        with open(args.data) as f:
            data = json.load(f)
            #get pic from camera
        for camera in data:
            print("Getting Pic from Camera {}".format(camera['name']))
            file = get_image(camera)

            #process file
            if file:
                print("Generating File")
                file_path, file_name = generate_file(camera, file)

                if args.credentials and file_name:
                    print("uploading to Drive")
                    results = drive_upload(args, file_path, file_name, camera)

                    if results:
                        print("{} uploaded to Drive Successfully".format(file_name))

                        if args.delete:
                            if os.path.exists(file_path):
                                delete_result = os.remove(file_path)
                                print("{} File Deleted".format(file_name))
                            else:
                                print("The file does not exist")
                    
                    else:
                        print("Failed uploading file to Drive")
                
                else:
                    print("{} generated locally, No credentials provided for Drive Upload".format(file_name))
                    
            else:
                print("Error getting image from camera")
    
    #confirm files on drive
    #remove files from local

if __name__ == '__main__':
    main()   