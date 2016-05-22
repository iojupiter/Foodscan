#!flask/bin/python

"""
This micro-service is responsible for making the API call to the open food facts database.
It does so by listening for a barcode object, decoding it, creating a base query string, initiating the query using Bash cURL.
The response from the cURL request is encoded as a json object and passed to the frontend via a publisher.
"""

from flask import Flask
import pika 
import json
import os
from pprint import pprint

#subscriber listening for incoming messages from API gateway service
def subscribeGateway():
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='gateway2OFFapi')


	def callback(ch, method, properties, barcode):
		print(" [x] Received %r" % barcode)
		p = json.loads(barcode)
		theBarcode = p['barcode']
		#curl http://world.openfoodfacts.org/api/v0/product/7622300026752.json
		query = "http://world.openfoodfacts.org/api/v0/product/%d.json" % (theBarcode)
		print query
		#channel.cancel()
		connection.close()
		#invoke curl popen method
		OFFcaller(query)
		


	channel.basic_consume(callback, queue='gateway2OFFapi', no_ack=True)
	
	print ' [*] Waiting for messages. To exit press CTRL+C'
	
	channel.start_consuming()
	
	
	return
	
	
def OFFcaller(query):
	"""
	declare terminal command curl http://world.openfoodfacts.org/api/v0/product/+barcode+.json to execute
	"""
	OFFquery = "curl "+ query
	#invoke terminal command
	OFFresponse = os.popen(OFFquery).read()

	passToPreparer(OFFresponse)
	
	return
	
def passToPreparer(OFFresponse):
	"""
	Back to front-end
	"""
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='prepareQueue')

	channel.basic_publish(exchange='', routing_key='prepareQueue', body=OFFresponse)
	#connection.close()
	subscribeGateway()
	return

	

if __name__ == '__main__':
	subscribeGateway()