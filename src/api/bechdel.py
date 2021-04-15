from flask_restful import Resource, reqparse
from flask import json, request, redirect, url_for
from db import bechdel_db

parser = reqparse.RequestParser()
session_k = 0

class List_All_Keys(Resource):
    """Lists all keys of movies table"""
    def get(self):
        return dict(bechdel_db.list_all_keys())

class List_Details(Resource):
    """Lists all details of movies table"""
    def get(self):
        return json.jsonify(bechdel_db.list_details())

class Show(Resource):
    """Shows all details of a specific row of movies table given an ID"""
    def get(self):
        id_data = request.args.get('id')
        return json.jsonify(bechdel_db.show(id_data))

class Register(Resource):
    """Registers a new user"""
    def post(self):
        usern = request.form['username']
        password = request.form['passw']
        return json.jsonify(bechdel_db.create_user(usern, password))

class Login_User(Resource):
    """Logs a user in given username and password"""
    def post(self):

        global session_k

        usern = request.form['username']
        password = request.form['passw']

        results = bechdel_db.generate_session_key(usern, password)
        session_k = results[0]

        return json.jsonify(results)

class Logout_User(Resource):
    """Logs a user out given a session key"""
    def post(self):
        global session_k

        cur_session_k = session_k
        session_k = 0

        return json.jsonify(bechdel_db.logout(cur_session_k))

class UserAPI(Resource):
    """UserAPI for create and delete CRUD methods"""
    def post(self):
        """Creates a movie"""
        global session_k

        title_data = request.form['title']
        rating_data = request.form['rating']
        year_data = request.form['year']

        return json.jsonify(bechdel_db.create(rating_data, title_data, year_data, session_k))

    def delete(self):
        """Deletes a movie"""
        global session_k

        parser.add_argument('title', type = str)
        args = parser.parse_args()

        return json.jsonify(bechdel_db.delete(args['title'], session_k))

class UpdateRating(Resource):
    """Updates a movie rating given a session key"""
    def post(self):
        global session_k

        new_rating = request.form['rating']
        title_data = request.form['title']

        return json.jsonify(bechdel_db.update_movie_rating(new_rating, title_data, session_k))
