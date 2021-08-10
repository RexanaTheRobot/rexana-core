
import sys
import numpy as np
import collections
from mic_array import MicArray
import snowboydecoder

interrupted = False
RATE = 16000
CHANNELS = 4
KWS_FRAMES = 10     # ms
DOA_FRAMES = 800    # ms


model = ['/home/pi/rexana/mic_array/custom_wake_words/rexana.pmdl',
         '/home/pi/rexana/mic_array/custom_wake_words/hey_rexana.pmdl']


def detected():
    print("detected")


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


detection = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
detection.terminate()


history = collections.deque(maxlen=int(DOA_FRAMES / KWS_FRAMES))

try:
    with MicArray(RATE, CHANNELS, RATE * KWS_FRAMES / 1000) as mic:
        for chunk in mic.read_chunks():
            history.append(chunk)
            # Detect keyword from channel 0

            ans = detection.detector.RunDetection(chunk[0::CHANNELS].tostring())

            if ans > 0:
                print ans
                frames = np.concatenate(history)
                direction = mic.get_direction(frames)
                print('\n{}'.format(int(direction)))

except KeyboardInterrupt:
    pass
