#! /usr/bin/env python

# run locally with this:
# ./buildJSONLDContexts.py ./ ../API/Specification/BrAPI-Core/brapi_openapi.yaml ../API/Specification/BrAPI-Phenotyping/brapi_openapi.yaml ../API/Specification/BrAPI-Genotyping/brapi_openapi.yaml ../API/Specification/BrAPI-Germplasm/brapi_openapi.yaml

import yaml
import sys
import json
from fileinput import filename

dataDictionary = {}


def findType(term, termSchema):
	type = "xsd:string"
	if 'type' in termSchema:
		type = "xsd:" + termSchema['type']
	elif '$ref' in termSchema:
		type = "brapi:" + termSchema['$ref'].split('/')[-1]
	
	return type

def isObject(termSchema):
	return ('type' in termSchema and termSchema['type'] == 'object') or ('properties' in termSchema)

def isArray(termSchema):
	return ('type' in termSchema and termSchema['type'] == 'array' and 'items' in termSchema)

def isString(termSchema):
	return ('type' in termSchema and termSchema['type'] == 'string')


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
	contextObj = {
		"@context": {
			"@version": 1.1,
			"brapi": "https://brapi.org/jsonld/jsonld.html#",
			"xsd": "http://www.w3.org/2001/XMLSchema#",
			"metadata":"brapi:metadata",
			"result": "brapi:result",
			"data": "brapi:data"
		} 
	}
	
	terms = recurseThroughAllProperties(schemaName, schemaObj)
	contextObj['@context'].update(terms)
	return contextObj

def recurseThroughAllProperties(schemaName, schemaObj):
	contextObj = {}
	if 'properties' in schemaObj:
		for term in schemaObj['properties']:
			termObj = schemaObj['properties'][term]
			addTermToDataDictionary(schemaName, term, termObj)
			id = "brapi:" + term
			
			if isObject(termObj):
				contextObj.update(recurseThroughAllProperties(term, termObj))
				contextObj[term] = id
			elif isArray(termObj):
				if isObject(termObj['items']):
					contextObj.update(recurseThroughAllProperties(term, termObj['items']))
				contextObj[term] = {
					"@id": id,
					"@container" : "@list"
				}
			elif isString(termObj):
				contextObj[term] = id
			else:
				contextObj[term] = {
					"@id": id,
					"@type": findType(term, termObj)
				}

	return contextObj

def buildContexts(rootPath, inputArr):
	fileObj = {'components':{'schemas':{}}}
	for filePath in inputArr:
		with open(filePath, "r") as stream:
			try:
				yamlObj = yaml.load(stream)
				fileObj['components']['schemas'].update(yamlObj['components']['schemas'])
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
inputArr = []

if len(sys.argv) > 1 :
	rootPath = sys.argv[1]
if len(sys.argv) > 2 :
	inputArr = sys.argv[2:]

buildContexts(rootPath, inputArr)

pageHTMLTemplate = loadTemplateFile(rootPath, 'page-template.html')
termHTMLTemplate = loadTemplateFile(rootPath, 'term-template.html')
defHTMLTemplate = loadTemplateFile(rootPath, 'def-template.html')
contextHTMLTemplate = loadTemplateFile(rootPath, 'context-template.html')

buildDataDictionary(rootPath)
