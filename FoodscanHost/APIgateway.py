#!flask/bin/python

"""
This module does nothing other then pass the barcode json object from the client to the rest of the backend.
This module is here as a provision for scaling the system without breaking the code base.
This adheres to micro-service application architecture principles.


"""

from flask import Flask
import pika 
import json
import os
import subprocess


def subscribe2API():
	"""
	This method subscribes to the foodscanAPI module waiting to treat messages assigned to it.
	Once a message is received, it passes it to a publisher: publish2apiHandler(barcode).
	

	"""
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()

	channel.queue_declare(queue='ToAPIgatewayQueue')

	def callback(ch, method, properties, body):
		if(body != ''):	
			connection.close()
    		publish2apiHandler(body)
			
			
			
	channel.basic_consume(callback, queue='ToAPIgatewayQueue', no_ack=True)

	print(' [*] Waiting for messages. To exit press CTRL+C')
	channel.start_consuming()
	
	return

def publish2apiHandler(barcode):
	"""
	This publisher passes the barcode json object to the OFFapiHandle.py module that will make the curl request.
	

	"""
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='gateway2OFFapi')

	channel.basic_publish(exchange='', routing_key='gateway2OFFapi', body=barcode)
	print "published barcode to OFFapiHandle, passing control back to subscribe2API", barcode
	#connection.close()
	subscribe2API()
	return
	
	
if __name__ == '__main__':
	subscribe2API()