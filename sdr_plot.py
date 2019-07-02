from __future__ import unicode_literals

from pyhamtools.locator import locator_to_latlong

import matplotlib.pyplot as plt

import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs

from geopy.geocoders import Nominatim

from pyhamtools import LookupLib, Callinfo

import requests

import sys

import xml.dom.minidom
from xml.etree import ElementTree
import lxml.etree as etree
import xmltodict, json

qrzlines = []
with open('qrz.txt') as f:
    qrzlines = f.read().splitlines()

apiusername=qrzlines[0]
apipassword=qrzlines[1]

apikey = ''

def GetApiKey():
    global apikey
    
    url = 'http://xmldata.qrz.com/xml/current/?username='+apiusername+';password='+apipassword+';agent=q5.0'
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)

    for child in tree:
        for node in child:
            if 'Key' in node.tag:
                print(node.text)
                apikey = node.text
    

def GetCallSignInfo(callsign):

    callsign_dict = {}

    with open('contacts.json', 'r') as infile:
        try:
            callsign_dict = json.load(infile)
            if callsign in callsign_dict:
                return(callsign_dict[callsign])
        except ValueError:
            print('empty dict')
            callsign_dict = {}
                
        
    #check if callsign is in file
    #   use it
    #otherwise use website then write it to file

    my_lookuplib = LookupLib(lookuptype="qrz", username=apiusername, pwd=apipassword)
    cic = Callinfo(my_lookuplib)

    if cic.is_valid_callsign(callsign):
        print('making api request')
        url = 'http://xmldata.qrz.com/xml/current/?s='+apikey+';callsign='+callsign
        response = requests.get(url)
        link='{http://xmldata.qrz.com}'

        root = ElementTree.fromstring(response.content)

        contact_dict = {}
        for child in root:
            if(child.tag == link+'Callsign'):
                for item in child:
                    itemname = item.tag.replace(link,'')
                    contact_dict[itemname] = item.text

        callsign_dict[callsign] = contact_dict
    
        with open('contacts.json', 'w') as outfile:
            json.dump(callsign_dict,outfile)    

        return(callsign_dict[callsign])
    else:
        return None

####################################################
        
GetApiKey()
GetCallSignInfo('N2NOM')
GetCallSignInfo('KE8KW')

lat_list = []
lon_list = []
callsigns = []

desired_countries = []

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "ALL_WSPR.TXT"

lineList = [line.rstrip('\n') for line in open(filename)]

for line in lineList:
    #print(line)
    latitude, longitude = locator_to_latlong(line.split()[7])

    callsign = line.split()[6]

    if callsign == '<...>':
        callsign = line.split()[7]
        #latitude, longitude = locator_to_latlong(line.split()[8])

    if callsign not in callsigns:

        callsigns.append(callsign)
        try:
            contact_dict = GetCallSignInfo(callsign)
            if contact_dict['country'] == 'United States':
                print(contact_dict['call'],contact_dict['lat'],contact_dict['lon'],contact_dict['state'])    
            else:
                print(contact_dict['call'],contact_dict['lat'],contact_dict['lon'],contact_dict['country'])
                if contact_dict['country'] not in desired_countries:
                    desired_countries.append(contact_dict['country'])
                    #desired_countries.append('Norway')
            
            lat_list.append(float(contact_dict['lat']))
            lon_list.append(float(contact_dict['lon']))
        except:
            print('invalid callsign - ',callsign)
    
plt.clf()
projection = ccrs.LambertConformal()

ax = plt.axes(projection=projection, aspect='auto')


ax.plot(lon_list, lat_list, 'b.', ms=1.0)
#ax.plot(la1k_lon, la1k_lat, 'o')

#shapename = 'admin_1_states_provinces_lakes_shp'
shapename = 'admin_0_countries'
#shapename = 'admin_0_details'
reader = shpreader.Reader(shpreader.natural_earth(resolution='10m', category='cultural', name=shapename))

countries = reader.records()

#for country in countries:
#     attribute = 'ADM0_A3'
#     ADM0_A3 = country.attributes['ADM0_A3']


#for country in countries:
#    print(country.attributes.keys())
#    try:
#        print country.attributes['admin']
#    except:
#        print 'country name error'
#    if country.attributes['admin'] == 'USA':
#        ax.add_geometries(country.geometry, projection,
#                          facecolor=(0, 0, 1),
#                          label=country.attributes['admin'])
#    else:
#        ax.add_geometries(country.geometry, projection,
#                          facecolor=(0, 1, 0),
#                          label=country.attributes['admin'])


ax.add_geometries(list(reader.geometries()), projection, facecolor=(0.7, 0.7, 0.7))

plot_countries = []
plot_sw_countries = []

#shortwave contacts
shortwave_countries = []
shortwave_countries.append('Cuba')
shortwave_countries.append('Brazil')
shortwave_countries.append('Romania')
shortwave_countries.append('Albania')

for country in list(reader.records()):
#    print(country.attributes['GEOUNIT'])
    if country.attributes['GEOUNIT'] in str(shortwave_countries):
        plot_sw_countries.append(country.geometry)
ax.add_geometries(plot_sw_countries, projection, facecolor=(0.4, 0.9, 0.9))

print(str(desired_countries))

for country in list(reader.records()):
#    print(country.attributes['GEOUNIT'])
    if country.attributes['GEOUNIT'] in str(desired_countries):
        plot_countries.append(country.geometry)

print(plot_countries)

ax.add_geometries(plot_countries, projection, facecolor=(0.9, 0.9, 0.9))

plt.show()
