import time
import picamera
import picamera.array
import cv2
import numpy as np
import os
import xively
import subprocess
import datetime
import requests

#FEED_ID = "204250689"
#API_KEY = "amKjcvqAJhlwIJdlx8G6TZyFNbVXZCGuqC1F3SrQm1bQB53P"
FEED_ID = "1050101694"
API_KEY = "ivYyc7hfJN4cD0f3PKhNFPSl9lpaBtI1yIBgygwRppunIX8D"

maxobj=9
watt=20
maxarea=4
resolution = (1296,972)


def takepic(file):
  with picamera.PiCamera() as camera:
    camera.resolution = resolution
    camera.rotation = 180
    camera.capture(file)


def detect_light(oldlight):
  with picamera.PiCamera() as camera:
    #camera.start_preview()
    #time.sleep(2)
    camera.resolution = resolution
    camera.iso = 100
#    camera.shutter_speed = 7250
    camera.shutter_speed = 15000
    camera.rotation = 180
    with picamera.array.PiRGBArray(camera) as stream:
        camera.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        image = stream.array
	cv2.imwrite( "low.jpg", image )
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(image,np.array([180,180,180]),np.array([255,255,255]))

#	cv2.inRange(hsv,np.array([0,0,0.5]),np.array([360,0.2,1]),threshold)	
#	cv2.imwrite( "hsv.jpg", threshold )

        mask2 = mask
        cv2.imwrite( "mask.jpg", mask )
        contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#       print len(contours)

        light = 0
        
        if len(contours) > 0:
          areas = [cv2.contourArea(c) for c in contours]
          for c in range(0,len(contours)):
            if areas[c] > maxarea:
	      cnt=contours[c]
              #print areas[c]
              x,y,w,h = cv2.boundingRect(cnt)
              print x,y,w,h

	      cv2.putText(image,str(c), (x,y-20), cv2.FONT_ITALIC, 0.5,(0,255,0))
              cv2.rectangle(image,(x-10,y-10),(x+w+4,y+h+4),(0,255,0),1)
              cv2.rectangle(mask,(x-10,y-10),(x+w+4,y+h+4),(0,255,0),1)
	     # cv2.line(image,(x,y),(x+10,y+10),(0,255,0),1)
	      roi = image[y: y + h, x: x + w]
	      tt = "roi%s.jpg" % c
	      cv2.imwrite( tt, roi ) 
	   #  print x-10,y-10,x+w+4,y+h+4
# 	      cv2.rectangle(image,(x-5,y-5),(470,400),(0,255,0),-1)
	 #     if (w > (2*h)) or (h > (2*w)) : 
	      	#cv2.putText(image,"Fluorescent", (x,y-20), cv2.FONT_HERSHEY_DUPLEX, 1,(0,255,0))
	#	cv2.putText(image,"Fluorescent", (x,y-20), cv2.FONT_ITALIC, 0.5,(0,255,0))
	      light = light+1
	
        #if light > 6:
          #print areas

        if light != oldlight:
          filename = "%s_low_speed_shutter.jpg" % datetime.datetime.now()
          cv2.imwrite( filename, image )
          #cv2.imwrite( "hsv.jpg", hsv )
          cv2.imwrite( "mask2.jpg", mask2 )

        return light


def run():
  api = xively.XivelyAPIClient(API_KEY)
  feed = api.feeds.get(FEED_ID)
  oldlight = 0

  while True:
	
#    filename = "ori_%s_.jpg" % datetime.datetime.now()
    takepic("original.jpg")
    now = datetime.datetime.utcnow()
    light = detect_light(oldlight)
    oldlight = light
    print "%s,%d" % (datetime.datetime.now(),light)

    if light > maxobj:
	light = maxobj
    feed.datastreams = [xively.Datastream(id='Lamp', current_value=(light*watt), at=now)]

    try:
      feed.update()
    except:
      pass
    time.sleep(57)


run()

