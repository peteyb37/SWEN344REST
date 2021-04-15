import os
import json
from psycopg2.extras import execute_values
import hashlib
import secrets
from .swen344_db_utils import *

def rebuild_tables():
    """Rebuilds tables"""
    exec_sql_file('src/db/schema.sql')

def build_movie_table():
    """Builds the movie table and all other tables as well"""
    exec_sql_file('src/db/schema.sql')

    with open("src/db/bechdel_test_movies.json", "r") as json_file:
        data = json.load(json_file)
    list_of_tuples = []
    for movie in data:
        list_of_tuples.append((
            movie['id'],
            movie['imdbid'],
            movie['rating'],
            movie['title'],
            movie['year']))
    conn = connect()
    cur = conn.cursor()
    sql = "INSERT INTO movies(id, imdbid, rating, title, year) VALUES %s"
    execute_values(cur, sql, list_of_tuples)

    #Create the user blorg
    hashed_password = hashlib.sha512(b'saltfatacidheat').hexdigest()
    cur.execute("INSERT INTO system_users (username, passw) VALUES (%s, %s);", ('blorg', hashed_password))


    conn.commit()
    conn.close()

def list_all_keys():
    """
    Lists all keys from movies table
    Params:
    Returns:
        All keys from movies table
    """
    return exec_get_all('SELECT id, imdbid FROM movies')

def list_details():
    """
    Lists all details about the entire movie table
    Params:
    Returns:
        All details from movie table
    """
    return exec_get_all('SELECT * FROM movies')

def show(id_of_entry):
    """
    Shows all details from a row in the movies table
    Params: 
        id_of_entry : id of movie to look for
    Returns:
        Details of specific id
    """
    return exec_get_all("""SELECT * FROM movies WHERE id = %s""" % (id_of_entry))


def create_user(username, password):
    """
    Creates a user account (Not required by prompt, but included in test cases)
    Params:
        username : The new username for the user
        password : The new password for the user
    Returns:
        None
    """
    conn = connect()
    cur = conn.cursor()

    enc_passw = password.encode('utf-8')
    hashed_password = hashlib.sha512(enc_passw).hexdigest()
    cur.execute("INSERT INTO system_users (username, passw) VALUES (%s, %s);", (username, hashed_password))

    conn.commit()
    conn.close()

def delete_user(username):
    """
    Deletes user from database
    Params:
        username : The username of the user to be deleted
    Returns:
        None
    """
    conn = connect()
    cur = conn.cursor()

    cur.execute("""DELETE FROM system_users WHERE username = '%s'""" % (username))

    conn.commit()
    conn.close()


def validate_session_key(given_session_key):
    """
    Given a session key, determines if session is valid
    Args:
        given_session_key : the key given with the user
    Returns:
        True if session key is valid
        False if session key is invalid
    """
    result = exec_get_all("""SELECT * FROM system_users WHERE session_key = '%s'""" % (given_session_key))

    if len(result) > 0:
        return True
    else:
        return False



def create(rating, title, year, session_k):
    """
    Creates a new movie and adds it to the database
    Params:
        rating : The new rating for the movie to be created
        title : The new title for the movie to be created
        year : The year for the the movie to be created
        session_k : The session key to verify the user is valid
    Returns:
        None
    """

    if validate_session_key(session_k) is False:
        return None

    """First we must get new unique identifiers for the ID section"""
    id_list = exec_get_all("""SELECT id, imdbid FROM movies""")
    highest_id = 0
    highest_imdbid = 0

    for row in id_list:
        if row[0] > highest_id:
            highest_id = row[0]
        if row[1] > highest_imdbid:
            highest_imdbid = row[1]
    new_imdbid = highest_imdbid + 1
    new_id = highest_id + 1

    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO movies(id, imdbid, rating, title, year) VALUES (%s, %s, %s, %s, %s);", (new_id, new_imdbid, rating, title, year))
    conn.commit()
    conn.close()

def delete(movie_name, session_k):
    """
    Deletes the given movie from the database
    Args:
        movie_name : The movie to be deleted
        session_k : The session key to verify the user is valid
    Returns:
        None
    """

    if validate_session_key(session_k) is False:
        return None

    movie_id_tuple = exec_get_all("""SELECT id FROM movies WHERE title = '%s'""" % (movie_name))
    for row in movie_id_tuple:
        movie_id = row[0]

    conn = connect()
    cur = conn.cursor()
    cur.execute("""DELETE FROM movies WHERE id = '%s'""" % (movie_id))
    conn.commit()
    conn.close()

def update_movie_rating(rating, movie_title, session_k):
    """
    Updates a movie rating (Not required by prompt, but included in test cases)
    Args:
        rating : The new rating for the movie
        movie_title : Title of the movie for rating to be changed
        session_k : The session key to verify user is logged in
    Returns:
        None
    """
    if validate_session_key(session_k) is False:
        return None

    conn = connect()
    cur = conn.cursor()
    cur.execute("""UPDATE movies SET rating = '%s' WHERE title = '%s'""" % (rating, movie_title))
    conn.commit()
    conn.close()
    

def generate_session_key(username, passw):
    """
    Generates a session key given a password and username if they exist in the database and adds the session key to the system_users db
    Args:
        username : username of the user
        passw : password of the user
    Returns:
        session_key : the  session key of the logged in user
    """
    enc_passw = passw.encode('utf-8')
    hashed_password = hashlib.sha512(enc_passw).hexdigest()
    results = exec_get_all("""SELECT username, passw FROM system_users WHERE username='%s' AND passw='%s'""" % (username, hashed_password))

    """if results = 1 generate session key, add it to the user table, return the session key"""
    if len(results) == 1:
        session_key = secrets.token_hex(512)

        conn = connect()
        cur = conn.cursor()

        cur.execute("""UPDATE system_users SET session_key='%s' WHERE username='%s'""" % (session_key, username))

        conn.commit()
        conn.close()

        return session_key, 'Login was successful'
    else:
        return 0, 'Login invalid'

def logout(session_key):
    """
    Attempts to log a user out provided a session key
    Args:
        session_key : The session_key of a user
    Returns:
        None
    """
    results = exec_get_all("""SELECT * FROM system_users WHERE session_key = '%s'""" % (session_key))

    if len(results) == 1:
        conn = connect()
        cur = conn.cursor()

        cur.execute("""UPDATE system_users SET session_key='None' WHERE session_key='%s'""" % (session_key))

        conn.commit()
        conn.close()