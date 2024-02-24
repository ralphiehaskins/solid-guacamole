#!/usr/bin/env python3
import requests
from flask import Flask
from models import Dogs
from extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Dogs.sqlite3'
db.init_app(app)

def get_api_token():
    url = "https://api.petfinder.com/v2/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": "sYLEidGfuRLLXBSjE2LnM9Gq8fVbGJVDHpgQ1NyXiGgoHva3DE",
        "client_secret": "yR1KCcztClukDcKHorxbj7PuhCoicLV93mER0PmC"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        return access_token
    else:
        print("Failed to get API token:", response.text)
        return None

def get_chihuahua():
    token = get_api_token()
    response = requests.get(f"https://api.petfinder.com/v2/animals?type=dog&breed=Chihuahua&location=Texas", headers={"Authorization" : f"Bearer {token}"})
    return response.json()['pagination']['total_count']

'''
In main we first get the current temperature and then 
create a new object that we can add to the database. 
'''
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        current_number_chihuahuas = get_chihuahua()
        print(current_number_chihuahuas)
        new_entry = Dogs(dogs=current_number_chihuahuas)
        db.session.add(new_entry)
        db.session.commit()
