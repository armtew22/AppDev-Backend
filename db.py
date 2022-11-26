import os
import sqlite3
from datetime import datetime

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the instance
        variable `conn`.
        """
        self.conn = sqlite3.connect(
            "fetch.db", check_same_thread=False
        )
        self.create_user_table()
        self.create_match_table()
        self.create_message_table()
    
    # USER TABLE

    # Not entirely sure how to implement the below yet but will do some research
    # -profile pictures
    # -bio (since we decided that this would have constraints and the user would 
    #  just select from a list of tags)
    # -location 
    def create_user_table(self):
        """
        Using SQL, creates a user table.
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        );
        """)

    def delete_user_table(self):
        """
        Using SQL, delete the user table.
        """
        self.conn.execute("DROP TABLE IF EXISTS user;")

    def get_all_users(self):
        """
        Using SQL, returns all users in a table.
        """
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []
        for row in cursor:
            users.append({"id":row[0], "name":row[1], "age":row[2]})
        return users

    def insert_user_table(self, name, age):
        """
        Using SQL, inserts a user into the user table.
        """
        cursor = self.conn.execute("INSERT INTO user (name, age) VALUES (?, ?);", (name, age))
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, id):
        """
        Using SQL, gets a user by its id.
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,))
        for row in cursor:
            return ({"id":row[0], "name":row[1], "age":row[2]})
        return None

    def delete_user_by_id(self, id):
        """
        Using SQL, delete a user by its id.
        """
        self.conn.execute("DELETE FROM user WHERE id = ?;", (id,))
        self.conn.commit()

    def update_user_by_id(self, name, age, id):
        """
        Using SQL, updates a user in table.
        """
        self.conn.execute("""
        UPDATE user
        SET 
        name = ?, age = ?
        WHERE id = ?;
        """, (name, age, id))
        self.conn.commit()

    # MATCH TABLE

    def create_match_table(self):
        """
        Using SQL, creates a match table.
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS match(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            user_1_id INTEGER NOT NULL,
            user_2_id INTEGER NOT NULL,
            accepted BOOLEAN
        );
        """)

    def get_matches_by_user_id(self, user_id):
        """
        Using SQL, returns all matches where either user 1 or 2 has id user_id.
        """
        cursor = self.conn.execute("SELECT * FROM match WHERE user_1_id = ? OR user_2_id = ?;", (user_id, user_id))
        matches = []
        for row in cursor:
            matches.append({"id":row[0], "timestamp":row[1], "user_1_id":row[2], "user_2_id":row[3], "accepted":row[4]})
        
        return matches

    def insert_match_table(self, user_1_id, user_2_id, accepted):
        """ 
        Using SQL, inserts a match into the matches table. Match has happened
        when user 1 initiates by swiping first even if user 2 hasn't swiped back
        yet.
        """
        cursor = self.conn.execute("INSERT INTO match (timestamp, user_1_id, user_2_id, accepted) VALUES (?, ?, ?, ?);", (str(datetime.now()), user_1_id, user_2_id, accepted))
        self.conn.commit()
        return cursor.lastrowid

    def get_match_by_id(self, id):
        """
        Using SQL, gets a match by its id.
        """
        cursor = self.conn.execute("SELECT * FROM match WHERE id = ?;", (id,))
        for row in cursor:
            return ({"id":row[0], "timestamp":row[1], "user_1_id":row[2], "user_2_id":row[3], "accepted":row[4]})

        return None

    def update_match_by_id(self, accepted, id):
        """
        Using SQL, updates timestamp and accepted of match in table.
        """
        self.conn.execute("""
        UPDATE match
        SET
        timestamp = ?, accepted = ?
        WHERE id = ?;
        """, (str(datetime.now()), accepted, id))
        self.conn.commit()

    def delete_match_by_id(self, id):
        """
        Using SQL, deletes a match by its id.
        """
        self.conn.execute("DELETE FROM match WHERE id = ?;", (id,))
        self.conn.commit()

    # MESSAGE TABLE

    def create_message_table(self):
        """
        Using SQL, creates a message table.
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS message(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            message TEXT NOT NULL
        );
        """)

    def insert_message_table(self, sender_id, receiver_id, match_id, message):
        """
        Using SQL, inserts a message into the messages table.
        """
        cursor = self.conn.execute("INSERT INTO message (sender_id, receiver_id, match_id, timestamp, message) VALUES (?, ?, ?, ?, ?);", (sender_id, receiver_id, match_id, str(datetime.now()), message))
        self.conn.commit()
        return cursor.lastrowid

    def get_message_by_id(self, message_id):
        """
        Using SQL, returns a message by its id.
        """
        cursor = self.conn.execute("SELECT * FROM message WHERE id = ?;", (message_id, ))
        for row in cursor:
            return ({"id":row[0], "sender_id":row[1], "receiver_id":row[2], "match_id":row[3], "timestamp":row[4], "message": row[5]})
        
        return None

    def get_messages_by_match_id(self, match_id):
        """
        Using SQL, returns messages where sender_id or receiever_id is user_id.
        """
        cursor = self.conn.execute("SELECT * FROM message WHERE match_id = ?;", (match_id, ))

        messages = []
        for row in cursor:
            messages.append({"id":row[0], "sender_id":row[1], "receiver_id":row[2], "match_id":row[3], "timestamp":row[4], "message": row[5]})

        return messages

# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
