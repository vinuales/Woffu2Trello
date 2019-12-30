# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 16:53:03 2019

@author: vinuales
"""

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