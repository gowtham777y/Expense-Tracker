import pika
import json

def publish_event(routing_key, data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=routing_key,durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=routing_key,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()