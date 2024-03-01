#!/usr/bin/env python3
import os
import sys

import pika
import json
from models import Dogs
from extensions import db
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlqcvjnrtasrxj:3c63e4fcc60e28930ac97c0d11ea6513d22f4ec7a889178d02af32f73a113409@ec2-54-156-8-21.compute-1.amazonaws.com:5432/dbklucmcg8du3o'
db.init_app(app)


def callback(ch, method, properties, body):
    print(f'Received: {body}')
    data = json.loads(body)
    count = data.get("count")
    after_date_str = get_after_date_string()

    with app.app_context():
        db.create_all()
        existing_entry = Dogs.query.filter_by(datetime=after_date_str).first()
        if existing_entry:
            existing_entry.dogs = count  # Update existing entry
        else:
            new_entry = Dogs(datetime=after_date_str, dogs=count)
            db.session.add(new_entry)  # Insert new entry
        db.session.commit()  # Commit each entry individually

def get_after_date_string():
    from datetime import timedelta, datetime
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)  # Calculate yesterday's date
    return yesterday.strftime("%Y-%m-%dT00:00:00Z")

def main():
    connection = pika.BlockingConnection(pika.URLParameters('amqps://msiknnac:tzytvfAu-zDK6KAWmC_hh0ExlRkLsmYH@toad.rmq.cloudamqp.com/msiknnac'))
    channel = connection.channel()

    channel.queue_declare(queue='chihuahua_data')

    channel.basic_consume(queue='chihuahua_data', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
