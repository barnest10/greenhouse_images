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
import argparse


SCOPES = ['https://www.googleapis.com/auth/drive']
LOCAL_FOLDER = "temp/"

def build_credentials(creds, scopes):
    credentials = service_account.Credentials.from_service_account_file(creds, scopes=scopes)
    service = build('drive', 'v3', credentials=credentials)

    if service:
        return service

    else:
        return None

def filter_date(service, startTime, endTime, parent):
    if service:
        page_token = None
        files = []
        query_string = "modifiedTime >= \'{}\' and modifiedTime <= \'{}\' and name contains \'{}\' and mimeType != 'application/vnd.google-apps.folder'".format(startTime, endTime, parent)

        while True:
            response = service.files().list(q=query_string,
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name, modifiedTime, size)',
                                                pageToken=page_token).execute()
            
            files.extend(response.get('files'))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                return files

def get_files(files, service, camera_name, folder):
     #check if output exists
    if not os.path.exists(folder):
        #add folder
        print("Creating temp directory")
        os.makedirs(folder)
    i = 1
    total_files = len(files)
    #need enough decimal places for all files
    digit_length = len(str(total_files))
    for file in files:
        #check for 0 byte files or all black ones :)
        if int(file['size']) > 50000:
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
    parser = argparse.ArgumentParser(description='Generate timelapse video from images stored on google drive')
    parser.add_argument('parent_file_name', help='Parent folder in Google Drive Hierachy -- Camera NAME')
    parser.add_argument('--start_time', '-s', help="Start date in format %Y-%m-%dT%H:%M:%S.%fZ")
    parser.add_argument('--end_time', '-e', help="Start date in format %Y-%m-%dT%H:%M:%S.%fZ")
    parser.add_argument('--credentials', '-c', help="Google Service Account JSON" )
    
    args = parser.parse_args()
    if not args.credentials:
        print("Credential file required")
        quit()
    
    if not (args.start_time and args.end_time):
        print("Start and end times required")
        quit()
    
    service = build_credentials(args.credentials, SCOPES)

    #get list of files after date/time
    files = filter_date(service, args.start_time, args.end_time, args.parent_file_name)

    sorted_files = (sorted(files,key=lambda file: file['modifiedTime']))

    get_files(sorted_files, service, args.parent_file_name, LOCAL_FOLDER)
   
    output = generate_video(LOCAL_FOLDER, args.parent_file_name)


if __name__ == '__main__':
    main()   