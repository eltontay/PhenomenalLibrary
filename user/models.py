from flask import Flask, jsonify


class User:

    def signup(self):

        user = {
            "_id": "",
            "name": "",
            "username": "",
            "password": ""
        }

        return jsonify(user), 200
