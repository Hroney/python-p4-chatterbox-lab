#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET','POST'])
def messages():

    if request.method == 'GET':
        messages = []
        for message in db.session.query(Message).order_by(Message.created_at.asc()):
            message_dict = message.to_dict()
            messages.append(message_dict)
        response = make_response(
            jsonify(messages),
            200
        )
        return response
    elif request.method == 'POST':
        new_message = Message(
            body=request.json.get("body"),
            username=request.json.get("username"),
        )
        db.session.add(new_message)
        db.session.commit()

        message_dict = new_message.to_dict()

        response = make_response(
            jsonify(message_dict),
            201
        )
        return response

@app.route('/messages/<int:id>', methods=['GET','PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()
    if message == None:
        response_body = {
            "message": "This record does not exist in our database. Please try again."
        }
        response = make_response(response_body,404)
        return response
    else:
        if request.method == 'GET':
            message_dict = message.to_dict()
            response = make_response(
                jsonify(message_dict),
                200
            )
            return response
        elif request.method == "PATCH":
            for attr in request.json:
                setattr(message, attr, request.json.get(attr))
            db.session.add(message)
            db.session.commit()
            message_dict = message.to_dict()
            response = make_response(
                jsonify(message_dict),
                200
            )
            return response
        elif request.method == "DELETE":
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "delete_successful": True,
                "message": "Message delted."
            }
            response = make_response(
                response_body,
                200
            )
            return response

if __name__ == '__main__':
    app.run(port=5555)
