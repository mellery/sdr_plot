from __future__ import unicode_literals

from pyhamtools.locator import locator_to_latlong

import matplotlib.pyplot as plt

import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs

from geopy.geocoders import Nominatim

from pyhamtools import LookupLib, Callinfo

import itertools
import requests
import sys

import xml.dom.minidom
from xml.etree import ElementTree
import lxml.etree as etree
import xmltodict, json

qrzlines = []
with open('qrz.txt') as f:
    qrzlines = f.read().splitlines()

progress = 0
with open('progress.txt') as f:
    progress = int(f.read().splitlines()[0])

print("resuming from line",progress)

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

    #if cic.is_valid_callsign(callsign):
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
    #else:
    #    return None

####################################################
        
GetApiKey()

lat_list = []
lon_list = []
callsigns = []

desired_countries = []
desired_states = []

with open('seen_countries.txt') as f:
    lines = f.read().splitlines()
    for line in lines:
        if line not in desired_countries:
            desired_countries.append(line)

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "ALL_WSPR.TXT"

print("loading file")

lineList = [line.rstrip('\n') for line in open(filename)]

print("file loaded")

#progress = 0

#for line in lineList:
with open(filename) as f:
    for line in itertools.islice(f,progress, None):
        progress = progress + 1
        #print(progress,"/",len(lineList))
        #print(line)
        with open("progress.txt", "w") as myfile:
            myfile.write(str(progress))

        if ("FT8" in line): 
            #latitude, longitude = locator_to_latlong(line.split()[7])
            callsign = line.split()[7]
            #if callsign == "CQ":
            #    callsign = line.split()[8]
#        else:
            #latitude, longitude = locator_to_latlong(line.split()[7])
#            callsign = line.split()[6]

#            if callsign == '<...>':
#                callsign = line.split()[7]

        if callsign not in callsigns:
            callsigns.append(callsign)
            try:
                contact_dict = GetCallSignInfo(callsign)
                if contact_dict['country'] not in desired_countries:
                    print("new country seen", contact_dict['country'])
                    with open("seen_countries.txt", "a") as myfile:
                        myfile.write(contact_dict['country']+'\n')
                    desired_countries.append(contact_dict['country'])
            
                lat_list.append(float(contact_dict['lat']))
                lon_list.append(float(contact_dict['lon']))
                with open("contacts_latlon.txt", "a") as myfile:
                    myfile.write(callsign+','+str(float(contact_dict['lat']))+','+str(float(contact_dict['lon']))+','+contact_dict['country']+'\n')
            except:
                print('invalid callsign - ',callsign)
                with open("invalid.txt", "a") as myfile:
                    myfile.write(line)
   
with open('contacts_latlon.txt') as f:
    lines = f.read().splitlines()
    for line in lines:
        lat_list.append(float(line.split(',')[1]))
        lon_list.append(float(line.split(',')[2]))
        country = line.split(',')[3]
        if country not in desired_countries:
            desired_countries.append(country)

plt.clf()
projection = ccrs.LambertConformal()

ax = plt.axes(projection=projection, aspect='auto')


ax.plot(lon_list, lat_list, 'b.', ms=1.0)
#ax.plot(-32.049523,115.891969, 'r.', ms=2.0)
#ax.plot(115.891969,-32.049523, 'r.', ms=2.0)
#ax.plot(99.771, -37.216, 'ro', ms=1.0)

#shapename = 'admin_1_states_provinces_lakes_shp'
shapename = 'admin_0_countries'
#shapename = 'admin_0_details'
reader = shpreader.Reader(shpreader.natural_earth(resolution='10m', category='cultural', name=shapename))

countries = reader.records()


ax.add_geometries(list(reader.geometries()), projection, facecolor=(0.7, 0.7, 0.7))

plot_countries = []

print("plotting countries")
desired_countries.append('United States of America')
desired_countries.append('Czechia')
desired_countries.append('Slovakia')
desired_countries.append('Republic of Serbia')
desired_countries.append('United Kingdom')
desired_countries.append('Puerto Rico')
desired_countries.append('United States Virgin Islands')
desired_countries.append('Saint Martin')
desired_countries.append('Guam')
desired_countries.append('Saint Helena')

#desired_countries.append('Curacao')
#desired_countries.append('Sao Tome and Principe')

for country in list(reader.records()):
    if country.attributes['GEOUNIT'] in str(desired_countries):
        plot_countries.append(country.geometry)

ax.add_geometries(plot_countries, projection, facecolor=(0.9, 0.9, 0.9))

plt.show()
