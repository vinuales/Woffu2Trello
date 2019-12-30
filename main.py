# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:14:28 2019

@author: vinuales
"""

import woffu_helpers as helpers

def main():
    cfg = helpers.loadYAMLConfig()
    if (cfg['config']['debug']):
            print("Config: {} \n".format(cfg))

    wof = helpers.loadWoffu(cfg)
    requests = wof.getRequests({'fromDate': '2019-09-01T00:00:00'})
    users= wof.getUsers()

    tre = helpers.loadTrello(cfg)
    tre.addRequests(requests, wof)
    tre.addUserRequests(users, wof)

if __name__ == "__main__":
    main()