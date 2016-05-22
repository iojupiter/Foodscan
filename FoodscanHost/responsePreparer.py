#!flask/bin/python

"""
This micro-service is responsible for the preparation of a response for the frontend interface
It does so by extracting require data from the openfoodfacts response and preparing a tailormade json response.
The response is sent to the foodfactAPI microservice that response the object to the client interface.
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
			pprint(response)
			data = json.loads(response)
			if (data['status_verbose'] == 'product not found'):
				#return product not found
				response = {"status":"product not found"}
				readyResponse = json.dumps(response)
				connection.close()
				publishResponseToFront(readyResponse)
			else:
				#extract desired variables to push to UI
				prodImg = data['product']['image_small_url']
				print " "
				print " "
				print prodImg
				print " "
				print " "
				prodName = data['product']['generic_name']
				print prodName
				print " "
				print " "
				nutrientLevels = data['product']['nutrient_levels']
				print nutrientLevels
				print " "
				print " "
				ingredients = data['product']['ingredients_text']
				print ingredients
				print " "
				print " "
				nutriments = data['product']['nutriments']
				print nutriments
				print " "
				print " "
				response = {
						"status": "product found",
						"prodImg": prodImg,
						"prodName": prodName,
						"nutrientLevels": nutrientLevels,
						"ingredients": ingredients
						}
				readyResponse = json.dumps(response)
				pprint(readyResponse)
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

