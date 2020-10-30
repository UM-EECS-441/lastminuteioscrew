"""REST API for getting speakers."""
import flask
from flask import request
import os

import forgetMeNot
from forgetMeNot import model
from forgetMeNot.api.model.speakerrecognition import task_enroll

import base64

@forgetMeNot.app.route('/api/addVoice', methods=["GET"])
def add_voice():
    #name = request.get_json()['name']

    #audio_encode = request.get_json()['audio_string']
    #wav_file = open(name + "/temp.wav", "wb")
    #decode_string = base64.b64decode(audio_encode)
    #wav_file.write(decode_string)

    path = str(os.path.abspath(os.getcwd()) + "/forgetMeNot/api")

    # context = {}
    # context['success'] = path
    # return flask.jsonify(**context)

    enrolled = task_enroll(path + "/data/bea", path + "/model.out")

    status = "true"
    if(not enrolled):
        status = "false"
    context = {}
    context['success'] = str(enrolled)
    return flask.jsonify(**context)
