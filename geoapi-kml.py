#!/usr/bin/env python
# encoding: utf-8

# -*- coding: ISO-8859-1 -*-

import sys, os, json, urllib, re

#usage: python get_tweets.py [lat] [lng]

lat = sys.argv[1]
lng = sys.argv[2]

# Regex to find properly formatted lat-long pairs in the where response.

lat_lng_re = re.compile('^([\D]*[^-^\d])*(?P<lat>[\d\.-]+)\s*\,\s*(?P<lng>[\d\.-]+).*')
tweet_re = re.compile('@([^\s^\.]+)')

api = '[YOUR API KEY HERE]'

parent_request = 'http://api.geoapi.com/v1/parents?lat=%s&lon=%s&apikey=%s' % (lat,lng,api)
response = urllib.urlopen(parent_request).read()

json1 = json.loads(response)

# Find your neighborhood 

guid = json1['result']['parents'][0]['guid']

# Get Tweets in your neighborhood

tweets_request = 'http://api.geoapi.com/v1/e/%s/view/twitter?apikey=%s' % (guid,api)

response = urllib.urlopen(tweets_request).read()

json2 = json.loads(response)

print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
print "<kml xmlns=\"http://earth.google.com/kml/2.2\">"
print "<Document>"
print "\t<name>Twitters in %s</name>" % json1['result']['parents'][0]['meta']['name']
print "\t<description><![CDATA[Built by BlinkTag, Inc.  Data courtesty of geoapi.com]]></description>"
print "\t<Style id=\"bluedot\">"
print "\t\t<IconStyle>"
print "\t\t\t<Icon>"
print "\t\t\t\t<href>http://maps.gstatic.com/intl/en_us/mapfiles/ms/micons/blue-dot.png</href>"
print "\t\t\t</Icon>"
print "\t\t</IconStyle>"
print "\t</Style>"
print "\t<Style id=\"nhoodpoly\">"
print "\t\t<LineStyle>"
print "\t\t\t<color>40000000</color>"
print "\t\t\t<width>3</width>"
print "\t\t</LineStyle>"
print "\t\t<PolyStyle>"
print "\t\t\t<color>730000FF</color>"
print "\t\t\t<fill>1</fill>"
print "\t\t\t<outline>1</outline>"
print "\t\t</PolyStyle>"
print "\t</Style>"
print "\t<Placemark>"
print "\t\t<name>%s</name>" % json1['result']['parents'][0]['meta']['name']
print "\t\t<description><![CDATA[%s Boundary]]></description>" % json1['result']['parents'][0]['meta']['name']
print "\t\t<styleUrl>#nhoodpoly</styleUrl>"
print "\t\t<Polygon>"
print "\t\t\t<outerBoundaryIs>"
print "\t\t\t\t<LinearRing>"
print "\t\t\t\t\t<tessellate>1</tessellate>"
print "\t\t\t\t\t<coordinates>"
for i in json1['result']['parents'][0]['meta']['geom']['coordinates'][0]:
	print "\t\t\t\t\t\t%s,%s" % (i[0],i[1])
print "\t\t\t\t\t</coordinates>"
print "\t\t\t\t</LinearRing>"
print "\t\t\t</outerBoundaryIs>"
print "\t\t</Polygon>"
print "\t</Placemark>"
for tweet in json2['result']:
	loc = lat_lng_re.match(tweet['location'])
	if loc:
		lat = loc.group('lat')
		lng = loc.group('lng')
		usr = tweet['from_user']
		img = tweet['profile_image_url']
		twt = tweet_re.sub(r' <a href="http://twitter.com/\1">@\1</a>',tweet['text'])
		try:
			print "\t<Placemark>\n\t\t<name>Tweet</name>\n\t\t<description><![CDATA[<a href=\"http://twitter.com/%s\"><img src=\"%s\"></a>%s]]></description>" % (usr,img,twt)
			print "\t\t<styleUrl>#bluedot</styleUrl>"
			print "\t\t<Point>"
			print "\t\t\t<coordinates>%s,%s</coordinates>" % (lng,lat)
			print "\t\t</Point>"
			print "\t</Placemark>"
		except UnicodeEncodeError:
			pass
	else:
		usr = tweet['from_user']
		img = tweet['profile_image_url']
		twt = tweet_re.sub(r' <a href="http://twitter.com/\1">@\1</a>',tweet['text'])
		location = tweet['location']
		g_code_url = "http://google.com/maps/geo?q=%s&output=json" % location.replace(' ','+')
		try:
			g_code_json = json.loads(urllib.urlopen(g_code_url).read())
			if g_code_json['Status']['code'] == 200 and g_code_json['Placemark'][0]['AddressDetails']['Accuracy'] > 6:
				print "\t<Placemark>\n\t\t<name>Tweet (google geocoded)</name>\n\t\t<description><![CDATA[<a href=\"http://twitter.com/%s\"><img src=\"%s\"></a>%s]]></description>" % (usr,img,twt)
				print "\t\t<styleUrl>#bluedot</styleUrl>"
				print "\t\t<Point>"
				lng = g_code_json["Placemark"][0]["Point"]['coordinates'][0]
				lat = g_code_json["Placemark"][0]["Point"]['coordinates'][1]
				print "\t\t\t<coordinates>%s,%s</coordinates>" % (lng,lat)
				print "\t\t</Point>"
				print "\t</Placemark>"
		except UnicodeError:
			pass			
print "</Document>"
print "</kml>"