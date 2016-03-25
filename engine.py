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

def secToDay(seconds):
	return seconds/60/60/24

def sweep(rootdir):
	#dirname is the name of the directory
	#subdirlist is a list of all of the folders under the current directory
	#filelist is a list of all files in the current directory
	for dirname, subdirlist, filelist in os.walk(rootdir):
		for fname in filelist:
			fullname = dirname + "/" + fname
			#Check to make sure file is not empty (in range)
			if os.path.getsize(fullname) > 0:
				#Check if file is already a shortcut (and therefore saved already
				if not fname.endswith('.lnk') and not fname.endswith('.url'):
					#Check if file has been used in the last 30 days
					print fullname
					#if secToDay(time.time() - os.path.getmtime(fullname)) > 30:
					ingest(fullname)

def ingest(filename):
	result = commitCloudFile(filename)
	if result is not None:
		os.remove(filename)
		createShortcut(filename)

#untested
def getFileIcon(filename):
	found = False
	workdir = os.path.join(os.getcwd(),"exts")
	new_filename, file_extension = os.path.splitext(filename)
	sample_file = "example" + file_extension
	for dirname, subdirlist, filelist in os.walk(workdir):
		for fname in filelist:
			if sample_file == fname:
				found = True
	if found:
		return workdir + sample_file
	else:
		r = open(sample_file, 'w+')
		r.close()

def createShortcut(filename):
	#Strip extension off
	new_filename, file_extension = os.path.splitext(filename)

	shell = win32com.client.Dispatch("WScript.Shell")
	shortcut = shell.CreateShortCut(new_filename + ".lnk")
	#Get current directory assuming that the spawn script is in the same directory
	shortcut.Targetpath = os.path.join(os.getcwd(), "horizon-spawn.py")
	shortcut.Arguments = filename
	shortcut.IconLocation = filename
	shortcut.save()

def getDefaultDirectory():
	drive = os.getenv('SystemDrive')
	user = os.getenv('username')
	if drive is not None and user is not None:
		return drive + "/Users/" + user
	else:
		print "Critical drive or user error (missing environment variable)"

def main():
	test = "C:\Users\Arpad\photondocs"
	sweep(test)

if __name__ == "__main__":
	main()
