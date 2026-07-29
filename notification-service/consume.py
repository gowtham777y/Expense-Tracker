import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="expense.created", durable=True)

def callback(ch, method, properties, body):
    event = json.loads(body.decode())
    print(f"📩 Notify {event['user_id']}: New expense of ₹{event['amount']} logged in {event['category']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue="expense.created", on_message_callback=callback, auto_ack=False)
print("notification-service listening for expense.created events...")
channel.start_consuming()