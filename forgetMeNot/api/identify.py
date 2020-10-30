"""REST API for getting speakers."""
import flask
from flask import request

import forgetMeNot
from forgetMeNot import model
from forgetMeNot.api.helpers import task_predict

import base64
import os

@forgetMeNot.app.route('/api/identify', methods=["POST"])
def identify():
    audio_encode = request.get_json()['audio']
    
    path = forgetMeNot.app.config['MODEL_FILEPATH']
    if os.path.exists(str(path) + "/temp.wav"):
        os.remove(str(path) + "/temp.wav")
    
    wav_file = open(str(path) + "/temp.wav", "wb")
    decode_string = base64.b64decode(audio_encode + "=========")
    wav_file.write(decode_string)   
    
    label, score = task_predict(str(path) + "/temp.wav", str(path) + "/model.out")

    threshold = .5
    if score < threshold:
        label = "Unknown: Score below " + str(threshold)
    
    context = {}
    context['label'] = label
    context['score'] = score 
    return flask.jsonify(**context)