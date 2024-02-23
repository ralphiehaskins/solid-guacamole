#!/usr/bin/env python3

from flask import Flask, request

from src.Data_Collection import Dogs

app = Flask(__name__)

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
    dogs_records = Dogs.query.all()

    # Print each 'dogs' category value
    for record in dogs_records:
        print(record.dogs)

    # Optionally return a message indicating completion
    return "Dogs printed successfully."

# @app.route('/print_dogs')
# def print_dogs():
#     # Query the database to get all 'dogs' records
#     dogs_records = Dogs.query.all()
#
#     # Print each 'dogs' category value
#     for record in dogs_records:
#         print(record.dogs)
#
#     # Optionally return a message indicating completion
#     return "Dogs printed successfully."