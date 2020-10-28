"""REST API for getting speakers."""
import flask
from flask import request

import forgetMeNot
from forgetMeNot import model


@forgetMeNot.app.route('/api/identify', methods=["GET"])
def identify():
    #audio = request.get_json()['audio_string']
    context = {}
    context['speaker'] = 'Allen Gray'

    return flask.jsonify(**context)