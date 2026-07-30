import pika
import json
from database.database import SessionLocal
from database.models import ExpenseModel, CategoryModel, BudgetModel

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="user-deleted",durable=True)

def callback(ch,method,properties,body):
    event = json.loads(body.decode())
    user_id = event["user_id"]
    db = SessionLocal()
    try:
        db.query(ExpenseModel).filter(ExpenseModel.user_id == user_id).delete()
        db.query(CategoryModel).filter(CategoryModel.user_id == user_id).delete()
        db.query(BudgetModel).filter(BudgetModel.user_id == user_id).delete()
        db.commit()
        print(f"Data deleted for user_id = {user_id}")
    except Exception as e:
        db.rollback()
        print(f"failed to clean up user_id = {user_id} : {e}")
    finally:
        db.close()
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(queue="user-deleted",on_message_callback=callback,auto_ack=False)
print("Expense Service listening to events...")
channel.start_consuming()