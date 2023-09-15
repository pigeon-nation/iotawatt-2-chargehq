# This code was written as a response to the issue stated by {info-remioved} this morning. Apparently you have been having some issues, and needed error handling for the requests. 
# This code was written by Pigeon Nation. (GH: pigeon-nation :: pigeon-nation.github.io).
# Copyright remains with Darek Margas.

import sys, os
import locale
import json
import requests
import argparse
import logging
import time

# A quick recreation of print(...), but with sys.stderr as the "file" parameter.
def show_error(text):
   logging.error(text)

__author__ = "Darek Margas"
__copyright__ = "Copyright 2023, Darek Margas"
__license__ = "MIT"

# Arguments
my_parser = argparse.ArgumentParser(description="Update ChargeHQ from IoTaWatt")
my_parser.add_argument( "--ip", metavar="IP address", type=str, help="IP Address of IoTaWatt", required=True )
my_parser.add_argument( "--grid", metavar="Net grid import", type=str, help="Net import from Grid (kW)", required=True )
my_parser.add_argument( "--production", metavar="PV production", type=str, help="PV production (kW)", required=True)
my_parser.add_argument( "--key", metavar="API key", type=str, help="ChargeHQ API key", required=True)

args = my_parser.parse_args()

# Charge HQ
chq_url = 'https://api.chargehq.net/api/public/push-solar-data'

# Getting data
try:
   g = requests.get( "http://{}/query".format(args.ip), params = "select=[{}.watts,{}.watts]&begin=s-1m&end=s&group=all&header=no".format(args.grid, args.production), timeout=15)
except requests.exceptions.Timeout: # todo: specific error handling
   show_error('Timeout.')
   sys.exit(1) # Exit, status code 1.
except requests.exceptions.HTTPError:
   show_error('HTTP Error.')
   sys.exit(1) # Exit, status code 1.
except requests.exceptions.ConnectionError:
   show_error('Connection Error - Could not connect. ')
   sys.exit(1) # Exit, status code 1.
except requests.exceptions.SSLError as expt:
   show_error('SSL Error.')
   show_error('More Details: ')
   # Show the origional error, but exit in a controlled manner.
   try:
      raise Exception('SSL Error Details.')
   except:
      raise expt
   finally:
      sys.exit(1) # Exit, status code 1.
except requests.exceptions.InvalidURL:
   show_error('Invalid URL.')
   show_error('Attempted URL: ' + "http://{}/query".format(args.ip))
   sys.exit(1)
except Exception as expt: # If all else fails.
   show_error('Unknown Error.')
   show_error('More Details: ')
   # Show the origional error, but exit in a controlled manner.
   try:
      raise Exception('Error Details.')
   except:
      raise expt
   finally:
      sys.exit(1) # Exit, status code 1.

# Assembling json
data = {}
data['apiKey'] = args.key
if g.status_code == 200:
   logging.info("Iotawatt collection successful")
   data['siteMeters'] = {}
   data['siteMeters']['production_kw'] = round( g.json()[0][1] / 1000, 3)
   data['siteMeters']['net_import_kw'] = round( g.json()[0][0] / 1000, 3)
   data['siteMeters']['consumption_kw'] = round( sum(g.json()[0])/1000,3)
else:
   data['error'] = "Collection error: " +g.reason

# Posting to CHQ
payload = json.dumps(data)
header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

try:
   p = requests.post( chq_url, data=payload, headers=header)
except requests.exceptions.Timeout: # todo: specific error handling
   show_error('Timeout.')
   sys.exit(1) # Exit, status code 1.
except requests.exceptions.HTTPError:
   show_error('HTTP Error.')
   sys.exit(1) # Exit, status code 1.
except requests.exceptions.ConnectionError:
   show_error('Connection Error - Could not connect. ')
   sys.exit(1) # Exit, status code 1.
except requests.exceptions.SSLError as expt:
   show_error('SSL Error.')
   show_error('More Details: ')
   # Show the origional error, but exit in a controlled manner.
   try:
      raise Exception('SSL Error Details.')
   except:
      raise expt
   finally:
      sys.exit(1) # Exit, status code 1.
except requests.exceptions.InvalidURL:
   show_error('Invalid URL.')
   show_error('Attempted URL: ' + chq_url)
   sys.exit(1)
except Exception as expt: # If all else fails.
   show_error('Unknown Error.')
   show_error('More Details: ')
   # Show the origional error, but exit in a controlled manner.
   try:
      raise Exception('Error Details.')
   except:
      raise expt
   finally:
      sys.exit(1) # Exit, status code 1.

if p.status_code != 200:
   logging.warning("ChargeHQ API error: " + p.reason)

#print(payload, p.text)
logging.info(payload, p.text)
