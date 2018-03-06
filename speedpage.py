#!/usr/bin/python

import time
import sys
import subprocess
import ConfigParser
import json
from datetime import datetime
from elasticsearch import Elasticsearch 
cfg = ConfigParser.ConfigParser()
cfg.readfp(open('parameters.conf'))
es_host=cfg.get('speedpage', 'es_host')
es_port=cfg.get('speedpage', 'es_port')
es_indexprefix=cfg.get('speedpage', 'es_indexprefix')
if cfg.get('speedpage', 'elastic_auth'):
 es_user=cfg.get('speedpage', 'es_user')
 es_password=cfg.get('speedpage', 'es_password')
 #es=Elasticsearch([{'host': es_host, 'port': es_port, 'user': es_user, 'password': es_password}])
 es=Elasticsearch(host=es_host, port=es_port, http_auth=(es_user,es_password))
else:
 es=Elasticsearch([{'host': es_host, 'port': es_port}])

domain=vmname=sys.argv[1]
now=datetime.utcnow()
es_index=es_indexprefix + "-" + datetime.now().strftime('%Y.%m.%d')

def insert_elastic(data):
  es.index(index=es_index, doc_type='speed',body=data) 
def parse_result(result):
  doc = {'@timestamp': now }
  #print result
  result = json.loads(result)
  #print dir(jsonresult)
  domainname=result["overview"]["URL"] 
  speed=result["overview"]["Speed"] 
  strategy=result["overview"]["Strategy"] 
  doc["domainname"]=domainname
  doc["speed"]=speed
  doc["strategy"]=strategy
  print doc
  insert_elastic(doc)

# Desktop Strategy
cmd="psi --threshold 0 --strategy desktop --format json " + domain 
result=subprocess.check_output(cmd, shell=True) 
parse_result(result)
# Mobile Strategy
cmd="psi --threshold 0 --strategy mobile --format json " + domain 
result=subprocess.check_output(cmd, shell=True) 
parse_result(result)
