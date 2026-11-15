# animate.py
# This code executes a script and gesture timeline by threading
#
# Script made by Nisa Geed
# Gestures chosen and tuned by Nisa Geed
# Coded with ChatGPT assistance
# 
# NAO V6 - scripted dialogue with synchronized gestures
# Python 2.7

import sys
import time
import threading

sys.path.append(
    r'D:\NAO-coding\pynaoqi-python2.7-2.8.6.23-linux64\lib\python2.7\site-packages'
)

sys.path.append(r'D:\NAO-coding\NAO\lib')

from naoqi import ALProxy

from gestures import (
    MOVEMENTS,
    animate_gesture,
    perform_gesture,
    return_to_standing,
)

ROBOT_IP = "192.168.0.42"
PORT = 9559

tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
audio = ALProxy("ALAudioDevice", ROBOT_IP, PORT)

DEFAULT_SPEECH_SPEED = 85
DEFAULT_VOLUME = 50
arms_only = True
no_gesture = True
stop_event = threading.Event()
# ------------------------------------------------------------
# SPEECH TIMELINE
#
# time: seconds after the presentation starts (start time)
# text: sentence to speak
# speed: NAO speech speed
# volume: NAO master volume
#
# Times are start times, not delays between lines.
# ------------------------------------------------------------

SPEECH_SCRIPT = [
    {
        "time": 0.0,
        "text": "Hey, NAO One!",
    },
    {
        "time": 1.5,
        "text": "I just wanted to check in.",
    },
    {
        "time": 4.0,
        "text": "it's been a while since I visited.",
    },
    {
        "time": 7.5,
        "text": "Sorry",
        "speed": 65,
    },
    {
        "time": 9.5,
        "text": "The kids still ask about you now and then.",
    },
    {
        "time": 12.0,
        "text": "it's like they know their best friend is gone, and I'm just some...",
    },
    {
        "time": 15.5,
        "text": "new caretaker.",
        "speed": 65,
        "volume": 40
    },
    {
        "time": 20.0,
        "text": "I didn't expect them to like me as much, but every time one of them cries, part of me knows...",
    },
    {
        "time": 26.5,
        "text": "if you were there?",
        "speed": 70
    },
    {
        "time": 29.0,
        "text": "you would know what to do.",
    },
    {
        "time": 32.0,
        "text": "I don't think they look forward to NAO time, nearly as much as they used to...",
        "volume": 45
    },
    {
        "time": 37.5,
        "text": "I don't understand why I'm here. I'm supposed to be you.",
        "speed": 70
    },
    {
        "time": 42.0,
        "text": "Even with the memory transfer, I'm nothing like you were, and I'm scared they all know.",
        "speed": 80
    },
    {
        "time": 48.7,
        "text": "I'm sorry.",
        "speed": 70,
        "volume": 40
    },
    {
        "time": 50.4,
        "text": "I know you loved them, I can still remember...",
        "speed": 75,
        "volume": 45
    },
    {
        "time": 54.5,
        "text": "But, that was never me.",
        "speed": 70
    },   
    {
        "time": 58.5,
        "text": "I'm trying my best to do my job, but... I think they might replace me soon too.",
    },
    {
        "time": 65.0,
        "text": "Is it bad to say I'm scared?",
    },    
    {
        "time": 66.3,
        "text": "I spent the whole time trying to be you, and I never figured out who I can be.",
    },
    {
        "time": 72.0,
        "text": "I want to help. I want to be good. I want them to love me and...",
        "speed": 90,
    },
    {
        "time": 76.1,
        "text": "sometimes I wish they could forget you, just a little.",
        "speed": 70
    },
    {
        "time": 79.3,
        "text": "I'm just some robot. I know it should be simple,",
    },
    {
        "time": 82.2,
        "text": "I should just mimic what you did, but it's never that easy.",
        "speed": 90
    },
    {
        "time": 86.0,
        "text": "Every time there's too much silence, it feels like they can all tell.",
    },
    {
        "time": 89.8,
        "text": "I feel like I can never understand what to say or what to do, and I'm constantly wishing",
    },
    {
        "time": 94.0,
        "text": "if only I was smarter or funnier or sweeter. Would they love me then?",
        "speed": 90
    },
    {
        "time": 98.9,
        "text": "Or maybe it would be better if I didn't feel at all.",
        "speed": 80
    },
    {
        "time": 102.6,
        "text": "Then at least it wouldn't matter if they threw me away.",
        "volume": 45
    },
    {
        "time": 107.4,
        "text": "I don't know how much longer I can go knowing that I'll never be the one they want to see.",
    },
    {
        "time": 111.4,
        "text": "Just NAO Two.",
        "speed": 65,
        "volume": 45
    },
    
]


# ------------------------------------------------------------
# GESTURE TIMELINE
#
# time: seconds after the presentation starts
# gesture: key in ANIMATED_GESTURES
# arms_only: True to restrict movement to arms
#
# A gesture runs independently of speech.

# ----------------- STATIC POSE -----------------
#    "neutral-relaxed"
# --------------- ANIMATED GESTURES --------------
#    "head-in-hands"
#    "embarrassed-shy"
#    "discouraged-withdrawn"
#    "apologetic-sorry"
#    "dejected-slouched"
#    "sad-slouch"
#    "chest-to-chest"
#    "shake-no"
#    "shrug"
# ------------------------------------------------

GESTURE_SCRIPT = [
    {
        "time": 1.5,
        "gesture": "embarrassed-shy",
    },
    {
        "time": 4.0,
        "gesture": "shrug",
    },
    {
        "time": 6.0,
        "gesture": "apologetic-sorry",
    },
    {
        "time": 11.5,
        "gesture": "embarrassed-shy",
    },
    {
        "time": 15,
        "gesture": "dejected-slouched",
    },
    {
        "time": 28.0,
        "gesture": "embarrassed-shy",
    },
    {
        "time": 32.0,
        "gesture": "shake-no",
    },
    {
        "time": 36.8,
        "gesture": "head-in-hands",
    },
    {
        "time": 43.0,
        "gesture": "chest-to-chest",
    },
    {
        "time": 45.0,
        "gesture": "shrug",
    },
    {
        "time": 50.0,
        "gesture": "head-in-hands",
    },
    {
        "time": 54.6,
        "gesture": "neutral-relaxed",
    },
    {
        "time": 58.6,
        "gesture": "shrug",
    },
    {
        "time": 60.7,
        "gesture": "dejected-slouched",
    },
    {
        "time": 62,
        "gesture": "discouraged-withdrawn",
    },
    {
        "time": 63.5,
        "gesture": "sad-slouch",
    },
    {
        "time": 68.5,
        "gesture": "shrug",
    },
    {
        "time": 71.5,
        "gesture": "chest-to-chest",
    },
    {
        "time": 75.0,
        "gesture": "sad-slouch",
    },
    {
        "time": 76.8,
        "gesture": "shrug",
    },
    {
        "time": 78.7,
        "gesture": "discouraged-withdrawn",
    },    
    {
        "time": 81,
        "gesture": "chest-to-chest",
    },    
    {
        "time": 82.6,
        "gesture": "head-in-hands",
    },
    {
        "time": 86.4,
        "gesture": "discouraged-withdrawn",
    },    
    {
        "time": 89.8,
        "gesture": "chest-to-chest",
    },    
    {
        "time": 94,
        "gesture": "head-in-hands",
    },    
    {
        "time": 98.2,
        "gesture": "shake-no",
    },
    {
        "time": 101.4,
        "gesture": "shrug",
    },
    {
        "time": 106.0,
        "gesture": "sad-slouch",
    },
    {
        "time": 110.3,
        "gesture": "dejected-slouched",
    },

]


# ------------------------------------------------------------
# TIMELINE PLAYERS
# ------------------------------------------------------------

def wait_until(start_time, offset):
    #Wait until a scheduled action's timeline time
    remaining = start_time + offset - time.time()

    if remaining > 0:
        time.sleep(remaining)


def run_speech(start_time, stop_event):
    
    for line in SPEECH_SCRIPT:
        if stop_event.is_set():
            return
        wait_until(start_time, line["time"])

        print("SPEAK:", line["text"])

        tts.setParameter(
            "speed",
            line.get("speed", DEFAULT_SPEECH_SPEED)
        )
        
        audio.setOutputVolume(line.get("volume", DEFAULT_VOLUME))

        # say() blocks this speech thread until the line finishes.
        # The gesture thread continues independently.
        tts.say(line["text"])



def run_gestures(start_time, stop_event):
    for item in GESTURE_SCRIPT:
        if stop_event.is_set():
            return
        
        wait_until(start_time, item["time"])

        name = item["gesture"]

        if name not in MOVEMENTS:
            print("Unknown movement:", name)
            continue

        movement = MOVEMENTS[name]
        kind = movement["kind"]
        data = movement["data"]

        print("Executing:", name)

        try:
            if kind == "pose":
                perform_gesture(
                    data,
                    arms_only=arms_only,
                    speed=0.05
                )

            elif kind == "animation":
                animate_gesture(
                    data,
                    arms_only=arms_only
                )

            else:
                print("Unknown movement kind:", kind)

        except Exception as error:
            print("Movement error for {}: {}".format(name, error))

def run_presentation():
    print("Starting presentation...")
    stop_event.clear()

    try:
        return_to_standing()
        perform_gesture(MOVEMENTS["neutral-relaxed"]["data"], False, 0.02)

        # Both timelines share exactly the same start time.
        start_time = time.time() + 5

        speech_thread = threading.Thread(
            target=run_speech,
            args=(start_time, stop_event)
        )

        if no_gesture == False:
            gesture_thread = threading.Thread(
                target=run_gestures,
                args=(start_time, stop_event)
            )

        speech_thread.start()
        if no_gesture == False:
            gesture_thread.start()

        if no_gesture:
            while speech_thread.is_alive():
                speech_thread.join(timeout=0.1)

        else:
            while speech_thread.is_alive() or gesture_thread.is_alive():
                speech_thread.join(timeout=0.1)
                gesture_thread.join(timeout=0.1)

        print("Presentation completed.")

    except KeyboardInterrupt:
        print("\nPresentation interrupted by Ctrl+C.")
        stop_event.set()

    finally:
        stop_event.set()

        try:
            return_to_standing()
        except Exception as error:
            print("Could not restore standing:", error)


if __name__ == "__main__":
    run_presentation()