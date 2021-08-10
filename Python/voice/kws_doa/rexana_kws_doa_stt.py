import os
import sys
import time
import numpy as np
import collections
from mic_array import MicArray
import snowboydecoder
import speech_recognition as sr
import datetime
from chat_bot_api import startConvo, endConvo, sendMessage

RATE = 16000
CHANNELS = 4
KWS_FRAMES = 10     # ms
DOA_FRAMES = 800    # ms
CONVO_ID = None


model = ['/home/pi/rexana/voice/custom_wake_words/rexana.pmdl',
         '/home/pi/rexana/voice/custom_wake_words/hey_rexana.pmdl',
         '/home/pi/rexana/voice/custom_wake_words/yo_rexana.pmdl']

detection = snowboydecoder.HotwordDetector(model, sensitivity=0.5)


def start_doa():
    detection.terminate()
    history = collections.deque(maxlen=int(DOA_FRAMES / KWS_FRAMES))
    with MicArray(RATE, CHANNELS, RATE * KWS_FRAMES / 1000) as mic:
        for chunk in mic.read_chunks():
            history.append(chunk)
            frames = np.concatenate(history)
            direction = mic.get_direction(frames)
            print('Direction %s Degrees' % (int(direction)))
            mic.close()
            run_stt()


def run_stt():
    # obtain audio from the microphone
    stopped = False
    timeout = time.time() + 60  # 60 seconds from now
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = r.listen(source)
       # recognize speech using Google Speech Recognition
    while True:
        if time.time() > timeout:
            print('timeout')
            start_wake_word()
        else:
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                stt = r.recognize_google(audio)
                print(stt)
                if stt == "stop":
                    print("Stop STT")
                    stopped = True
                    start_wake_word()
                elif stt == "over here" or stt == "look here" or stt == "look over here":
                    print("get doa again")
                    start_doa()
                else:
                    print("thinking....")
                    print(sendMessage(CONVO_ID["convoId"], stt))

            except sr.UnknownValueError:
                print "Google Speech Recognition could not understand audio"
            except sr.RequestError as e:
                print "Could not request results from Google Speech Recognition service; {0}".format(e)

            if not stopped:
                run_stt()


def detected():
    print("KWS detected")
    detection.terminate()
    global CONVO_ID
    CONVO_ID = startConvo()
    start_doa()


def interrupt_callback():
    pass


def start_wake_word():
    print("Listening for wake word")
    detection.start(detected_callback=detected,
                    # audio_recorder_callback=audioRecorderCallback,
                    # interrupt_check=interrupt_callback,
                    sleep_time=0.01)

start_wake_word()
print('add function to add minutes since last activity and go back to sleep')
