import pika

from listing import get_page_links_generator

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
queue = channel.queue_declare(queue="999_urls", durable=True, auto_delete=False)


for page_link in get_page_links_generator(url="https://999.md/ro/list/computers-and-office-equipment/laptops", max_depth=20):
    channel.basic_publish(
        exchange="",
        routing_key="999_urls",
        body=page_link,
    )
    print(f"Sent {page_link}")