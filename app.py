from datetime import datetime
import json
import random

from db import db
from flask import Flask
from flask import request

from db import User
from db import Match
from db import Message

app = Flask(__name__)

db_filename = "fetch.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code = 200):
    return json.dumps(data), code

def error_response(message, code = 404):
    return json.dumps({"error" : message}), code    

@app.route("/")
def hello_world():
    return "Hello world!"

# your routes here
@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all users
    """
    users = []
    for user in User.query.all():
        users.append(user.serialize())

    return success_response({"users": users})



@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user. Use this when you need to create a profile.
    """
    body = json.loads(request.data)
    name = body.get("name")
    age =  body.get("age")
    bio = body.get("bio")

    if name is None:
        return json.dumps({"error": "Unable to create user, name not supplied."}), 400
    if age is None:
        return json.dumps({"error": "Unable to create user, age not supplied."}), 400
    if bio is None:
        return json.dumps({"error": "Unable to create user, bio not supplied."}), 400
   
    new_user = User(name = name, age = age, bio = bio)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)
#DONE UP TO HERE

@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Endpoint for getting a user by id. Use this when the user wants to view their
    own profile.
    """
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return error_response("User not found")

    return success_response(user.serialize())    


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a user from database by id. Use this when a user deletes
    their own account.
    """
    # user = DB.get_user_by_id(user_id)
    # if user is None:
    #     return json.dumps({"error": "User not found"}), 404
    # DB.delete_user_by_id(user_id)
    # return json.dumps(user), 200
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return error_response("User not found")

    print('user:' + repr(user))
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())     


@app.route("/api/users/<int:user_id>/", methods=["POST"])
def update_profile(user_id):
    """
    Endpoint for deleting a user from database by id. Use this when user is 
    updating their profile.
    """
    body = json.loads(request.data)
    # name = body.get("name")
    # age = body.get("age")
    # bio = body.get("bio")

    # if name is None:
    #     return json.dumps({"error": "cannot update profile because name not supplied"}), 400
    # if age is None:
    #     return json.dumps({"error": "cannot update profile because age not supplied"}), 400
    # if bio is None:
    #     return json.dumps({"error": "cannot update profile because bio not supplied"}), 400
        

    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return error_response("User not found")

    user.name = body.get("name", user.name)
    user.age = body.get("age", user.age)
    user.bio = body.get("bio", user.bio)
    db.session.commit()
    return success_response(user.serialize())

#DONE UP TO HERE


# (1) first get data from request
# (2) check if both users exist
# (3) Check if there is already a match that exists where user 1 (person who likes) 
# is user 2 (in this case someone else liked them) -> no need to create new match 
# since a match between these two users already exists. Simply set the accepted 
# field to true
# (4) If no match exists -> create new match where accepted field is false

@app.route("/api/matches/", methods=["POST"])
#endpoint is not working but is close to working to API SPECS
def handle_match():
    """
    Endpoint for a handling one user wanting to match with another. Use this 
    anytime user "swipes right/likes" (however it is implemented in frontend) 
    another user.
    """
    #retrieve request data, ensure relevant fields are provided
    body = json.loads(request.data)
    req_user_1_id = body.get("user_1_id")
    req_user_2_id = body.get("user_2_id")
    if req_user_1_id is None:
        return json.dumps({"error": "Unable to initiate match, user 1 id not supplied or does not exist."}), 400
    if req_user_2_id is None:
        return json.dumps({"error": "Unable to initiate match, user 2 id not supplied or does not exist."}), 400

    #check if both users exist and are not the same user
    user_1 = User.query.filter_by(id = req_user_1_id).first()
    user_2 = User.query.filter_by(id = req_user_2_id).first()
    if user_1 is None:
        return json.dumps({"error": "user 1 does not exist"}), 404
    if user_2 is None:
        return json.dumps({"error": "user 2 does not exist"}), 404
    if req_user_1_id == req_user_2_id:
        return json.dumps({"error": "user cannot match with themselves"}), 403


    existing_match = Match.query.filter_by(user_id_1 = req_user_2_id, user_id_2 = req_user_1_id).first()

    if existing_match is None:
        print('NEW MATCH BEING CREATED')
        new_match = Match(time_stamp = 'filler time stamp', user_id_1 = req_user_1_id, user_id_2 = req_user_2_id, accepted = False)
        db.session.add(new_match)
    else:
        print('UPDATING EXISTING MATCH TO BE ACCEPTED')
        existing_match.accepted = True
        new_match = existing_match

    db.session.commit() 
    print(new_match)       
    return success_response(new_match.serialize(), 201)
    

@app.route("/api/matches/<int:match_id>/", methods=["DELETE"])
def unmatch(match_id):
    #done but untested
    """
    Endpoint for deleting a match by its id. Use this when a user wants to 
    unmatch with another user.
    """
    # match = DB.get_match_by_id(match_id)
    # if match is None:
    #     return json.dumps({"error": "match not found"}), 404
    # DB.delete_match_by_id(match_id)
    # return json.dumps(match), 200

    match = Match.query.filter_by(id = match_id)
    if match is None:
        return error_response('match with given match_id does not exist')
    db.session.delete(match)
    db.session.commit()
    return success_response(match.serialize())       

@app.route("/api/matches/<int:user_id>/matched/", methods=["GET"])
def get_user_matches(user_id):
    """
    Endpoint for getting a user's matches by their user id. Use this to display
    a list/grid (however frontend implements) user's current matches.

    Returns an array of ids of users that the user with the given user_id has 
    matched with
    """
    #initialize and empty arrary
    matched_users = []

    #make sure user exists
    user = User.query.filter_by(id = user_id)
    if user is None:
        return error_response('user not found')

    #in mathces table, query for all the user-1_ids being the given id
    #add all of the user_2 ids to that array    

    matches_intitated = Match.query.filter_by(user_id_1 = user_id, accepted = True)
    if matches_intitated is not None:
        for row in matches_intitated:
            matched_users.append(
                User.query.filter_by(id = row.user_id_2))
    
    #in matches table, query for all the user-2_ids being the given id
    #add all of the user_1 ids to that array
    matches_accepted = Match.query.filter_by(user_id_2 = user_id, accepted = True)
    if matches_accepted is not None:
        for row in matches_accepted:
            matched_users.append(
                User.query.filter_by(id = row.user_id_1))

    return success_response(matched_users)

#DONE UP TO HERE BUT NOT TESTED


# potential matches are matches that satisfy:
# (1) the user_id is not user_1_id in a match and accepted is false or
# (2) a match with the user_id does not exist
@app.route("/api/users/<int:user_id>/notmatched/", methods=["GET"])
def get_potential_matches(user_id):
    """
    Endpoint for getting a user's potential matches. Use this to display users
    the user hasn't matched with yet.
    """
    #tracks all 
    potential_matches = []
    matched_user_ids = []


    #make sure user w given id exists
    user = User.query.filter_by(id = user_id)
    if user is None:
        return error_response('user not found')

    #users that have matched with given user but given user hasn't matched with
    users_unaccepted = Match.query.filter_by(user_id_2 = user_id,accepted = False)
    if users_unaccepted is not None:
        for row in users_unaccepted:
            potential_matches.append(
                User.query.filter_by(id = row.user_id_1))

            


    





    # user = DB.get_user_by_id(user_id)
    # if user is None:
    #     return json.dumps({"error": "User not found"}), 404

    # users_matched_with = []
    # matches = DB.get_matches_by_user_id(user_id)
    # for match in matches:
    #     if match["user_1_id"] == user_id:
    #         users_matched_with.append(match["user_2_id"])
    #     elif match["accepted"]:
    #         users_matched_with.append(match["user_1_id"])
    
    # all_users = DB.get_all_users()
    # not_matched = []
    # for user in all_users:
    #     if user["id"] not in users_matched_with and user["id"] != user_id:
    #         not_matched.append(user)

    # return json.dumps({"not matched with":not_matched}), 200

    # if we want this to be a randomized single user from not_matched, the code
    # below will handle that instead of the return statement above
    # if len(not_matched) == 0:
    #     return json.dumps({"error":"out of users!"}), 404
    # return json.dumps(random.choice(not_matched)), 200

@app.route("/api/messages/", methods=["POST"])
def send_message():
    """
    Endpoint for sending a message between users in a match. Use this for when a 
    user wants to send a message.
    """
    # retrieve data from request, make sure it is valid
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    match_id = body.get("match_id")
    message = body.get("message")

    if sender_id is None:
        return json.dumps({"error": "Unable to send message, sender id not supplied."}), 400
    if receiver_id is None:
        return json.dumps({"error": "Unable to send message, receiver id not supplied."}), 400
    if match_id is None:
        return json.dumps({"error": "Unable to send message, match id not supplied."}), 400
    if message is None:
        return json.dumps({"error": "Unable to send message, message not supplied."}), 400

    # check if both users and match exist
    match = DB.get_match_by_id(match_id)
    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)

    if match is None:
        return json.dumps({"error": "match not found"}), 404
    if sender is None:
        return json.dumps({"error": "sender not found"}), 404
    if receiver is None:
        return json.dumps({"error": "receiver not found"}), 404
    
    # check that sender and receiver are matched in match with the match_id
    if (match["user_1_id"] != sender_id or match["user_2_id"] != receiver_id) and (match["user_1_id"] != receiver_id or match["user_2_id"] != sender_id):
        return json.dumps({"error": "these users are not matched"}), 403
    if (match["accepted"] == False):
        return json.dumps({"error": "these users are not matched"}), 403
    
    message_id = DB.insert_message_table(sender_id, receiver_id, match_id, message)
    message = DB.get_message_by_id(message_id)
    return json.dumps(message), 201

@app.route("/api/messages/<int:match_id>/", methods=["GET"])
def get_conversation(match_id):
    """
    Endpoint for getting a conversation between two users. Use this for when 
    the user wants to view a conversation.
    """
    # check if match exists
    match = DB.get_match_by_id(match_id)
    if match is None:
        return json.dumps({"error":"match not found"}), 404

    messages = DB.get_messages_by_match_id(match_id)
    return json.dumps({"messages":messages}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

