from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#missing location and picture storage + bio is represented as a  string for now
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    age = db.Column(db.Integer, nullable = False)
    bio = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)

    def __init__(self, **kwargs):
        self.age = kwargs.get("age", "")
        self.bio = kwargs.get("bio", "")
        self.name = kwargs.get("name", "")

    def serialize(self):
        return {
            "id": self.id,
            "age": self.age,
            "bio": self.bio,
            "name": self.name,
        }    

class Match(db.Model):
    __tablename__ = "match"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    time_stamp = db.Column(db.String, nullable = False)
    user_id_1 = db.Column(db.Integer, nullable = False)
    user_id_2 = db.Column(db.Integer, nullable = False)
    accepted = db.Column(db.Boolean, nullable = False)


class Message(db.Model):
#id, sender_id, receiver_id, timestamp ,match_id, message
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    sender_id = db.Column(db.Integer, nullable = False)
    receiver_id = db.Column(db.Integer, nullable = False)
    time_stamp = db.Column(db.String, nullable = False)
    message = db.Column(db.String, nullable = False)


    

    

    