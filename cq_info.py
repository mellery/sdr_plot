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
                apikey = node.text
    

def GetCallSignInfo(callsign):

    callsign_dict = {}

    my_lookuplib = LookupLib(lookuptype="qrz", username=apiusername, pwd=apipassword)
    cic = Callinfo(my_lookuplib)

#    print('making api request')
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
    return(callsign_dict[callsign])
    

####################################################
        
GetApiKey()

lat_list = []
lon_list = []
callsigns = []

desired_countries = []
desired_states = []

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "ALL_WSPR.TXT"

print("loading file")

lineList = [line.rstrip('\n') for line in open(filename)]

print("file loaded")

progress = 0

#for line in lineList:
with open(filename) as f:
    for line in itertools.islice(f,progress, None):

        if ("FT8" in line): 
            #latitude, longitude = locator_to_latlong(line.split()[7])
            
            if line.split()[7] == "CQ":
                callsign = line.split()[8]
                if callsign not in callsigns:
                    callsigns.append(callsign)
                    try:
                        contact_dict = GetCallSignInfo(callsign)
                        if contact_dict['country'] not in desired_countries:
                            desired_countries.append(contact_dict['country'])
                            print("new country seen", contact_dict['country'])
                    except:
                        print('invalid callsign - ',callsign)
   
