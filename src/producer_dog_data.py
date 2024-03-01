#!/usr/bin/env python3
import pika
import requests
import json

def get_chihuahua_listings():
    token = get_api_token()
    after_date_str = get_after_date_string()
    response = requests.get(
        f"https://api.petfinder.com/v2/animals?type=dog&after={after_date_str}",
        headers={"Authorization": f"Bearer {token}"})
    count = response.json()['pagination']['total_count']
    return count

def get_api_token():
    url = "https://api.petfinder.com/v2/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": "7GKYnvhDW5VouyRL78CEFg8usADmcdrIJBbQkPeP5azKnLAI2P",
        "client_secret": "4MXdbVi6B2mq4URyIpZNTp7I2bvbwPaEUDJWblS9"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        return access_token
    else:
        print("Failed to get API token:", response.text)
        return None

def get_after_date_string():
    from datetime import timedelta, datetime
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)  # Calculate yesterday's date
    return yesterday.strftime("%Y-%m-%dT00:00:00Z")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='chihuahua_data')

    chihuahua_count = get_chihuahua_listings()

    channel.basic_publish(exchange='',
                          routing_key='chihuahua_data',
                          body=json.dumps({"count": chihuahua_count}))

    print(" [x] Sent Chihuahua count:", chihuahua_count)
    connection.close()

if __name__ == "__main__":
    main()
