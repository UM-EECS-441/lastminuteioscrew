"""REST API for getting speakers."""
import flask
from flask import request

import forgetMeNot
from forgetMeNot import model


@forgetMeNot.app.route('/api/<int:patient_id>/speakers/', methods=["GET"])
def get_speakers(patient_id):
    context = {}
    # figure out functionality for this
    # logname = request.cookies.get('username')

    # Query for speaker names
    query = "SELECT s.fullname FROM speakers s JOIN patient_speaker p ON p.speakerID=s.speakerID AND p.patientID=?"
    args = (patient_id,)
    speakers = model.get_db().execute(query, args).fetchall()

    context['speakers'] = speakers

    return flask.jsonify(**context)