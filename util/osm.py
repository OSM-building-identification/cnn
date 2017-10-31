import urllib2
import json
import sys
import pyproj #must install
import base64
import time
import math
import zipfile
from StringIO import StringIO
from cred import *

wgs84 = pyproj.Proj(init='epsg:4326')
webMerc = pyproj.Proj(init='epsg:3857')
def transform(x,y):
	return pyproj.transform(wgs84, webMerc, x, y)

auth = 'Basic ' + base64.b64encode(CRED['trimble_marketplace']['email']+':'+CRED['trimble_marketplace']['pass'])

def fetchBuildings(topLeft,bottomRight):
	topLeft = transform(topLeft[0], topLeft[1])
	bottomRight = transform(bottomRight[0], bottomRight[1])

	#create job
	job = {
		'job' : {
			'parameters' : {
				'job_north' : topLeft[1],
				'job_south' : bottomRight[1],
				'job_east' : bottomRight[0],
				'job_west' : topLeft[0],
				'job_datum_projection' : 'Native',
				'job_file_format' : 'GEOJSON',
				'job_layers' : 'Building'
			},
			'dataset_token' : 'e0dd1ef6-df94-4e7f-a95f-f48327ba3467',
			'layers' : ['Building'],
			'content_license_acceptance' : True
		}
	}

	jobRequest = urllib2.Request("https://market.trimbledata.com/jobs.json", json.dumps(job))
	jobRequest.add_header('Content-Type', 'application/json')
	jobRequest.add_header('Authorization', auth)
	res = urllib2.urlopen(jobRequest)
	jobData = json.loads(res.read())
	jobToken = jobData['job']['token']

	print 'created job %s' % jobToken

	#order job
	order = {
		'order' : {
			'payment_method_id' : None
		}
	}

	orderRequest = urllib2.Request('https://market.trimbledata.com/jobs/%s/process_job.json' % jobToken, json.dumps(order))
	orderRequest.add_header('Content-Type', 'application/json')
	orderRequest.add_header('Authorization', auth)
	orderRequest.get_method = lambda: 'PUT'
	res = urllib2.urlopen(orderRequest)
	orderData = json.loads(res.read())
	print 'ordered job'

	# wait for job to process
	ready = False
	checkData = None
	i=2
	while ready == False:
		checkRequest = urllib2.Request('https://market.trimbledata.com/jobs/%s.json' % jobToken)
		checkRequest.add_header('Authorization', auth)
		res = urllib2.urlopen(checkRequest)
		checkData = json.loads(res.read())
		status = checkData['job']['status']
		if status == 'Ready for Download':
			ready = True
		else: 
			delay = 5*math.log(i-1)
			print 'status: %s. waiting...' % status
			i = i+1
			time.sleep(delay)

	print 'job ready'

	# fetch dl link
	downloadApiUrl = checkData['job']['download_api_url']
	dlUrlRequest = urllib2.Request(downloadApiUrl)
	dlUrlRequest.add_header('Authorization', auth)
	res = urllib2.urlopen(dlUrlRequest)
	dlUrlData = json.loads(res.read())
	downloadUrl = dlUrlData[0]['url']

	#download it
	resp = urllib2.urlopen(downloadUrl)
	
	archive = zipfile.ZipFile(StringIO(resp.read()), 'r')
	names = archive.namelist()
	geojson = archive.open(names[0]+'data/building_polygon.json')

	return json.loads(geojson.read())
