from flask_sqlalchemy import SQLAlchemy
import datetime
import base64
import boto3
import io
from io import BytesIO
from mimetypes import guess_type, guess_extension
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    age = db.Column(db.Integer, nullable = False)
    bio = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    images = db.relationship("Asset", cascade = "delete")


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
            "images": [i.serialize_no_id() for i in self.images]
        }    

class Match(db.Model):
    __tablename__ = "match"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    time_stamp = db.Column(db.String, nullable = False)
    user_id_1 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    user_id_2 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    accepted = db.Column(db.Boolean)

    def __init__(self, **kwargs):

        self.time_stamp = kwargs.get("time_stamp", str(datetime.datetime.now()))
        self.user_id_1 = kwargs.get("user_id_1", "")
        self.user_id_2 = kwargs.get("user_id_2", "")

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
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    time_stamp = db.Column(db.String, nullable = False)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable = False)
    message = db.Column(db.String, nullable = False)

    def __init__(self, **kwargs):
        self.sender_id = kwargs.get("sender_id","")
        self.receiver_id = kwargs.get("reciever_id", "")
        self.time_stamp = kwargs.get("time_stamp", "")
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

class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    base_url = db.Column(db.String, nullable = False)
    salt = db.Column(db.String, nullable = False)
    extension = db.Column(db.String, nullable = False)
    width = db.Column(db.Integer, nullable = False)
    height = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)

    def __init__(self, **kwargs):
        self.create(kwargs.get("image_data"))
        self.user_id = kwargs.get("user_id", "")

    def upload(self, img, img_filename):
            """
            attempts to upload image to the specified s3 bucket
            """
            try:
                #temporary save image to temporary location
                img_tmp_loc = f"{BASE_DIR}/{img_filename}"
                img.save(img_tmp_loc)

                #s3 upload
                s3_client = boto3.client("s3")
                s3_client.upload_file(img_tmp_loc, S3_BUCKET_NAME, img_filename)

                s3_resource = boto3.resource("s3")
                object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
                object_acl.put(ACL = "public-read")

                #del img from temporary location
                os.remove(img_tmp_loc)

            except Exception as e:
                print(f"Error when uploading image: {e}")

    def create(self, image_data):
        """
        takes in image in base64 encoding:
        - rejects file if type is not correct
        - generates random string for name of the image
        - decodes image and attempts to upload to AWS
        """    
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f"Extenstion {ext} is invalid!")

            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)

            )
            img_str = re.sub("^data:image/.+;base64,","", image_data)    
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data)) 

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"

            self.upload(img, img_filename)

        except Exception as e:
            print(f"Error when creating image: {e}")

    def serialize(self):
        """
        serializes asset object
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at),
            "user_id": self.user_id
            
        }    
    def serialize_no_id(self):
        """
        serializes asset object
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at),
            
        }          

        



    


    

    

    