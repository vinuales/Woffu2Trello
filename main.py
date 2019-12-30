# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:14:28 2019

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
    if (cfg['config']['proxy']):
        obj = Woffu(cfg['config']['env']['wu'], cfg['config']['env']['wk'], cfg['config']['proxies'], cfg['config']['debug'])
    else:
        obj = Woffu(cfg['config']['env']['wu'], cfg['config']['env']['wk'])
    return obj

def loadTrello(cfg):
    from woffu_trello import Trello

    if (cfg['config']['proxy']):
        client = Trello(cfg['config']['env']['tk'], cfg['config']['env']['ts'], cfg['config']['env']['tboard'], cfg['config']['proxies'], cfg['config']['debug'])
    else:
        client = Trello(cfg['config']['env']['tk'], cfg['config']['env']['ts'], cfg['config']['env']['tboard'])

    return client

def main():
    cfg = loadYAMLConfig()
    if (cfg['config']['debug']):
            print("Config: {} \n".format(cfg))
            #print(cfg)

    wof = loadWoffu(cfg)
    requests = wof.getRequests('2019-07-01T00:00:00')
    users= wof.getUsers()

    tre = loadTrello(cfg)
    tre.addRequests(requests, wof)
    tre.addUserRequests(users, wof)

if __name__ == "__main__":
    main()