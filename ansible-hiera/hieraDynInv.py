#!/usr/bin/env python

# Morgan Wallace
# 2016
# Grabs all DNS for 1+ environments and 1+ services, ignoring 0+ services (as specified in group_vars/hieraData.yml)

import sys
import yaml
import json
import os

#argument passed: --list

#Run with ansible: ansible all -i environmentDynInv.py -m ping

#Get hiera data location from hieraData.yml file
f = open('group_vars/hieraData.yml', 'r')
hieraDict = yaml.load(f)
f.close()

envlist = hieraDict['dynInvEnv']
servlist = hieraDict['dynInvServ']
ignorelist = hieraDict['dynInvServIgnore']


f = open(hieraDict['hieraFile'], 'r')
yamlDict = yaml.load(f)
f.close()
hieraBase=yamlDict[':eyaml'][':datadir']

d = {}
if envlist[0] != "all":
	for env in envlist:
		envFile = env+".yaml"
		f = open(os.path.join(hieraBase, "nodes", envFile), 'r')
		yamlDict = yaml.load(f)
		f.close()
		if servlist[0] != "all":
			for serv in servlist:
				for item in yamlDict:
					if item == serv:
						string = env + "." + serv
						d[string] = []
						for DNS in yamlDict[item]:
							d[string].append(DNS)
		else: #use all services (except ignores)
			for item in yamlDict:
				if item not in ignorelist:
					string = env + "." + item
					d[string] = []
					for DNS in yamlDict[item]:
						d[string].append(DNS)


else: #use all environments
	nodesPath = os.path.join(hieraBase,"nodes")
	for file in os.listdir(nodesPath):
		f = open(os.path.join(nodesPath, file), 'r')
		yamlDict=yaml.load(f)
		f.close()
		if servlist[0] != "all":
			for serv in servlist:
				for item in yamlDict:
					if item == serv:
						string = os.path.splitext(file)[0] + "." + serv
						d[string] = []
						for DNS in yamlDict[item]:
							d[string].append(DNS)
		else: #use all services (except ignores)
			for item in yamlDict:
				if item not in ignorelist:
					string = os.path.splitext(file)[0] + "." + item
					d[string] = []
					#print item
					#print yamlDict[item]
					for DNS in yamlDict[item]:
						d[string].append(DNS)

json.dump(d, sys.stdout, indent=4)
