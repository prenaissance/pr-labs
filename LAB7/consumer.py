import os
import sys
import pika
import product
import pymongo
import threading

client = pymongo.MongoClient("mongodb://localhost:27018/")
db = client["999_products"]

def create_consumer(number: int):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="999_urls", durable=True, auto_delete=False)
    
    def callback(ch, method, properties, body):
        try:
            product_dict = product.get_product_dict(body)
            db["products"].insert_one(product_dict)
            print(f"Consumer {number} processed {body}")
        except:
            print(f"Consumer {number} failed processing {body}")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="999_urls", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def main():
    consumer_count = 2
    try:
        consumer_count = int(sys.argv[1])
    except:
        pass
    
    # spawn separate threads
    threads = []
    for i in range(consumer_count):
        thread = threading.Thread(target=create_consumer, args=(i + 1,))
        thread.start()
        threads.append(thread)

    # wait for threads to finish
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()

