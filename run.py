from __future__ import print_function
import numpy as np
import speech_recognition as sr
import cv2
import requests
import PIL
import StringIO
import matplotlib
import pdb
matplotlib.use('TkAgg')
import time
from matplotlib.pyplot import imshow
from matplotlib.pyplot import rcParams
from matplotlib.patches import Polygon
from matplotlib.pyplot import gcf, gca
from random import random
from tts_watson.TtsWatson import TtsWatson
import playsound


FEAR0 = 'Are you okay?'
FEAR0A = 'Glad to hear'
FEAR1 = 'Is there someone you do not know at the door?'
FEAR1A = 'Calling the police'
FEAR2 = 'Are you watching a scary movie?'
FEAR2A = 'Have fun'
FEAR3 = 'Did anything break?'
FEAR3A = 'Calling for help'
SADNESS0 = 'Hey Granny! Why the long face? Is everything okay?'
SADNESS0A = 'Then smile! life is great'
SADNESS1 = 'Would you like to hear a song?'
SADNESS1A = 'This one always cheers you up'
SADNESS2 = 'Do you feel like talking to anybody?'
SADNESS2A = 'Calling Andy'
HAPPINESS0 = 'Cool granny, looking good today. Would you like to spread that smile?'
HAPPINESS0A = "Let's go for a walk"
SURPRISED0 = "Anythind interesting?"
SURPRISED0A = "Please, do tell"
FH0 = "What's up granny? Are you tired?"
FH0A = "Go to sleep then!"
FH1 = "Maybe you have a headache then?"
FH1A = "Did you have enough to drink today?"
END = "Okay, I'm here if you need me"

count_questions = {'sadness': 3, 'FH':2, 'happiness': 1, 'surprised': 1, 'fear': 4}


def find_emotion(data):
    emotions = (data.get('faceAttributes')).get('emotion')
    max_emotion =  emotions[max(emotions, key=emotions.get)]
    return emotions.keys()[emotions.values().index(max_emotion)]


def handle_emotions(emotion):
    if 'neutral'==emotion:
        return
    question_index = 0
    while True:   
        if question_index < count_questions.get(emotion):
            question = globals()[emotion.upper() + str(question_index)]
            ttsWatson.play(question)
            response = speech2text()
            if 'yes' in response:
                reply = 1
            else: reply = 0
            if reply:
                ttsWatson.play(globals()[emotion.upper() + str(question_index) + 'A'])
                if emotion == 'sadness' and question_index == 1:
                    playsound.playsound('/Users/home/Downloads/hounddog.mp3',True)
                print ("timing: " + str(time.time() - start))
                break
            elif question_index + 1 == count_questions.get(emotion): 
                ttsWatson.play(END)
                return
        else: 
            ttsWatson.play(END)
            break
        question_index = question_index + 1

def handle_forehead():
    question_index = 0
    while True:
        print (question_index)
        
        if question_index < count_questions.get('FH'):
            question = globals()['FH' + str(question_index)]
            ttsWatson.play(question)
            response = speech2text()
            if 'yes' in response:
                reply = 1
            else: reply = 0
            if reply:
                ttsWatson.play(globals()['FH' + str(question_index) + 'A'])
                break
            else: 
                print ('Hell no!')
                #print (type(globals()['FH' + str(question_index + 1)]))
                if question_index + 1 == count_questions.get('FH'): 
                    ttsWatson.play(END)
                    return
                # else:
                #     print ('voodoo')
                #     print (globals()['FH' + str(question_index + 1)])
        else: 
            ttsWatson.play(END)
            break
        question_index = question_index + 1
        

def speech2text():
   # get audio from the microphone
   r = sr.Recognizer()
   with sr.Microphone() as source:
       print("Speak:")
       audio = r.listen(source)

   try:
       text = r.recognize_google(audio)
       print("You said " + text)
       return text
   except sr.UnknownValueError:
       print("Could not understand audio")
   except sr.RequestError as e:
       print("Could not request results; {0}".format(e))
   return 'sorry, I didn''t get that'



rcParams['figure.figsize'] = (12, 8)
#%matplotlib inline

API_KEY = "ac3a58fe09a54c6fb568546f4d0c0674"
endpoint = 'https://westeurope.api.cognitive.microsoft.com/face/v1.0/detect'
args = {'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
    'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'}
headers = {'Content-Type': 'application/octet-stream',
           'Ocp-Apim-Subscription-Key': API_KEY}
ttsWatson = TtsWatson('0ceb1e44-e69d-4781-8eb9-e214cc8e4389', 'gNFDi45r1APE', 'en-US_AllisonVoice') 

start = time.time()
### CAPTURE VIDEO
cam = cv2.VideoCapture(0)
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1)
    ret, img = cam.read()
    img = cv2.flip(img, 1)
    cv2.imshow('Frame',img)
    scaling_factor = 0.25
    img = cv2.resize(img, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

    f = StringIO.StringIO()
    #pdb.set_trace()
    PIL.Image.fromarray(img).save(f, 'png')
    data = f.getvalue()
    
    response = requests.post(data=data, url=endpoint, headers=headers, params=args)
    result = response.json()
    
    if result:
        try:
            if (result[0].get('faceAttributes').get('occlusion').get('foreheadOccluded')):
                handle_forehead()
                continue
            emotion = find_emotion(result[0])
            print (emotion)
            handle_emotions(emotion)
        
        except KeyError as e:
            # print ("KeyError: " + str(result))
            continue

        
    

    #cv2.waitKey(1)
cv2.destroyAllWindows()
cam.release()




