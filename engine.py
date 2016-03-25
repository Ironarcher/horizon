import os
import sys
import time
import win32com.client
from googleapiclient import discovery
from googleapiclient import http
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials

#User identification (temporary)
uid = "akovesdy17"

#Login to cloud service
def create_service():
	credentials = GoogleCredentials.get_application_default()
	return discovery.build('storage', 'v1', credentials=credentials)

#Save file to the google cloud storage
#Usage: commitCloudFile("C:/Code/fetch_earth.py")
def commitCloudFile(filename):
	bucket = "horizon_data_bucket"
	service = create_service()
	body = {
		'name': uid + "/" + filename,
	}
	# Now insert them into the specified bucket as a media insertion.
	try:
		with open(filename, 'rb') as f:
			req = service.objects().insert(
				bucket=bucket, body=body,
				media_body=http.MediaIoBaseUpload(f, 'application/octet-stream'))
			resp = req.execute()
		return resp
	except HttpError, details:
		print "HttpError thrown during a commit: " + str(details)
		return "httperror"

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

def secToDay(seconds):
	return seconds/60/60/24

def sweep(rootdir):
	#dirname is the name of the directory
	#subdirlist is a list of all of the folders under the current directory
	#filelist is a list of all files in the current directory
	for dirname, subdirlist, filelist in os.walk(rootdir):
		for fname in filelist:
			fullname = dirname + "/" + fname
			#Check if file is already a shortcut (and therefore saved already
			if not fname.endswith('.lnk') and not fname.endswith('.url'):
				#Check if file has been used in the last 30 days
				if secToDay(time.time() - os.path.getmtime(fullname)) > 30:
					ingest(fullname)

def ingest(filename):
	result = downloadCloudFile(filename)
	if result is not None:
		os.remove(filename)
		createShortcut(filename)

def createShortcut(filename):
	#Strip extension off
	new_filename, file_extension = os.path.splitext(filename)

	shell = win32com.client.Dispatch("WScript.Shell")
	shortcut = shell.CreateShortCut(new_filename + ".lnk")
	#Get current directory assuming that the spawn script is in the same directory
	shortcut.Targetpath = os.path.join(os.getcwd(), "horizon-spawn.py") + " " + filename
	shortcut.save()

def retrieveFileIcon(filetype):
	pass

def main():
	commitCloudFile("C:/Code/fetch_earth.py")

if __name__ == "__main__":
	main()
