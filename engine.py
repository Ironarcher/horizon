import os
import sys
import time
import win32com.client
import subprocess
from _winreg import *
from googleapiclient import discovery
from googleapiclient import http
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials

#Make sure that the registry allows folders to report the date they were recently accessed
def check_reg_file_access_date():
	key = OpenKey(HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\FileSystem', 0, KEY_READ)
	if QueryValueEx(key, "NtfsDisableLastAccessUpdate")[0] is not 0:
		#Edit key to zero value or report error (program will not function)
		#TO-DO
		print("Please enable recent file access date data collection")
	CloseKey(key)

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

def user_file_sweep(rootdir):
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
					#if secToDay(time.time() - os.stat.st_atime) > 30:
					ingest(fullname)

#Get all program directories in each program folder
def program_file_search():
	program_dir_1 = getProgramDirectory()
	program_dir_2 = getProgramDirectoryx86()
	programlist = []
	for programdir in os.listdir(program_dir_1):
		programlist.append(os.path.join(program_dir_1, programdir))
	for programdir2 in os.listdir(program_dir_2):
		programlist.append(os.path.join(program_dir_2, programdir2))
	return programlist

#Ingest all programs that are not used
#Accept list of all directories to ingest
def program_file_sweep():
	programlist = program_file_search()
	for programdir in programlist:
		if secToDay(time.time() - os.stat(programdir).st_atime) > 180:
			for dirname, subdirlist, filelist in os.walk(programdir):
				for fname in filelist:
					fullname = dirname + "/" + fname
					if os.path.getsize(fullname) > 0:
						if not fname.endswith('.lnk') and not fname.endswith('.url'):
							print fullname
							#ingest(fullname)

def ingest(filename):
	result = commitCloudFile(filename)
	if result is not None:
		os.remove(filename)
		createShortcut(filename)

def getFileIcon(filename):
	new_filename, file_extension = os.path.splitext(filename)
	command1 = "assoc " + file_extension
	#Remove unncessesary components of output
	fileassoc = subprocess.check_output(command1, shell=True).split("=")[1]
	command2 = "ftype " + fileassoc
	tmp = subprocess.check_output(command2, shell=True)
	#Remove all arguments from the output and remove quotes
	tmp_cut = tmp.find(".exe")+4
	return tmp[:tmp_cut].split("=", 1)[1].replace('"', "")

def createShortcut(filename):
	#Strip extension off
	new_filename, file_extension = os.path.splitext(filename)

	shell = win32com.client.Dispatch("WScript.Shell")
	shortcut = shell.CreateShortCut(new_filename + ".lnk")
	#Get current directory assuming that the spawn script is in the same directory
	shortcut.Targetpath = os.path.join(os.getcwd(), "horizon-spawn.pyw")
	shortcut.Arguments = filename 
	shortcut.IconLocation = getFileIcon(filename)
	shortcut.save()

def getDefaultDirectory():
	drive = os.getenv('SystemDrive')
	user = os.getenv('username')
	if drive is not None and user is not None:
		return drive + "/Users/" + user
	else:
		print "Critical drive or user error (missing environment variable)"

def getProgramDirectory():
	drive = os.getenv('SystemDrive')
	if drive is not None:
		returndir = os.path.join(drive, "/Program Files/")
		if os.path.isdir(returndir):
			return returndir
		else:
			print "Critical program files folder missing"
	else:
		print "Critical drive or user error (missing environment variable)"

def getProgramDirectoryx86():
	drive = os.getenv('SystemDrive')
	if drive is not None:
		returndir = os.path.join(drive, "/Program Files (x86)/")
		if os.path.isdir(returndir):
			return returndir
		else:
			print "Critical program files folder missing"
	else:
		print "Critical drive or user error (missing environment variable)"

def main():
	check_reg_file_access_date()
	program_file_sweep()

if __name__ == "__main__":
	main()
