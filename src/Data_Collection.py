#!/usr/bin/env python3
from datetime import timedelta, datetime

import requests
from flask import Flask
from models import Dogs
from extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlqcvjnrtasrxj:3c63e4fcc60e28930ac97c0d11ea6513d22f4ec7a889178d02af32f73a113409@ec2-54-156-8-21.compute-1.amazonaws.com:5432/dbklucmcg8du3o'
db.init_app(app)


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


def get_chihuahua_listings_after(after_date_str):
    token = get_api_token()
    response = requests.get(
        f"https://api.petfinder.com/v2/animals?type=dog&after={after_date_str}",
        headers={"Authorization": f"Bearer {token}"})
    count = response.json()['pagination']['total_count']
    return count


def get_chihuahua():
    today = datetime.now().date()
    after_date = datetime(2021, 12, 28).date()
    prev_data = get_chihuahua_listings_after((after_date - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z"))

    chihuahua_data = []

    while after_date < today:
        after_date_str = after_date.strftime("%Y-%m-%dT00:00:00Z")
        curr_count = get_chihuahua_listings_after(after_date_str)
        data_difference = abs(curr_count - prev_data)

        chihuahua_data.append((datetime.strptime(after_date_str, "%Y-%m-%dT%H:%M:%SZ"), data_difference))

        prev_data = curr_count
        after_date += timedelta(days=1)

    return chihuahua_data

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        chihuahua_data = get_chihuahua()
        for after_date, data_difference in chihuahua_data:
            existing_entry = Dogs.query.filter_by(datetime=after_date).first()
            if existing_entry:
                existing_entry.dogs = data_difference  # Update existing entry
            else:
                new_entry = Dogs(datetime=after_date, dogs=data_difference)
                db.session.add(new_entry)  # Insert new entry
            db.session.commit()  # Commit each entry individually


