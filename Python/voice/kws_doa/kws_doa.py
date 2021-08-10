import sys
import numpy as np
import collections
from mic_array import MicArray
import snowboydecoder


RATE = 16000
CHANNELS = 4
KWS_FRAMES = 10     # ms
DOA_FRAMES = 800    # ms


#detector = SnowboyDetect('snowboy/resources/common.res', 'snowboy/resources/alexa/alexa_02092017.umdl')
#detector = SnowboyDetect('custom_wake_words/rexana.pmdl', 'custom_wake_words/hey_rexana.pmdl')
detector = snowboydecoder.HotwordDetector(['/home/pi/rexana/mic_array/custom_wake_words/rexana.pmdl',
                                           '/home/pi/rexana/mic_array/custom_wake_words/hey_rexana.pmdl'], sensitivity=0.5)
# detector.SetAudioGain(1)
# detector.SetSensitivity('0.5')
# detector.SetSensitivity('0.9')


def main():
    history = collections.deque(maxlen=int(DOA_FRAMES / KWS_FRAMES))

    try:
        with MicArray(RATE, CHANNELS, RATE * KWS_FRAMES / 1000) as mic:
            for chunk in mic.read_chunks():
                history.append(chunk)

                # Detect keyword from channel 0
                ans = detector.RunDetection(chunk[0::CHANNELS].tostring())
                if ans > 0:
                    frames = np.concatenate(history)
                    direction = mic.get_direction(frames)
                    print('\n{}'.format(int(direction)))

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
