# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 16:53:03 2019

@author: vinuales
"""

def loadYAMLConfig():
  import yaml
  import os

  root_dir = os.getcwd() + "//"
  with open(root_dir + "config.yaml", 'r') as ymlfile_1:
    cfg = yaml.load(ymlfile_1)

  with open(root_dir + "environment.yaml", 'r') as ymlfile_2:
    env = yaml.load(ymlfile_2)

  cfg['config']['env'] = env[cfg['config']['env']]

  return cfg

def loadWoffu(cfg):
    from woffu import Woffu
    #config_endpoint, config_key, config_proxies=None, config_debug=False)
    
    obj = Woffu(cfg['config']['env'], cfg['config']['debug'], (cfg['config']['proxies'] if cfg['config']['proxy'] else None))
    #if (cfg['config']['proxy']):
    #    obj = Woffu(cfg['config']['env'], cfg['config']['debug'], (cfg['config']['proxies'] if cfg['config']['proxy'] else None))
    #else:
    #    obj = Woffu(cfg['config']['env'], None, cfg['config']['debug'])
    return obj

def loadTrello(cfg):
    from woffu_trello import Trello

    client = Trello(cfg['config']['env'], cfg['config']['debug'], (cfg['config']['proxies'] if cfg['config']['proxy'] else None))
    #if (cfg['config']['proxy']):
    #    client = Trello(cfg['config']['env']['tk'], cfg['config']['env']['ts'], cfg['config']['env']['tboard'], cfg['config']['proxies'], cfg['config']['debug'])
    #else:
    #    client = Trello(cfg['config']['env']['tk'], cfg['config']['env']['ts'], cfg['config']['env']['tboard'])

    return client

def getDateFrom(days):
    from datetime import date, timedelta                   
    return (date.today() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S')
    
def doDict2QueryString(dict):
    from urllib.parse import urlencode
    return urlencode(dict, doseq=True)

def dump_json(file):
    import json
    print("Content:\n {}".format(json.dumps(file, indent=4, sort_keys=True)))
    
def is_json(j):
    import json
    try:
        obj = json.loads(j)
    except ValueError as e:
        return False
    return True

def getDateTimeFormat(s):
    import datetime
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d-%m-%Y, %H:%M:%S')

def getDateFormat(s):
    import datetime
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d-%m-%Y')

def getFileZipped(content):
    from io import BytesIO
    import zipfile

    mem_zip = BytesIO()
    
    with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(content)

    return mem_zip.getvalue()
