from django.shortcuts import render
# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
import json
import random
from google.oauth2 import id_token
from google.auth.transport import requests
import hashlib, time
import base64, shutil
from app.speaker_recognition import task_predict,task_enroll
import os
import time
def getchatts(request):
    if request.method != 'GET':
        return HttpResponse(status=404)

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM chatts ORDER BY time DESC;')
    rows = cursor.fetchall()

    response = {}
    response['chatts'] = rows
    return JsonResponse(response)


def getSpeakers(request):
    if request.method != 'GET':
        return HttpResponse(status=404)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM speakers ORDER BY id ASC;')
    rows = cursor.fetchall()
    response = {}
    response['speakers'] = rows
    return JsonResponse(response)

def getSpeakersV2(request):
    if request.method != 'GET':
        return HttpResponse(status=404)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM speakersV2 ORDER BY id ASC;')
    rows = cursor.fetchall()
    response = {}
    response['speakers'] = rows
    return JsonResponse(response)

@csrf_exempt
def addchatt(request):
    if request.method != 'POST':
        return HttpResponse(status=404)
    json_data = json.loads(request.body)

    chatterID = json_data['chatterID']
    message = json_data['message']

    cursor = connection.cursor()
    cursor.execute("SELECT username FROM chatters WHERE chatterID='"+ chatterID +"';")

    username = cursor.fetchone()
    if username is None:
        # return an error if there is no chatter with that ID
        return HttpResponse(status=401) # 401 Unauthorized

    # Else, insert into the chatts table
    cursor.execute('INSERT INTO chatts (username, message) VALUES '
                   '(%s, %s);', (username[0], message))

    return JsonResponse({})

@csrf_exempt
def addVoice(request):
    if request.method != 'POST':
        return HttpResponse(status = 404)
    json_data = json.loads(request.body)
    id = json_data['id']
    name = json_data['name'].strip()
    relationship = json_data['relationship'].strip()
    if id == 0:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM speakers;')
        num_rows = cursor.fetchone()[0]
        id = 1
        if num_rows !=0:
            cursor.execute('SELECT MAX(id) FROM speakers;')
            id = cursor.fetchone()[0]+1
        cursor.execute('INSERT INTO speakers (id, name, relationship) VALUES '
                  '(%s, %s, %s);', (id, name, relationship))
    return JsonResponse({})

@csrf_exempt
def addVoiceV2(request):
    if request.method != 'POST':
        return HttpResponse(status = 404)
    json_data = json.loads(request.body)
    id = json_data['id']
    name = json_data['name'].strip()
    relationship = json_data['relationship'].strip()
    photo = json_data['photo']
    cursor = connection.cursor()
    if id == 0:
        cursor.execute('SELECT COUNT(*) FROM speakersV2;')
        num_rows = cursor.fetchone()[0]
        id = 1
        if num_rows !=0:
            cursor.execute('SELECT MAX(id) FROM speakersV2;')
            id = cursor.fetchone()[0]+1
        cursor.execute('INSERT INTO speakersV2 (id, name, relationship, photo) VALUES '
                  '(%s, %s, %s, %s);', (id, name, relationship,photo))
    audio_encode = json_data['audio']
    aacname = os.path.join(os.getcwd(),str(id),'temp.aac')
    wavname = os.path.join(os.getcwd(),str(id),'temp.wav')
    cursor.execute('SELECT DISTINCT id FROM speakersV2;')
    all_ids = cursor.fetchall()
    all_ids = [str(x[0]) for x in all_ids]
    all_dirs = [os.path.join(os.getcwd(),x) for x in all_ids]
    for d in all_dirs:
        if not os.path.exists(d): os.mkdir(d)
    decode_string = base64.b64decode(audio_encode)
    with open(aacname,"wb") as aac_file:
        aac_file.write(decode_string)
    os.system('ffmpeg -i {} {}'.format(aacname, wavname))
    os.remove(aacname)
    new_filename = os.path.join(os.getcwd(),str(id),'{}.wav'.format(str(time.time()).replace('.','_')))
    os.system('mv {} {}'.format(wavname,new_filename))
    if os.path.exists("model.out"):os.remove("model.out")
    task_enroll(' '.join(all_dirs),"model.out")
    return JsonResponse({})


@csrf_exempt
def identify(request):
    if request.method != 'POST':
        return HttpResponse(status = 404)
    response = {}
    response['name'] = 'Bart Simpson'
    response['relationship'] = 'Son'
    if random.random() < 0.5:
        response['name'] = ''
        response['relationship'] = ''
    return JsonResponse(response)

@csrf_exempt
def identifyV2(request):
    if request.method != 'POST':
        return HttpResponse(status = 404)
    json_data = json.loads(request.body)
    audio_encode = json_data['audio']
    aacname = os.path.join(os.getcwd(),'temp.aac')
    wavname = os.path.join(os.getcwd(),'temp.wav')
    modelname = os.path.join(os.getcwd(),'model.out')
    decode_string = base64.b64decode(audio_encode)
    if os.path.exists(aacname): os.remove(aacname)
    if os.path.exists(wavname): os.remove(wavname)
    response = {}
    response['name'] = ''
    response['relationship'] = ''
    response['photo'] = ''
    response['label'] = '0'
    if not os.path.exists("model.out"): return JsonResponse(response)
    with open(aacname,"wb") as aac_file:
        aac_file.write(decode_string)
    os.system('ffmpeg -i {} {}'.format(aacname, wavname)) 
    label, score= task_predict(wavname,"model.out")
    #if score < 0.3: return JsonResponse(response)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM speakersV2 WHERE id={};'.format(label))
    row = cursor.fetchone()
    if len(row) == 0: return JsonResponse(response)
    response['name']  = row[1]
    response['relationship'] = row[2]
    response['photo'] = row[3]
    response['label'] = label
    return JsonResponse(response)

@csrf_exempt
def adduser(request):
    if request.method != 'POST':
        return HttpResponse(status=404)

    json_data = json.loads(request.body)
    clientID = json_data['clientID']   # the front end app's OAuth 2.0 Client ID
    idToken = json_data['idToken']     # user's OpenID ID Token, a JSon Web Token (JWT)

    currentTimeStamp = time.time()
    backendSecret = "ifyougiveamouse"

    try:
        # Collect user info from the Google idToken, verify_oauth2_token checks
        # the integrity of idToken and throws a "ValueError" if idToken or
        # clientID is corrupted or if user has been disconnected from Google
        # OAuth (requiring user to log back in to Google).
        idinfo = id_token.verify_oauth2_token(idToken, requests.Request(), clientID)

        # Verify the token is valid and fresh
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        if currentTimeStamp >= idinfo['exp']:
            raise ValueError('Expired token.')

    except ValueError:
        # Invalid or expired token
        return HttpResponse(status=511)  # 511 Network Authentication Required

    # Check if token already exists in database
    # Instead of the unlimited length ID Token,
    # we work with a fixed-size SHA256 of the ID Token.
    tokenhash = hashlib.sha256(idToken.strip().encode('utf-8')).hexdigest()

    cursor = connection.cursor()
    cursor.execute("SELECT chatterid FROM chatters WHERE idtoken='"+ tokenhash +"';")

    chatterID = cursor.fetchone()
    if chatterID is not None:
        # if we've already seen the token, return associated chatterID
        return JsonResponse({'chatterID': chatterID[0]})

    # If it's a new token, get username
    try:
        username = idinfo['name']
    except:
        username = "Profile NA"

    # Compute chatterID and add to database
    hashable = idToken + username + str(currentTimeStamp) + backendSecret
    chatterID = hashlib.sha256(hashable.strip().encode('utf-8')).hexdigest()
    cursor.execute('INSERT INTO chatters (chatterid, idtoken, username) VALUES '
                   '(%s, %s, %s);', (chatterID, tokenhash, username))

    # Return chatterID
    return JsonResponse({'chatterID': chatterID})


