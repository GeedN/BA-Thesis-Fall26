# gestures.py
# This code implements gesture, animation, and speech command definitions
# along with a menu where these gestures can be executed (for modifying and debugging)
#
# Function definitions, import recommendations, and debugging done with ChatGPT assistance
# Restructuring, simplifying code, gesture tuning, and configuration done by Nisa Geed
# Robot: NAO v6
# To reuse code:
#   execute in a Linux environment with pynaoqi-python2.7-2.8.6.23-linux64
#   Python version 2.7.18
#   Modules used other than NAO-related modules are available on standard Python installations


import sys
import time
import math

sys.path.append(
    r'D:\NAO-coding\pynaoqi-python2.7-2.8.6.23-linux64\lib\python2.7\site-packages'
)
sys.path.append(r'D:\NAO-coding\NAO\lib')

from naoqi import ALProxy


# ============================================================
# CONFIGURATION
# ============================================================

ROBOT_IP = "192.168.0.42"
PORT = 9559

SPEED = 0.1

motion = ALProxy("ALMotion", ROBOT_IP, PORT)
posture = ALProxy("ALRobotPosture", ROBOT_IP, PORT)
audio = ALProxy("ALAudioDevice", ROBOT_IP, PORT)

audio.setOutputVolume(50)

tts = None


# ============================================================
# POSE DEFINITIONS
# Angles are in degrees.
# ============================================================

POSES = {
    "1": {
        "name": "Neutral / relaxed",
        "angles": {
            "HeadYaw": 0,
            "HeadPitch": 0,

            "LShoulderPitch": 80,
            "LShoulderRoll": 8,
            "LElbowYaw": -60,
            "LElbowRoll": -35,

            "RShoulderPitch": 80,
            "RShoulderRoll": -8,
            "RElbowYaw": 60,
            "RElbowRoll": 35,

            "LHipPitch": 0,
            "RHipPitch": 0,

            "LKneePitch": 0,
            "RKneePitch": 0,

            "LAnklePitch": 0,
            "RAnklePitch": 0,
        },
    },

}


ANIMATED_GESTURES = {
    
    "head_in_hands": [
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 15,
                "LShoulderPitch": 65,
                "LShoulderRoll": 12,
                "LElbowYaw": -70,
                "LElbowRoll": -65,
                "RShoulderPitch": 65,
                "RShoulderRoll": -12,
                "RElbowYaw": 70,
                "RElbowRoll": 65,
                "LHand": 0.2,
                "RHand": 0.2,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadPitch": 25,
                "LShoulderPitch": 45,
                "LShoulderRoll": 15,
                "LElbowRoll": -80,
                "RShoulderPitch": 45,
                "RShoulderRoll": -15,
                "RElbowRoll": 80,
                "LHand": 0.8,
                "RHand": 0.8,
            },
            "pause": 0.5,
        },
        {
            "pose": {
                "HeadPitch": 28,
                "LShoulderPitch": 42,
                "RShoulderPitch": 42,
                "LHand": 1.0,
                "RHand": 1.0,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadPitch": 15,
                "LShoulderPitch": 60,
                "LElbowRoll": -65,
                "RShoulderPitch": 60,
                "RElbowRoll": 65,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 0,
                "LShoulderPitch": 80,
                "LShoulderRoll": 8,
                "LElbowYaw": -60,
                "LElbowRoll": -35,
                "RShoulderPitch": 80,
                "RShoulderRoll": -8,
                "RElbowYaw": 60,
                "RElbowRoll": 35,
                "LHipPitch": 0,
                "RHipPitch": 0,
                "LKneePitch": 0,
                "RKneePitch": 0,
                "LAnklePitch": 0,
                "RAnklePitch": 0,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.3,
        },
    ],

    "embarrassed_shy": [
        {
            "pose": {
                "HeadYaw": 12,
                "HeadPitch": 10,
                "LShoulderPitch": 60,
                "LShoulderRoll": 15,
                "LElbowYaw": -70,
                "LElbowRoll": -55,
                "RShoulderPitch": 70,
                "RShoulderRoll": -18,
                "RElbowYaw": 75,
                "RElbowRoll": 50,
                "LHand": 0.0,
                "RHand": 0.3,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadYaw": 18,
                "HeadPitch": 25,
                "LShoulderPitch": 45,
                "LShoulderRoll": 18,
                "LElbowYaw": -75,
                "LElbowRoll": -70,
                "RShoulderPitch": 65,
                "RElbowRoll": 55,
                "LHand": 0.4,
                "RHand": 0.7,
            },
            "pause": 0.3,
        },
        {
            "pose": {
                "HeadYaw": 22,
                "HeadPitch": 28,
                "LShoulderPitch": 40,
                "LElbowRoll": -75,
                "LHand": 0.8,
                "RShoulderPitch": 60,
                "RHand": 0.9,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadYaw": -12,
                "HeadPitch": 20,
                "LShoulderPitch": 50,
                "LElbowRoll": -65,
                "LHand": 0.0,
                "RShoulderPitch": 68,
                "RHand": 0.0,
            },
            "pause": 0.3,
        },
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 0,
                "LShoulderPitch": 80,
                "LShoulderRoll": 8,
                "LElbowYaw": -60,
                "LElbowRoll": -35,
                "RShoulderPitch": 80,
                "RShoulderRoll": -8,
                "RElbowYaw": 60,
                "RElbowRoll": 35,
                "LHipYawPitch": 0,
                "LHipPitch": 0,
                "RHipPitch": 0,
                "LKneePitch": 0,
                "RKneePitch": 0,
                "LAnklePitch": 0,
                "RAnklePitch": 0,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.3,
        },
    ],

    "discouraged_withdrawn": [
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 18,
                "LShoulderPitch": 85,
                "LShoulderRoll": 6,
                "LElbowYaw": -60,
                "LElbowRoll": -25,
                "RShoulderPitch": 85,
                "RShoulderRoll": -6,
                "RElbowYaw": 60,
                "RElbowRoll": 25,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadPitch": 28,
                "LShoulderPitch": 90,
                "RShoulderPitch": 90,
                "LHipPitch": -7,
                "RHipPitch": -7,
                "LKneePitch": 14,
                "RKneePitch": 14,
                "LAnklePitch": -6,
                "RAnklePitch": -6,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "LShoulderRoll": 3,
                "RShoulderRoll": -3,
                "LElbowRoll": -22,
                "RElbowRoll": 22,
                "LHand": 0.9,
                "RHand": 0.9,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "LShoulderPitch": 95,
                "RShoulderPitch": 95,
                "LShoulderRoll": 10,
                "RShoulderRoll": -10,
                "LHand": 0.5,
                "RHand": 0.5,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadPitch": 12,
                "LShoulderPitch": 85,
                "RShoulderPitch": 85,
                "LHipPitch": -2,
                "RHipPitch": -2,
                "LKneePitch": 4,
                "RKneePitch": 4,
                "LAnklePitch": -1,
                "RAnklePitch": -1,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 0,
                "LShoulderPitch": 80,
                "LShoulderRoll": 8,
                "LElbowYaw": -60,
                "LElbowRoll": -35,
                "RShoulderPitch": 80,
                "RShoulderRoll": -8,
                "RElbowYaw": 60,
                "RElbowRoll": 35,
                "LHipPitch": 0,
                "RHipPitch": 0,
                "LKneePitch": 0,
                "RKneePitch": 0,
                "LAnklePitch": 0,
                "RAnklePitch": 0,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.2,
        },
    ],

    "apologetic_sorry": [
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 8,
                "LShoulderPitch": 55,
                "LShoulderRoll": 5,
                "LElbowYaw": -55,
                "LElbowRoll": -25,
                "RShoulderPitch": 65,
                "RShoulderRoll": -12,
                "RElbowYaw": 65,
                "RElbowRoll": 45,
                "LHand": 0.0,
                "RHand": 0.7,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadPitch": 18,
                "LShoulderPitch": 35,
                "LShoulderRoll": 5,
                "LElbowYaw": -55,
                "LElbowRoll": -25,
                "LHand": 0.0,
                "RHand": 0.9,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "LShoulderPitch": 30,
                "LElbowRoll": -30,
                "LHand": 0.5,
                "RShoulderPitch": 60,
                "RHand": 0.5,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadPitch": 25,
                "LShoulderPitch": 55,
                "LHand": 0.0,
                "RShoulderPitch": 60,
                "RHand": 0.0,
                "LHipPitch": -6,
                "RHipPitch": -6,
                "LKneePitch": 8,
                "RKneePitch": 8,
                "LAnklePitch": -3,
                "RAnklePitch": -3,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadPitch": 8,
                "LHipPitch": -2,
                "RHipPitch": -2,
                "LKneePitch": 3,
                "RKneePitch": 3,
                "LAnklePitch": -1,
                "RAnklePitch": -1,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 0,
                "LShoulderPitch": 80,
                "LShoulderRoll": 8,
                "LElbowYaw": -60,
                "LElbowRoll": -35,
                "RShoulderPitch": 80,
                "RShoulderRoll": -8,
                "RElbowYaw": 60,
                "RElbowRoll": 35,
                "LHipPitch": 0,
                "RHipPitch": 0,
                "LKneePitch": 0,
                "RKneePitch": 0,
                "LAnklePitch": 0,
                "RAnklePitch": 0,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.2,
        },
    ],

    "dejected_slouched": [
        {
            "pose": {
                "HeadYaw": -8,
                "HeadPitch": 18,
                "LShoulderPitch": 90,
                "LShoulderRoll": 8,
                "LElbowYaw": -60,
                "LElbowRoll": -25,
                "RShoulderPitch": 90,
                "RShoulderRoll": -8,
                "RElbowYaw": 60,
                "RElbowRoll": 25,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadYaw": -12,
                "HeadPitch": 28,
                "LHipPitch": -8,
                "RHipPitch": -8,
                "LKneePitch": 15,
                "RKneePitch": 15,
                "LAnklePitch": -7,
                "RAnklePitch": -7,
                "LShoulderPitch": 95,
                "RShoulderPitch": 95,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "LShoulderRoll": 5,
                "RShoulderRoll": -5,
                "LHand": 1.0,
                "RHand": 1.0,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadYaw": 8,
                "HeadPitch": 28,
                "LShoulderPitch": 100,
                "RShoulderPitch": 100,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.2,
        },
        {
            "pose": {
                "HeadYaw": -5,
                "HeadPitch": 30,
                "LShoulderPitch": 95,
                "RShoulderPitch": 95,
                "LHand": 0.4,
                "RHand": 0.4,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 12,
                "LShoulderPitch": 85,
                "RShoulderPitch": 85,
                "LHipPitch": -3,
                "RHipPitch": -3,
                "LKneePitch": 5,
                "RKneePitch": 5,
                "LAnklePitch": -2,
                "RAnklePitch": -2,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.3,
        },
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 0,
                "LShoulderPitch": 80,
                "LShoulderRoll": 8,
                "LElbowYaw": -60,
                "LElbowRoll": -35,
                "RShoulderPitch": 80,
                "RShoulderRoll": -8,
                "RElbowYaw": 60,
                "RElbowRoll": 35,
                "LHipPitch": 0,
                "RHipPitch": 0,
                "LKneePitch": 0,
                "RKneePitch": 0,
                "LAnklePitch": 0,
                "RAnklePitch": 0,
                "LHand": 0.0,
                "RHand": 0.0,
            },
            "pause": 0.2,
        },
    ],
    "sad_slouch" : [
        {
            "pose": {
                "HeadYaw": 0,
                "HeadPitch": 20,

                "LShoulderPitch": 75,
                "LShoulderRoll": 8,
                "LElbowYaw": -60,
                "LElbowRoll": -30,

                "RShoulderPitch": 75,
                "RShoulderRoll": -8,
                "RElbowYaw": 60,
                "RElbowRoll": 30,
            },
            "pause": 0.1,
        },

        # Stage 2: add a gentle crouch and forward lean
        {
            "pose": {
                "LHipPitch": -5,
                "RHipPitch": -5,
                "LKneePitch": 8,
                "RKneePitch": 8,
                "LAnklePitch": -3,
                "RAnklePitch": -3,
            },
            "pause": 0.2,
        },
    ],

    "chest_to_chest": [
        # Stage 1: Arms close to chest
        {
            "pose": {
                "LShoulderPitch": 65,
                "LShoulderRoll": 12,
                "LElbowYaw": -65,
                "LElbowRoll": -65,

                "RShoulderPitch": 65,
                "RShoulderRoll": -12,
                "RElbowYaw": 65,
                "RElbowRoll": 65,
            },
            "speed": 0.05,
            "pause": 0.1,
        },

        # Stage 2: Open both arms outward
        {
            "pose": {
                "LShoulderPitch": 45,
                "LShoulderRoll": 25,
                "LElbowYaw": -60,
                "LElbowRoll": -35,

                "RShoulderPitch": 45,
                "RShoulderRoll": -25,
                "RElbowYaw": 60,
                "RElbowRoll": 35,
            },
            "speed": 0.06,
            "pause": 0.2,
        },

        # Stage 3: Bring both arms back toward the chest
        {
            "pose": {
                "LShoulderPitch": 65,
                "LShoulderRoll": 12,
                "LElbowYaw": -65,
                "LElbowRoll": -65,

                "RShoulderPitch": 65,
                "RShoulderRoll": -12,
                "RElbowYaw": 65,
                "RElbowRoll": 65,
            },
            "speed": 0.06,
            "pause": 0.1,
        },
    ],

    "shake_no" : [
        {"pose": {"HeadYaw": 20}, "pause": 0.2},
        {"pose": {"HeadYaw": -20}, "pause": 0.2},
        {"pose": {"HeadYaw": 20}, "pause": 0.2},
        {"pose": {"HeadYaw": 0}, "pause": 0.2},
    ],

    "shrug" : [
        {
            "pose": {
                "LShoulderRoll": 20,
                "RShoulderRoll": -20,
            },
            "pause": 0.1,
        },
        {
            "pose": {
                "LShoulderRoll": 8,
                "RShoulderRoll": -8,
            },
            "pause": 0.2,
        },
    ]
}

MOVEMENTS = {
    # ---------------- STATIC POSES ----------------
    "neutral-relaxed": {
        "kind": "pose",
        "data": POSES["1"]["angles"],
    },

    # ---------------- ANIMATED GESTURES ----------------
    "head-in-hands": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["head_in_hands"],
    },

    "embarrassed-shy": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["embarrassed_shy"],
    },

    "discouraged-withdrawn": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["discouraged_withdrawn"],
    },

    "apologetic-sorry": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["apologetic_sorry"],
    },

    "dejected-slouched": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["dejected_slouched"],
    },

    "sad-slouch": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["sad_slouch"],
    },

    "chest-to-chest": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["chest_to_chest"],
    },

    "shake-no": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["shake_no"],
    },

    "shrug": {
        "kind": "animation",
        "data": ANIMATED_GESTURES["shrug"],
    },
}
# ============================================================
# MOVEMENT FUNCTIONS
# ============================================================

def deg(value):
    return math.radians(value)


def move_pose(pose, speed=SPEED):
    """Move only the joints included in pose."""
    if not pose:
        return

    names = list(pose.keys())
    angles = [deg(pose[name]) for name in names]

    motion.angleInterpolationWithSpeed(
        names,
        angles,
        speed
    )


def perform_gesture(full_pose, arms_only=True, speed=SPEED):
    """
    Execute a pose.

    arms_only=True:
        Move only shoulder, elbow, wrist and hand joints.
        Head and legs are left untouched.

    arms_only=False:
        Move all joints included in full_pose.
    """

    arm_prefixes = (
        "LShoulder", "LElbow", "LWrist", "LHand",
        "RShoulder", "RElbow", "RWrist", "RHand"
    )

    if arms_only:
        pose = {
            joint: angle
            for joint, angle in full_pose.items()
            if joint.startswith(arm_prefixes)
        }
    else:
        pose = dict(full_pose)

    if not pose:
        print("No joints to move for this gesture.")
        return

    move_pose(pose, speed)

def animate_gesture(stages, arms_only=False):
    """
    Execute a gesture in multiple stages.

    Each stage is a dictionary containing:
        pose: joint angles in degrees
        pause: time to wait after the movement
        speed: optional movement speed
    """
    for stage in stages:
        pose = stage["pose"]
        pause = stage.get("pause", 0.3)
        speed = stage.get("speed", SPEED)

        perform_gesture(
            pose,
            arms_only=arms_only,
            speed=speed
        )

        time.sleep(pause)

# ============================================================
# ROBOT INITIALIZATION AND RESET
# ============================================================

def initialize_robot():
    print("Initializing NAO...")

    motion.wakeUp()
    posture.goToPosture("Stand", 0.05)

    time.sleep(1)

    print("Robot is ready.")


def return_to_standing():
    print("Returning to neutral...")

    # Request the standard standing posture.
    posture.goToPosture("Stand", 0.05)

GESTURES = {
    "1": ("Sad slouch - full body",
          lambda: animate_gesture(ANIMATED_GESTURES["sad_slouch"],arms_only=False)),
    "2": ("Sad slouch - arms only",
          lambda: animate_gesture(ANIMATED_GESTURES["sad_slouch"],arms_only=True)),
    "3": ("Nod yes",
          lambda: animate_gesture(ANIMATED_GESTURES["chest_to_chest"],arms_only=False)),
    "4": ("Shake no",
          lambda: animate_gesture(ANIMATED_GESTURES["shake_no"],arms_only=False)),
    "5": ("Shrug",
          lambda: animate_gesture(ANIMATED_GESTURES["shrug"],arms_only=True)),
}

# ============================================================
# POSE MENU
# ============================================================

def select_pose():
    while True:
        print("\n========== POSE MENU ==========")

        for key in sorted(POSES.keys(), key=int):
            print("{}: {}".format(key, POSES[key]["name"]))

        print("0: Return to main menu")

        choice = raw_input("Choose a pose: ").strip()

        if choice == "0":
            return

        if choice not in POSES:
            print("Invalid selection.")
            continue

        selected = POSES[choice]

        print("\nSelected: {}".format(selected["name"]))
        print("1: Arms only")
        print("2: Full pose")
        print("0: Cancel")

        mode = raw_input("Choose movement mode: ").strip()

        if mode == "0":
            continue
        elif mode == "1":
            arms_only = True
        elif mode == "2":
            arms_only = False
        else:
            print("Invalid selection.")
            continue

        try:
            print("Moving into pose...")
            perform_gesture(
                selected["angles"],
                arms_only=arms_only,
                speed=SPEED
            )
            print("Pose completed.")

        except Exception as error:
            print("Movement error:", error)
            return


# ============================================================
# DIALOGUE
# ============================================================

def initialize_dialogue():
    global tts

    if tts is None:
        tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)


def speak(text):
    """Speak text without deliberately changing the selected pose."""
    initialize_dialogue()
    tts.say(text)


def dialogue_menu():
    dialogue_lines = {
        "1": ("Greeting", "Hello! It is nice to meet you."),
        "2": ("Introduce yourself",
              "Hello! I am NAO, your robot assistant."),
        "3": ("Ask a question", "How are you doing today?"),
        "4": ("Say goodbye", "Goodbye! Have a wonderful day."),
    }

    while True:
        print("\n========== DIALOGUE MENU ==========")

        for key in sorted(dialogue_lines.keys(), key=int):
            print("{}: {}".format(
                key, dialogue_lines[key][0]
            ))

        print("5: Speak custom text")
        print("0: Return to main menu")

        choice = raw_input("Choose dialogue: ").strip()

        if choice == "0":
            return

        if choice in dialogue_lines:
            text = dialogue_lines[choice][1]

        elif choice == "5":
            text = raw_input(
                "Enter what NAO should say: "
            ).strip()

            if not text:
                continue

        else:
            print("Invalid selection.")
            continue

        try:
            print("Speaking...")
            speak(text)

        except Exception as error:
            print("Dialogue error:", error)
            return

def gesture_menu():
    while True:
        print("\n========== GESTURE MENU ==========")

        for key in sorted(GESTURES.keys(), key=int):
            print("{}: {}".format(
                key, GESTURES[key][0]
            ))

        print("0: Return to main menu")

        gesture_choice = raw_input(
            "Choose a gesture: "
        ).strip()

        if gesture_choice == "0":
            break

        if gesture_choice not in GESTURES:
            print("Invalid selection.")
            continue

        try:
            name, gesture_function = GESTURES[gesture_choice]
            print("Executing: {}".format(name))
            gesture_function()
            print("Gesture completed.")

        except Exception as error:
            print("Gesture error:", error)
            break

# ============================================================
# MAIN MENU
# ============================================================

def main():
    try:
        initialize_robot()

        while True:
            print("\n========== NAO CONTROL ==========")
            print("1: Choose a pose")
            print("2: Dialogue")
            print("3: Return to neutral standing pose")
            print("4: Choose gestures")
            print("0: Exit")

            choice = raw_input("Choose an option: ").strip()

            if choice == "1":
                select_pose()

            elif choice == "2":
                dialogue_menu()

            elif choice == "3":
                return_to_standing()

            elif choice == "4":
                gesture_menu()

            elif choice == "0":
                break

            else:
                print("Invalid selection.")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    except Exception as error:
        print("Robot control error:", error)

    finally:
        try:
            return_to_standing()
        except Exception as error:
            print("Could not restore standing posture:", error)

        print("Program finished.")


if __name__ == "__main__":
    main()
