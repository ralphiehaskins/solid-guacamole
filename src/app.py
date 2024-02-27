import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request
from sqlalchemy import func

from extensions import db
from src.Data_Collection import Dogs
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gzycfjvofdiwxl:937fd4996cd4e607d53ee6c77496e8130be9a55921ae65a8983ca66ee8bcb529@ec2-52-54-200-216.compute-1.amazonaws.com:5432/d70l82e27csi55'
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
        <p>Enter start date</p>
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
    plt.figure(figsize=(10, 10))
    plt.plot(dates, dogs_count, marker='o', linestyle='-')  # Use plot instead of scatter
    plt.xlabel('Date')
    plt.ylabel('Number of Dogs Available for Adoption')
    plt.title('Number of Dogs Over Time')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.grid(True)

    # Convert plot to image
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{plot_url}"



if __name__ == "__main__":
    app.run(debug=True)
