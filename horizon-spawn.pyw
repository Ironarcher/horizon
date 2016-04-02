#Script spawns from a shortcut and takes an argument to restore a cloud file
import os
import sys
import time
from googleapiclient import discovery
from googleapiclient import http
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials

#User identification (temporary)
uid = "akovesdy17"
fname = sys.argv[1]

#Login to cloud service
def create_service():
	credentials = GoogleCredentials.get_application_default()
	return discovery.build('storage', 'v1', credentials=credentials)

#Usage: downloadCloudFile("C:/Code/fetch_earth.py")
def downloadCloudFile(filename):
	out_file = open(filename, "w+")
	bucket = "horizon_data_bucket"
	filename = uid + "/" + filename
	service = create_service()

	# Use get_media instead of get to get the actual contents of the object.
	try:
		req = service.objects().get_media(bucket=bucket, object=filename)

		downloader = http.MediaIoBaseDownload(out_file, req)
		
		done = False
		while done is False:
			status, done = downloader.next_chunk()

		return out_file
	except HttpError, details:
		print "HttpError thrown during a download: " + str(details)
		return None

#Usage: pprint.pprint(deleteCloudFile("C:/Code/fetch_earth.py"))
def deleteCloudFile(filename):
	bucket = "horizon_data_bucket"
	filename = uid + "/" + filename
	service = create_service()

	req = service.objects().delete(bucket=bucket, object=filename)
	try:
		resp = req.execute()
		#If successful, returns ''
		#If not, throws exception otherwise
		return resp
	except HttpError, details:
		print "HttpError thrown during a delete: " + str(details)
		return None

#Filename is the place the file was originally created
#Source is the place the shortcut is when the script is run
def main(filename):
	result = downloadCloudFile(filename)
	if result is not None:
		new_filename, file_extension = os.path.splitext(filename)
		os.remove(new_filename + ".lnk")
		deleteCloudFile(filename)
		os.startfile(filename)

main(fname)