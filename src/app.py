#!/usr/bin/env python3

import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Dogs.sqlite3'
db = SQLAlchemy(app)

class Dogs(db.Model):
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow())
    dogs = db.Column(db.Integer, nullable=False)

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

@app.route("/")
def main():
    return '''
     <form action="/echo_user_input" method="POST">
        <p>Input</p>
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text

if __name__ == "__main__":
    with app.app_context():
        current_number_chihuahuas = get_chihuahua()
        print(current_number_chihuahuas)
        new_entry = Dogs(dogs=current_number_chihuahuas)
        db.session.add(new_entry)
        db.session.commit()
    app.run()
