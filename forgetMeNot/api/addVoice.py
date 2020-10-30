"""REST API for getting speakers."""
import flask
from flask import request

import forgetMeNot
from forgetMeNot import model
from forgetMeNot.api.helpers import task_enroll

import base64
import os

@forgetMeNot.app.route('/api/addVoice', methods=["POST"])
def add_voice():
    name = request.get_json()['name']

    path = forgetMeNot.app.config['MODEL_FILEPATH']
    if not os.path.exists(str(path) + "/" + name):
        os.mkdir(str(path) + "/" + name) 
    audio_encode = request.get_json()['audio']
    
    wav_file = open(str(path) + "/" + name + "/temp.wav", "wb")
    decode_string = base64.b64decode(audio_encode + "========")
    wav_file.write(decode_string)   
    
    enrolled = task_enroll(str(path) + "/" + name + "/", str(path) + "/model.out")
    
    status = "true"
    if(not enrolled):
        status = "false"
    context = {}
    context['success'] = status
    return flask.jsonify(**context)

