
import xml.dom.minidom
from xml.etree import ElementTree
import lxml.etree as etree
import xmltodict, json

from pyhamtools import LookupLib, Callinfo
import requests

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

        
    #check if callsign is in file
    #   use it
    #otherwise use website then write it to file

    my_lookuplib = LookupLib(lookuptype="qrz", username=apiusername, pwd=apipassword)
    cic = Callinfo(my_lookuplib)

    #if cic.is_valid_callsign(callsign):
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
    
    #else:
    #    return None

GetApiKey()
print(GetCallSignInfo('FM4SA'))
print(GetCallSignInfo('VU2IT'))


