from datetime import datetime
import json
import random

import db
from flask import Flask
from flask import request

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"

# your routes here
@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all users
    """
    return json.dumps({"users":DB.get_all_users()}), 200

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user. Use this when you need to create a profile.
    """
    body = json.loads(request.data)
    name = body.get("name")
    age =  body.get("age")

    if name is None:
        return json.dumps({"error": "Unable to create user, name not supplied."}), 400
    if age is None:
        return json.dumps({"error": "Unable to create user, age not supplied."}), 400
   

    user_id = DB.insert_user_table(name, age)
    user = DB.get_user_by_id(user_id)
    return json.dumps(user), 201

@app.route("/api/users/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Endpoint for getting a user by id. Use this when the user wants to view their
    own profile.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    return json.dumps(user), 200

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a user from database by id. Use this when a user deletes
    their own account.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    DB.delete_user_by_id(user_id)
    return json.dumps(user), 200

@app.route("/api/users/<int:user_id>/", methods=["POST"])
def update_profile(user_id):
    """
    Endpoint for deleting a user from database by id. Use this when user is 
    updating their profile.
    """
    body = json.loads(request.data)
    name = body.get("name")
    age = body.get("age")

    if name is None:
        return json.dumps({"error": "cannot update profile because name not supplied"}), 400
    if age is None:
        return json.dumps({"error": "cannot update profile because age not supplied"}), 400
        
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    DB.update_user_by_id(name, age, user_id)
    updated_user = DB.get_user_by_id(user_id)
    return json.dumps(updated_user), 201

# (1) first get data from request
# (2) check if both users exist
# (3) Check if there is already a match that exists where user 1 (person who likes) 
# is user 2 (in this case someone else liked them) -> no need to create new match 
# since a match between these two users already exists. Simply set the accepted 
# field to true
# (4) If no match exists -> create new match where accepted field is false

@app.route("/api/matches/", methods=["POST"])
def handle_match():
    """
    Endpoint for a handling one user wanting to match with another. Use this 
    anytime user "swipes right/likes" (however it is implemented in frontend) 
    another user.
    """
    #retrieve request data, ensure relevant fields are provided
    body = json.loads(request.data)
    user_1_id = body.get("user_1_id")
    user_2_id = body.get("user_2_id")
    if user_1_id is None:
        return json.dumps({"error": "Unable to initiate match, user 1 id not supplied."}), 400
    if user_2_id is None:
        return json.dumps({"error": "Unable to initiate match, user 2 id not supplied."}), 400

    #check if both users exist and are not the same user
    user_1 = DB.get_user_by_id(user_1_id)
    user_2 = DB.get_user_by_id(user_2_id)
    if user_1 is None:
        return json.dumps({"error": "user 1 does not exist"}), 404
    if user_2 is None:
        return json.dumps({"error": "user 2 does not exist"}), 404
    if user_1_id == user_2_id:
        return json.dumps({"error": "user cannot match with self"}), 403

    #check if match already exists where user 1 from request data is user 2 in 
    #an existing match table entry
    matches = DB.get_matches_by_user_id(user_1_id)
    for match in matches:
        if match["user_2_id"] == user_1_id and match["user_1_id"] == user_2_id:
            match_id = match["id"]
            DB.update_match_by_id(True, match_id)
            new_match = DB.get_match_by_id(match_id)
            return json.dumps(new_match), 201

    #if no match exists, create new match where accepted field is false
    match_id = DB.insert_match_table(user_1_id, user_2_id, False)
    match = DB.get_match_by_id(match_id)
    return json.dumps(match), 201

@app.route("/api/matches/<int:match_id>/", methods=["DELETE"])
def unmatch(match_id):
    """
    Endpoint for deleting a match by its id. Use this when a user wants to 
    unmatch with another user.
    """
    match = DB.get_match_by_id(match_id)
    if match is None:
        return json.dumps({"error": "match not found"}), 404
    DB.delete_match_by_id(match_id)
    return json.dumps(match), 200

@app.route("/api/matches/<int:user_id>/matched/", methods=["GET"])
def get_user_matches(user_id):
    """
    Endpoint for getting a user's matches by their user id. Use this to display
    a list/grid (however frontend implements) user's current matches.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    matches = DB.get_matches_by_user_id(user_id)
    accepted_matches = []
    for match in matches:
        if match["accepted"] == True:
            accepted_matches.append(match)
    return json.dumps({"matches":accepted_matches}), 200

# potential matches are matches that satisfy:
# (1) the user_id is not user_1_id in a match and accepted is false or
# (2) a match with the user_id does not exist
@app.route("/api/users/<int:user_id>/notmatched/", methods=["GET"])
def get_potential_matches(user_id):
    """
    Endpoint for getting a user's potential matches. Use this to display users
    the user hasn't matched with yet.
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    users_matched_with = []
    matches = DB.get_matches_by_user_id(user_id)
    for match in matches:
        if match["user_1_id"] == user_id:
            users_matched_with.append(match["user_2_id"])
        elif match["accepted"]:
            users_matched_with.append(match["user_1_id"])
    
    all_users = DB.get_all_users()
    not_matched = []
    for user in all_users:
        if user["id"] not in users_matched_with and user["id"] != user_id:
            not_matched.append(user)

    return json.dumps({"not matched with":not_matched}), 200

    # if we want this to be a randomized single user from not_matched, the code
    # below will handle that instead of the return statement above
    if len(not_matched) == 0:
        return json.dumps({"error":"out of users!"}), 404
    return json.dumps(random.choice(not_matched)), 200

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

