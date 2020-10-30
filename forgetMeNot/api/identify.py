"""REST API for getting speakers."""
import flask
import os
from flask import request

import forgetMeNot
from forgetMeNot import model
from forgetMeNot.api.model.speakerrecognition import task_predict

import base64

@forgetMeNot.app.route('/api/identify', methods=["GET"])
def identify():
    #audio_encode = request.get_json()['audio_string']
    #wav_file = open("temp.wav", "wb")
    #decode_string = base64.b64decode(audio_encode)
    #wav_file.write(decode_string)

    # path = forgetMeNot.app.config['MODEL_FILEPATH']
    path = str(os.path.abspath(os.getcwd()) + "/forgetMeNot/api")

    #
    # context = {}
    # context['label'] = str(os.path)
    # return flask.jsonify(**context)

    label, score = task_predict(str(path) + "/temp.wav", str(path) + "/model.out")

    threshold = .5
    if score < threshold:
        label = "Unknown: Score below " + str(threshold)

    context = {}
    context['label'] = label
    context['score'] = score
    return flask.jsonify(**context)
