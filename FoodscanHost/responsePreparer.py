#!flask/bin/python

"""
This micro-service is responsible for the preparation of a response for the frontend interface
It does so by extracting require data from the openfoodfacts response and preparing a tailormade json response.
The response is sent to the foodfactAPI microservice that response the object to the client interface.

pydoc -w
"""

from flask import Flask
import pika 
import json
import os
import subprocess
from pprint import pprint

def subscribeOFFcall():
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='prepareQueue')


	def callback(ch, method, properties, response):
		#dump the response into local python data structure (dictionary)
		if (response != ''):
			#pprint(response)
			data = json.loads(response)
			if (data['status_verbose'] == 'product not found'):
				#return product not found
				response = {"status":"product not found"}
				readyResponse = json.dumps(response)
				connection.close()
				publishResponseToFront(readyResponse)
			elif (data['status_verbose'] == 'product found'):
				product = data['product']
				if 'image_small_url' not in product:
					prodImg = "unknown"
				else:
					prodImg = data['product']['image_small_url']
				if 'generic_name' not in product:
					prodName = "unknown"
				else:
					prodName = data['product']['generic_name']
				if 'nutrient_levels' not in product:
					nutrientLevels = "unknown"
				else:
					nutrientLevels = data['product']['nutrient_levels']
				if 'ingredients_text' not in product:
					ingredients = "unknown"
				else:
					ingredients = data['product']['ingredients_text']
				if 'allergens_tags' not in product:
					allergens = "unknown"
				else:
					allergens = data ['product']['allergens_tags']
					allergenArray = []
					for a in allergens:
						y = a[3:]
						s = y.encode("utf-8")
						allergenArray.append(s)
				response = {
						"status": "product found",
						"prodImg": prodImg,
						"prodName": prodName,
						"nutrientLevels": nutrientLevels,
						"ingredients": ingredients,
						"allergens": allergenArray
						}
				readyResponse = json.dumps(response)
				#pprint(readyResponse)
				connection.close()
				publishResponseToFront(readyResponse)

	channel.basic_consume(callback, queue='prepareQueue', no_ack=True)
	
	print ' [*] Waiting for messages. To exit press CTRL+C'
	
	channel.start_consuming()
	
	return
	
def publishResponseToFront(readyResponse):
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='queueToFront')
	
	channel.basic_publish(exchange='', routing_key='queueToFront', body=readyResponse)
	print "published ready response to front, passing control back to OFFapi subscriber"
	#connection.close()
	subscribeOFFcall()
	return
	
	
if __name__ == '__main__':
	subscribeOFFcall()

