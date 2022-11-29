from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#missing location and picture storage + bio is represented as a  string for now
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    age = db.Column(db.Integer, nullable = False)
    bio = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    #implement the location with iOS, latitude and longitude
    #https://www.zerotoappstore.com/how-to-get-current-location-in-swift.html

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
    user_id_1 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    user_id_2 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    accepted = db.Column(db.Boolean)

    def __init__(self, **kwargs):
        #ask Marya if this is the right way to initialize it
        self.time_stamp = kwargs.get("time_stamp", str(datetime.now()))
        self.user_id_1 = kwargs.get("user_id_1", "")
        self.user_id_2 = kwargs.get("user_id_2", "")
        #ask Marya if this is the right way to initialize it
        self.accepted = kwargs.get("accepted", None)

    def serialize(self):
        return {
            "id": self.id,
            "time_stamp": self.time_stamp,
            "user_id_1": self.user_id_1,
            "user_id_2": self.user_id_2,
            "accepted": self.accepted,
        }        


class Message(db.Model):
#id, sender_id, receiver_id, timestamp ,match_id, message
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    #fks that points to user table!
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)


    time_stamp = db.Column(db.String, nullable = False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable = False)
    message = db.Column(db.String, nullable = False)

    def __init__(self, **kwargs):
        self.sender_id = kwargs.get("sender_id","")
        self.receiver_id = kwargs.get("reciever_id", "")
        self.time_stamp = kwargs.get("time_stamp", "")
        #ask Marya if this is the right way to initialize it
        self.accepted = kwargs.get("accepted", None)

    def serialize(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "reciever_id": self.receiver_id,
            "timestamp": self.time_stamp,
            "match_id": self.match_id,
            "message": self.message,
        }


    

    

    