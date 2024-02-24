from datetime import datetime
from extensions import db
class Dogs(db.Model):
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow())
    dogs = db.Column(db.Integer, nullable=False, default=0)