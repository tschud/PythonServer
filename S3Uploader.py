import boto
import sys
import os
import time
from time import sleep
import json
import subprocess
from boto.s3.key import Key
from os.path import basename
from ImageAnalysis import check_percentage_equal_to


#prints progress of upload to console
def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

#removes file after upload finish with error handling
def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured

def IAuploader(testURL, parameters):
    return check_percentage_equal_to(testURL, parameters['start x'], parameters['start y'], parameters['size width'],
                                                   parameters['size height'], str(tuple(parameters['color'])), parameters['tolerance'],
                                                   parameters['percentage'])

def uploader(path, parameters):

    #Gather delete_image info and service_name info from json
    if 'delete_image' in parameters:
        deleteAfterUpload = parameters['delete_image']
    #If not specified, default for delete image is yes
    else:
        deleteAfterUpload = 'yes'
    if 'service_name' in parameters:
        service_name = parameters['service_name']
    #If no service name given, return to user to enter a service name
    else:
        return 'Please give a service_name'

    #Find filename at end of given path
    filename = os.path.basename(path)

    #Find desired key to upload image
    if service_name == 'upload_image':
        key_name = 'difftool/screenshots/test/uploads/' + filename
    elif service_name == 'markup':
        key_name = 'difftool/screenshots/test/markups/' + filename
    #If service name from json does not match a valid service, return to user
    else:
        return 'Please give a valid service name'


    #Read in keys from seperate file and connect to S3 bucket
    with open('KeyHandler.txt', 'r') as key_file:
        access_key = key_file.readline().replace('\n', '')
        secret_key = key_file.readline().replace('\n', '')
    bucket_name = 'a360ci'
    conn = boto.connect_s3(access_key,secret_key)
    bucket = conn.create_bucket(bucket_name,
                            location=boto.s3.connection.Location.DEFAULT)
    #Locate desired key in bucket and save file
    k = Key(bucket)
    k.key = key_name
    k.set_contents_from_filename(path, cb=percent_cb, num_cb=10)

    #If told to delete, the image will be deleted from where it is saved locally
    if deleteAfterUpload.lower() == 'yes':
        silentremove(path)

    #Create the URL link to the image in the bucket
    testURL = "http://a360ci.s3.amazonaws.com/" + key_name

    #Determine which service to run
    if service_name == 'upload_image':
        return testURL
    if service_name == 'markup':
        return IAuploader(testURL, parameters) + '|' + testURL



# Main method call
if __name__ == '__main__':
    uploader(path, parameters)
