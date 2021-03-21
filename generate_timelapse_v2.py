#download files needed based on selected time
#rename files based ont creation date
#generate timelapse using ffmpeg

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import requests
import datetime
import argparse
import sys
import json
import urllib3
from pprint import pprint as pp
import io
import ffmpeg


def build_credentials(creds, scopes):
    credentials = service_account.Credentials.from_service_account_file(creds, scopes=scopes)
    service = build('drive', 'v3', credentials=credentials)

    if service:
        return service

    else:
        return None

def filter_date(service, selectedTime, parent):
    if service:
        page_token = None
        files = []
        while True:
            response = service.files().list(q="modifiedTime > \'{}\' and \'{}\' in parents".format(selectedTime, parent),
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name, modifiedTime, size)',
                                                pageToken=page_token).execute()
            
            files.extend(response.get('files'))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                return files

def get_files(files, service, camera_name, folder):
    i = 1
    total_files = len(files)
    #need enough decimal places for all files
    digit_length = len(str(total_files))
    for file in files:
        #check for 0 byte files or all black ones :)
        if int(file['size']) > 50:
            digits_needed = digit_length - len(str(i))
            number = "{}{}".format(digits_needed*"0", i)
            file_name = "{}-{}.jpg".format(camera_name, number)
            request = service.files().get_media(fileId=file['id'])
            fh = io.FileIO(folder + file_name, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            i+=1
            while done is False:
                status, done = downloader.next_chunk()
                print("Downloading: {}, size: {}".format(file_name, file['size']))
        else:
            #0 byte file so lets delete it
            request = service.files().delete(fileId=file['id'])

def generate_video(folder, camera_name, output_path=None):
    directory_length = len(os.listdir(folder))
    if directory_length > 0:
        file_format = "%0{}d.jpg".format(len(str(directory_length)))
        file_template = "{}{}-{}".format(folder, camera_name, file_format)
        if output_path:
            output_file = "{}/{}.mp4".format(output_path, camera_name)
        else:
            output_file = "{}.mp4".format(camera_name)
        
        #check if output exists
        if os.path.exists(output_file):
            #delete file
            print("Removing existing files...")
            os.remove(output_file)

        video = ffmpeg.input(file_template)
        output = ffmpeg.output(video, "{}".format(output_file), framerate=24)
        result = ffmpeg.run(output)
        
        return result
    
    else:
        print("Directory is empty... exiting")
        return False

def main():
    service = build_credentials(SERVICE_ACCOUNT_FILE, SCOPES)

    #get list of files after date/time
    files = filter_date(service, test_time, test_parent)

    sorted_files = (sorted(files,key=lambda file: file['modifiedTime']))

    get_files(sorted_files, service, test_camera, test_folder)
   
    output = generate_video(test_folder, test_camera)


if __name__ == '__main__':
    main()   