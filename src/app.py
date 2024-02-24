from flask import Flask, request
from extensions import db
from src.Data_Collection import Dogs
from datetime import datetime, timedelta
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Dogs.sqlite3'
db.init_app(app)


@app.route("/")
def main():
    return '''
     <form action="/dogs" method="GET">
        <p>Enter a date (YYYY-MM-DD)</p>
         <input name="date" type="date">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/dogs", methods=["GET"])
def display_dogs():
    date_str = request.args.get('date')
    if date_str:
        try:
            date_for = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_datetime = datetime.combine(date_for, datetime.min.time())
            end_datetime = datetime.combine(date_for, datetime.max.time())
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."
        dogs_data = db.session.query(Dogs).filter(or_(
            Dogs.datetime.between(start_datetime, end_datetime),
        )).all()
        dogs_list = [dog.dogs for dog in dogs_data]
        return dogs_list
    else:
        dogs_data = db.session.query(Dogs).all()
        dogs_list = [dog.dogs for dog in dogs_data]
        return dogs_list

if __name__ == "__main__":
    app.run(debug=True)
