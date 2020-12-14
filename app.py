# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource

from Helper import *

app = Flask(__name__)
app.config["MONGO_DBNAME"] = Mongo.Dbname
app.config["MONGO_URI"] = "mongodb://localhost:27017/" + Mongo.Dbname

mongo = PyMongo(app)
APP_URL = "http://127.0.0.1:5000"
collection = Mongo.collectionname


class Register(Resource):
    def post(self):
        '''
        This api takes body param like this
        {
            "uid":"abc@xyz.com",
            "role" : 1

        }
        :return: It will return jwt token user need to pass this token in header like auth : eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDc4NjUxODYsImlhdCI6MTYwNzg2NTE4MSwidWlkIjoiYWJjQHh5ei5jb20iLCJyb2xlIjoxfQ.w8AmQHxeMD6lGk4_v21OJu1CVhZX6NdDpwqSb0317RE
        '''
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            token = CommanFunction.encode_auth_token(data)
            return jsonify({"token": str(token)})


class Imdb(Resource):
    def get(self, name=None, score=None, director=None):

        '''

        :param name:  if user wants to search movies by name then user need to pass movie name like /api/name/sample_movie_name
        :param score: if user wants to search movies by it's imdb score grater than particular value then user need to pass movie imdb_score like /api/score/sample_score
        :param director: if user wants to search movies by director name then user need to pass director name like /api/director/sample_director_name
        :return:  user will get movie details in json format
        '''

        data = []
        if name:

            movie_info = mongo.db[collection].find_one({IMDB.name: name}, {"_id": 0})
            if movie_info:
                return jsonify({"status": "ok", "data": movie_info})
            else:
                return {"response": "no movie found for {}".format(name)}

        elif score:
            cursor = mongo.db[collection].find({IMDB.imdb_score: {"$gte": float(score)}}, {"_id": 0})
            for movie in cursor:
                data.append(movie)

            return jsonify({IMDB.imdb_score: score, "response": data})

        elif director:
            cursor = mongo.db[collection].find({IMDB.director: director}, {"_id": 0})
            for movie in cursor:
                data.append(movie)

            return jsonify({IMDB.director: director, "response": data})

        else:
            cursor = mongo.db[collection].find({}, {"_id": 0, "update_time": 0})
            for movie in cursor:
                data.append(movie)

            return jsonify({"response": data})

    def post(self):
        '''
        By using this Api user can add new movie details
        For this user need to pass jwt token in header's auth param if user's role is 1(admin) then user can add movie other wise operation will not be allowed
        :return:
        '''
        role = CommanFunction.decode_auth_token(request.headers.get('auth'))
        if role == 1:
            data = request.get_json()
            if not data:
                data = {"response": "ERROR"}
                return jsonify(data)
            else:
                name = data.get('name')
                if name:
                    if mongo.db[collection].find_one({IMDB.name: name}):
                        return {"response": "Data already exists."}
                    else:
                        mongo.db[collection].insert(data)
                        return {"respinse": "data inserted"}
                else:
                    return {"response": "name is missing"}
        else:
            return {"response": "user is not authorized to access the resource"}

    def put(self, name):
        '''
        BY using this api user can update existing movie details
        For this user need to pass jwt token in header's auth param if user's role is 1(admin) then user can add movie other wise operation will not be allowed
        :param name: user needs pass movie name which he want's to change
        :return:
        '''
        role = CommanFunction.decode_auth_token(request.headers.get('auth'))
        if role == 1:
            data = request.get_json()
            mongo.db[collection].update({IMDB.name: name}, {'$set': data})
            return {"response": "data has been updated"}
        else:
            return {"response": "user is not authorized to access the resource"}

    def delete(self, name):
        '''
                BY using this api user can delete existing movie details
                For this user need to pass jwt token in header's auth param if user's role is 1(admin) then user can add movie other wise operation will not be allowed
                :param name: user needs pass movie name which he want's to change
                :return:
                '''
        role = CommanFunction.decode_auth_token(request.headers.get('auth'))
        if role == 1:
            mongo.db[collection].remove({IMDB.name: name})
            return {"response": "data has been deleted"}
        else:
            return {"response": "user is not authorized to access the resource"}


class Index(Resource):
    def get(self):
        return redirect(url_for("imdb"))


api = Api(app)
api.add_resource(Register, "/register")
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Imdb, "/api", endpoint="imdb")
api.add_resource(Imdb, "/api/<string:name>", endpoint="name")
api.add_resource(Imdb, "/api/score/<string:score>", endpoint="score")
api.add_resource(Imdb, "/api/director/<string:director>", endpoint="director")

if __name__ == "__main__":
    app.run()
