#! /usr/bin/env python

import yaml
import sys
import json
from fileinput import filename

dataDictionary = {}


def findId(term, termSchema):
	id = term
	
	return "brapi:" + id

def findType(term, termSchema):
	type = "xsd:string"
	isArr = False
	if 'type' in termSchema:
		if 'array' == termSchema['type'] and 'items' in termSchema:
			isArr = True
			if 'type' in termSchema['items']:
				type = "xsd:" + termSchema['items']['type']
			elif '$ref' in termSchema['items']:
				type = "brapi:" + termSchema['items']['$ref'].split('/')[-1]
		else:
			type = "xsd:" + termSchema['type']
	elif '$ref' in termSchema:
		type = "brapi:" + termSchema['$ref'].split('/')[-1]
	
	return [type, isArr]

def addTermToDataDictionary(schemaName, term, termSchema):
	description = 'DEFINITION MISSING'
	if 'description' in termSchema:
		description = termSchema['description']
		
	if term not in dataDictionary:
		dataDictionary[term] = {}
	if description not in dataDictionary[term]:
		 dataDictionary[term][description] = []
	dataDictionary[term][description].append(schemaName)
	
def buildDataDictionary(rootPath):
	terms = ''
	for term in sorted(dataDictionary.keys()):
		descriptions = ''
		for desc in dataDictionary[term]:
			contexts = ''
			for context in dataDictionary[term][desc]:
				contexts += contextHTMLTemplate.replace('{{CONTEXT}}', context)
			descriptions += defHTMLTemplate.replace('{{CONTEXTS}}', contexts).replace('{{DEF}}', desc)
		terms += termHTMLTemplate.replace('{{ID}}', term).replace('{{DEFS}}', descriptions)
	
	defsPageStr = pageHTMLTemplate.replace('{{TERMS}}', terms)
	fileName = rootPath + '/jsonld.html'
	with open(fileName, 'w') as outfile:
		outfile.write(defsPageStr)
	
def buildContext(schemaName, schemaObj):
	contextObj = {}
	contextObj = {
		"@context": {
			"@version": 1.1,
			"brapi": "https://brapi.org/jsonld.html#",
			"xsd": "http://www.w3.org/2001/XMLSchema#"		
		} 
	}
	if 'properties' in schemaObj:
		for term in schemaObj['properties']:
			addTermToDataDictionary(schemaName, term, schemaObj['properties'][term])
			
			id = findId(term, schemaObj['properties'][term])
			type = findType(term, schemaObj['properties'][term])
			
			if(type[0] == 'xsd:string') and not type[1]:
				contextObj["@context"][term] = id
			else:
				contextObj["@context"][term] = {
					"@id": id,
					"@type": type[0] 
				}
				if type[1]:
					contextObj["@context"][term]['@container'] = '@list'

	return contextObj
	

def buildContexts(rootPath):
	filePath = rootPath + '/brapi_openapi.yaml'
	fileObj = {}
	with open(filePath, "r") as stream:
		try:
			fileObj = yaml.load(stream)
		except yaml.YAMLError as exc:
			print(exc)
	
	if 'components' in fileObj:
		if 'schemas' in fileObj['components']:
			for schema in fileObj['components']['schemas']:
				contextObj = buildContext(schema, fileObj['components']['schemas'][schema])
				fileName = rootPath + '/context/' + schema + '.jsonld'
				with open(fileName, 'w') as outfile:
					json.dump(contextObj, outfile, indent=4, separators=(',', ': '), default=str, sort_keys=True)
					print(fileName)
					
def loadTemplateFile(rootPath, fileName):
	template = ""
	with open(rootPath + "/html-templates/" + fileName, "r") as templateFile:
		template = templateFile.read()
	return template

rootPath = '.'

if len(sys.argv) > 1 :
	rootPath = sys.argv[1];

buildContexts(rootPath)

pageHTMLTemplate = loadTemplateFile(rootPath, 'page-template.html')
termHTMLTemplate = loadTemplateFile(rootPath, 'term-template.html')
defHTMLTemplate = loadTemplateFile(rootPath, 'def-template.html')
contextHTMLTemplate = loadTemplateFile(rootPath, 'context-template.html')

buildDataDictionary(rootPath)
