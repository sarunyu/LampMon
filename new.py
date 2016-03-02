import picamera
import picamera.array
import cv2
import numpy as np
import os
import xively
import time
import datetime
import json



FEED_ID = "1300366347"
API_KEY = "zwz5Ov5AFbOA3wTYPW4r9r8psbJPdFioAqAQciQm9HDX82gV"

lamp = 	[[473,482,87,9],
	[622,469,108,11],
	[805, 448, 121, 16],
	[310, 434, 103, 14],
	[491, 407, 157, 21],
	[767, 369, 196, 28],
	[10, 317, 76, 43],
	[156, 192, 212, 92],
	[608, 36, 487, 98]]

maxobj=9
watt=20
maxarea=4
resolution = (1296,972)


def detect():
  with picamera.PiCamera() as camera:
    camera.resolution = resolution
    camera.iso = 100
#    camera.shutter_speed = 15000
    camera.rotation = 180
    with picamera.array.PiRGBArray(camera) as stream:
	camera.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        image = stream.array
	return image
#    for c in lamp:
#      img = image[c[1]: c[1] + c[3], c[0]: c[0] + c[2]]
#      name = "new_%s.jpg" % c
#      cv2.imwrite( name, img )
  
	
def run():
  api = xively.XivelyAPIClient(API_KEY)
  feed = api.feeds.get(FEED_ID)
  image = detect()
  with open('roi.json') as data_file:    
    data = json.load(data_file)

  for item in data:
    print item,len(data[item])
    
    for list in data[item]:
      #print list['roi']
      roi = list['roi']
      #print roi[0]['x']
      #print roi[1]['y']
      #print roi[2]['w']
      #print roi[3]['h']
		
      img = image[roi[1]['y']:roi[1]['y']  + roi[3]['h'], roi[0]['x']: roi[0]['x'] + roi[2]['w']]
      name = "xx_%s.jpg" % list['name']
      cv2.imwrite( name, img )       
      #cvtColor( img, src_gray, CV_BGR2GRAY );
      #cv2.threshold( img, dst,128, 255,3 );	 
      ret,thresh1 = cv2.threshold(img,30,255,cv2.THRESH_BINARY)      
      name = "binary_%s.jpg" % list['name']
      now = datetime.datetime.utcnow()      
      power=0
      if np.count_nonzero(thresh1) > 500:
 	power = list['power']
      feed.datastreams = [xively.Datastream(id=list['name'], current_value=power, at=now)]
 
      cv2.imwrite( name, thresh1 )
      print np.count_nonzero(thresh1)
#      print np.count_nonzero(thresh1)
  try:
    feed.update()
  except:
    pass

  for id_, item in data.iteritems():
    print "------------------------"
#    print item[i]['roi']
    


run()
