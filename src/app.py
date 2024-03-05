import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from sqlalchemy import func

from extensions import db
from src.Data_Collection import Dogs
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mlqcvjnrtasrxj:3c63e4fcc60e28930ac97c0d11ea6513d22f4ec7a889178d02af32f73a113409@ec2-54-156-8-21.compute-1.amazonaws.com:5432/dbklucmcg8du3o'
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def main():
    return '''
    <h1>Welcome to our Dog Adoption Data Center!</h1>
    <p>Our site displays the number of dogs available for adoption at rescue centers throughout America. You can explore the number of dogs available on different dates to understand how it varies over time.</p>
    <h2>Explore Dog Adoption Data</h2>
    <form action="/dogs" method="GET">
        <p style="font-size: 16px; color: #333; font-family: Arial, sans-serif;">
            Enter start date <span style="color: red;">*no earlier than 2022</span>
        </p>
        <input name="start_date" type="date" required>
        <p>Enter end date</p>
        <input name="end_date" type="date" required>
        <br><br>
        <input type="submit" value="Submit!">
    </form>
    '''


@app.route("/dogs", methods=["GET"])
def display_dogs():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if start_date > end_date:
                return "Start date cannot be after end date."
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."

        # Filter data between start_date and end_date
        dogs_data = db.session.query(Dogs.datetime, func.sum(Dogs.dogs)).filter(
            Dogs.datetime.between(start_date, end_date)).group_by(Dogs.datetime).all()

        # Unzip the tuples into separate lists for dates and dog counts
        dates, dogs_count = zip(*dogs_data)

        # Plot the graph
        plot_url = plot_graph(dates, dogs_count)

        return f"<img src='{plot_url}'/>"
    else:
        return "Please provide both start date and end date."


def plot_graph(dates, dogs_count):
    # Sort the dates and corresponding dog counts
    dates_sorted, dogs_count_sorted = zip(*sorted(zip(dates, dogs_count)))

    plt.figure(figsize=(10, 10))
    plt.plot(dates_sorted, dogs_count_sorted, marker='o', linestyle='-')  # Use plot instead of scatter
    plt.xlabel('Date')
    plt.ylabel("Net # of Dogs Put Up for Adoption in US")
    plt.title("Net Adoption Trends Over Time for Dogs in the US")
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.grid(True)

    # Convert plot to image
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{plot_url}"

@app.route("/health")
def health_check():
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(debug=True)

