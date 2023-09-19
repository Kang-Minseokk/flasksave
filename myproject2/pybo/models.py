from pybo import db


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    height = db.Column(db.Integer, nullable=False)
