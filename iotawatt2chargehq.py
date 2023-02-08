#!/usr/bin/env python3
import sys, os
import locale
import json
import requests

__author__ = "Darek Margas"
__copyright__ = "Copyright 2023, Darek Margas"
__license__ = "MIT"

# IOTAWATT
ip="192.168.0.1"

# Names of inputs/outputs
IO_NET_IMPORT_KW = "Grid"
IO_PRODUCTION_KW = "Inverter"

# Charge HQ
chq_url = 'https://api.chargehq.net/api/public/push-solar-data'
api_key = "your key"

# Getting data
g = requests.get( "http://{}/query".format(ip), params = "select=[{}.watts,{}.watts]&begin=s-1m&end=s&group=all&header=no".format(IO_NET_IMPORT_KW, IO_PRODUCTION_KW), timeout=15)

#Assembling json
data = {}
data['apiKey'] = api_key
data['siteMeters'] = {}
data['siteMeters']['production_kw'] = round( g.json()[0][1] / 1000, 3)
data['siteMeters']['net_import_kw'] = round( g.json()[0][0] / 1000, 3)
data['siteMeters']['consumption_kw'] = round((g.json()[0][1] + g.json()[0][0])/1000,3)

# Posting to CHQ
payload = json.dumps(data)
header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

p = requests.post( chq_url, data=payload, headers=header)
#print(payload, p.text)
