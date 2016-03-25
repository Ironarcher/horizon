import os
import sys
import pprint
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

def main():
	pass

if __name__ == "__main__":
	main()
