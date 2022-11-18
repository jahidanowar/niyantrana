"""
-- Niyantran Class  --
-- All The Higher Order functions
"""

# Dependencies
import cv2
import mediapipe as mp
import pyautogui
from google.protobuf.json_format import MessageToDict

from Niyantrana import Niyantrana
# Utils & Classes
from utils.GestureMap import Gest, HLabel;
from LandmarksTracking import HandTracking

# Global Variables
pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

class Niyantran:
    """
    Handles camera, obtain landmarks from mediapipe, entry point
    for whole program.

    Attributes
    ----------
    gc_mode : int
        indicates weather gesture controller is running or not,
        1 if running, otherwise 0.
    cap : Object
        object obtained from cv2, for capturing video frame.
    CAM_HEIGHT : int
        highet in pixels of obtained frame from camera.
    CAM_WIDTH : int
        width in pixels of obtained frame from camera.
    hr_major : Object of 'HandRecog'
        object representing major hand.
    hr_minor : Object of 'HandRecog'
        object representing minor hand.
    dom_hand : bool
        True if right hand is domaniant hand, otherwise False.
        default True.
    """
    gc_mode = 0
    cap = None
    CAM_HEIGHT = None
    CAM_WIDTH = None
    hr_major = None  # Right Hand by default
    hr_minor = None  # Left hand by default
    dom_hand = True

    def __init__(self):
        """Initilaizes attributes."""
        Niyantran.gc_mode = 1
        Niyantran.cap = cv2.VideoCapture(1)
        Niyantran.CAM_HEIGHT = Niyantran.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        Niyantran.CAM_WIDTH = Niyantran.cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    def classify_hands(results):
        """
        sets 'hr_major', 'hr_minor' based on classification(left, right) of
        hand obtained from mediapipe, uses 'dom_hand' to decide major and
        minor hand.
        """
        left, right = None, None
        try:
            handedness_dict = MessageToDict(results.multi_handedness[0])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[0]
            else:
                left = results.multi_hand_landmarks[0]
        except:
            pass

        try:
            handedness_dict = MessageToDict(results.multi_handedness[1])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[1]
            else:
                left = results.multi_hand_landmarks[1]
        except:
            pass

        if Niyantran.dom_hand == True:
            Niyantran.hr_major = right
            Niyantran.hr_minor = left
        else:
            Niyantran.hr_major = left
            Niyantran.hr_minor = right

    def start(self):
        handmajor = HandTracking(HLabel.MAJOR)
        handminor = HandTracking(HLabel.MINOR)

        with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while Niyantran.cap.isOpened() and Niyantran.gc_mode:
                success, image = Niyantran.cap.read()

                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    Niyantran.classify_hands(results)
                    handmajor.update_hand_result(Niyantran.hr_major)
                    handminor.update_hand_result(Niyantran.hr_minor)

                    handmajor.set_finger_state()
                    handminor.set_finger_state()
                    gest_name = handminor.get_gesture()

                    if gest_name == Gest.PINCH_MINOR:
                        Niyantrana.handle_controls(gest_name, handminor.hand_result)
                    else:
                        gest_name = handmajor.get_gesture()
                        Niyantrana.handle_controls(gest_name, handmajor.hand_result)

                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                else:
                    Niyantrana.prev_hand = None
                cv2.imshow('Gesture Controller', image)
                if cv2.waitKey(5) & 0xFF == 13:
                    break
        Niyantran.cap.release()
        cv2.destroyAllWindows()

