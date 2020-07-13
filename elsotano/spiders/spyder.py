import scrapy
import json
from scrapy.linkextractors import LinkExtractor
import csv
import time
import calendar
from datetime import datetime, date

import requests
import os
from urllib.request import urlopen
import urllib.request
import xml.etree.ElementTree as ET

def getFecha():
	#Traemos la fecha
	x = datetime.now()

	dia = str(x.strftime("%d"))
	mes = str(x.strftime("%m"))
	anio = str(x.year)

	return dia + '_' + mes + '_' + anio

def getName(count):
	#Traemos la fecha
	x = datetime.now()

	dia = str(x.strftime("%d"))
	mes = str(x.strftime("%m"))
	anio = str(x.year)
	hora = str(x.strftime("%H"))

	return 'sitemap.' + str(count) + '_'+ dia + '_' + mes + '_' + anio

def loadSitemap(sitemapList):
	count = 0
	listNames = []
	for s in sitemapList :
		resp = requests.get(s)
		name = getName(count) + ".xml"
		with open(name, 'wb') as f:
			f.write(resp.content)
		listNames.append(name)
		count += 1
	return listNames

def loadRRS():
	url = 'https://www.elsotano.com/sitemap.xml'
	
	resp = requests.get(url)
	date = "sotano_" + getFecha() + '.xml'

	with open(date, 'wb') as f:
		f.write(resp.content)

	return date

def parseXML(xmlFile):
	print(xmlFile)
	listXml = []
	#Creamos el arbol
	tree = ET.parse(xmlFile)
	root = tree.getroot()

	for r in root:
		listXml.append(r[0].text)

	print(len(listXml))
	return listXml

def downloadUrl(listNames):
	listUrl = []
	count = 0
	for li in listNames:
		tree = ET.parse(li)
		root = tree.getroot()
		for r in root:
			name = r[0].text
			count += 1
			listUrl.append(name)

	return listUrl

def main():
	#Cargamos la URL del XML
	date = loadRRS()

	#Descargamos cada uno de los URLS
	xmlLinio = parseXML(date)

	#Descargamos cada link
	listNames = loadSitemap(xmlLinio)

	#Leemos todos los xml y los guardamos en una lista y leer todos los links
	return downloadUrl(listNames)
	#return downloadUrl("sitemap.123_06_02_2020.xml")

class LinioCat(scrapy.Spider):
	name = 'elsotano'
	allowed_domains = ["www.elsotano.com"]	
	#Corremos así
	# scrapy crawl liniocat -o linioItemsFinal.csv -t csv

	#Vamos a seguir a este link
	#//div[@class="catalogue-list"]/ul/li/a/@href
	def start_requests(self):

		urls = main()

		for i in urls:
			yield scrapy.Request(url=i, callback=self.parse_dir_contents)

	#Funcion que hace click en el link dada una página (2)
	def parse_dir_contents(self, response):

		titulo = response.xpath('(//div[@class="so-booktitle"]/h3[@id="titulo"])[last()]/text()').extract()
		cat = response.xpath('(//ul[@class="so-bookscategories"]/li/a)[last()]/text()').extract()
		des = response.xpath('//div[@class="so-postbookcontent precioDetalle"]/span[@class="so-bookprice"]/ins/text()').extract()
		orig = response.xpath('//div[@class="so-postbookcontent precioDetalle"]/span[@class="so-bookprice"]/del/text()').extract()
		if len(orig) == 0:
			orig = des

		edit = response.xpath('//*[@id="so-content"]/div/div/div[2]/div/ul/li[1]/span[2]/a/text()').extract()
		data = json.loads(response.xpath('//script[@type="application/ld+json"][last()]/text()').extract_first())
		isbn = data['isbn']
		#desc = response.xpath('//p[@id="sinopsis"]/text()').extract()
		url = response.xpath('//link[@rel="canonical"]/@href').extract()
		

		yield {
		'ISBN': isbn,
		'titulo': titulo,
		'precio_descuento': des,
		'precio_lista': orig,
		'categoría': cat,
		'editorial': edit,
		#'descripción': desc,
		'URL':url
		}


