# Niyantrana: Executes commands according to detected gestures

import pyautogui
import screen_brightness_control as sbc
from utils.GestureMap import Gest


class Niyantrana:
    """
    Executes commands according to detected gestures.

    Attributes
    ----------
    tx_old : int
        previous mouse location x coordinate
    ty_old : int
        previous mouse location y coordinate
    flag : bool
        true if V gesture is detected
    grabflag : bool
        true if FIST gesture is detected
    pinchmajorflag : bool
        true if PINCH gesture is detected through MAJOR hand,
        on x-axis 'Controller.changesystembrightness',
        on y-axis 'Controller.changesystemvolume'.
    pinchminorflag : bool
        true if PINCH gesture is detected through MINOR hand,
        on x-axis 'Controller.scrollHorizontal',
        on y-axis 'Controller.scrollVertical'.
    pinchstartxcoord : int
        x coordinate of hand landmark when pinch gesture is started.
    pinchstartycoord : int
        y coordinate of hand landmark when pinch gesture is started.
    pinchdirectionflag : bool
        true if pinch gesture movment is along x-axis,
        otherwise false
    prevpinchlv : int
        stores quantized magnitued of prev pinch gesture displacment, from
        starting position
    pinchlv : int
        stores quantized magnitued of pinch gesture displacment, from
        starting position
    framecount : int
        stores no. of frames since 'pinchlv' is updated.
    prev_hand : tuple
        stores (x, y) coordinates of hand in previous frame.
    pinch_threshold : float
        step size for quantization of 'pinchlv'.
    """

    tx_old = 0
    ty_old = 0
    trial = True
    flag = False
    grabflag = False
    pinchmajorflag = False
    pinchminorflag = False
    pinchstartxcoord = None
    pinchstartycoord = None
    pinchdirectionflag = None
    prevpinchlv = 0
    pinchlv = 0
    framecount = 0
    prev_hand = None
    pinch_threshold = 0.3

    def __int__(self):
        print("Controller")

    def getpinchylv(hand_result):
        """returns distance beween starting pinch y coord and current hand position y coord."""
        dist = round((Niyantrana.pinchstartycoord - hand_result.landmark[8].y) * 10, 1)
        return dist

    def getpinchxlv(hand_result):
        """returns distance beween starting pinch x coord and current hand position x coord."""
        dist = round((hand_result.landmark[8].x - Niyantrana.pinchstartxcoord) * 10, 1)
        return dist

    def changesystembrightness():
        """sets system brightness based on 'Controller.pinchlv'."""
        print("Changing brightness")
        currentBrightnessLv = sbc.get_brightness(display=0) / 100.0
        currentBrightnessLv += Niyantrana.pinchlv / 50.0
        if currentBrightnessLv > 1.0:
            currentBrightnessLv = 1.0
        elif currentBrightnessLv < 0.0:
            currentBrightnessLv = 0.0
        sbc.fade_brightness(int(100 * currentBrightnessLv), start=sbc.get_brightness(display=0))

    def changesystemvolume():
        """sets system volume based on 'Controller.pinchlv'."""
        print("Changing volume")
        pyautogui.scroll(120 if Niyantrana.pinchlv > 0.0 else -120)
        print("Scroll Vertically")
        # devices = AudioUtilities.GetSpeakers()
        # interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        # volume = cast(interface, POINTER(IAudioEndpointVolume))
        # currentVolumeLv = volume.GetMasterVolumeLevelScalar()
        # currentVolumeLv += Controller.pinchlv / 50.0
        # if currentVolumeLv > 1.0:
        #     currentVolumeLv = 1.0
        # elif currentVolumeLv < 0.0:
        #     currentVolumeLv = 0.0
        # volume.SetMasterVolumeLevelScalar(currentVolumeLv, None)

    def scrollVertical():
        """scrolls on screen vertically."""
        pyautogui.scroll(120 if Niyantrana.pinchlv > 0.0 else -120)
        print("Scroll Vertically")

    def scrollHorizontal():
        """scrolls on screen horizontally."""
        pyautogui.keyDown('option')
        pyautogui.scroll(-120 if Niyantrana.pinchlv > 0.0 else 120)
        pyautogui.keyUp('option')

    # Locate Hand to get Cursor Position
    # Stabilize cursor by Dampening
    def get_position(hand_result):
        """
        returns coordinates of current hand position.

        Locates hand to get cursor position also stabilize cursor by
        dampening jerky motion of hand.

        Returns
        -------
        tuple(float, float)
        """
        point = 9
        position = [hand_result.landmark[point].x, hand_result.landmark[point].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)
        if Niyantrana.prev_hand is None:
            Niyantrana.prev_hand = x, y
        delta_x = x - Niyantrana.prev_hand[0]
        delta_y = y - Niyantrana.prev_hand[1]

        distsq = delta_x ** 2 + delta_y ** 2
        ratio = 1
        Niyantrana.prev_hand = [x, y]

        if distsq <= 25:
            ratio = 0
        elif distsq <= 900:
            ratio = 0.07 * (distsq ** (1 / 2))
        else:
            ratio = 2.1
        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio
        return (x, y)

    def pinch_control_init(hand_result):
        """Initializes attributes for pinch gesture."""
        Niyantrana.pinchstartxcoord = hand_result.landmark[8].x
        Niyantrana.pinchstartycoord = hand_result.landmark[8].y
        Niyantrana.pinchlv = 0
        Niyantrana.prevpinchlv = 0
        Niyantrana.framecount = 0

    # Hold final position for 5 frames to change status
    def pinch_control(hand_result, controlHorizontal, controlVertical):
        """
        calls 'controlHorizontal' or 'controlVertical' based on pinch flags,
        'framecount' and sets 'pinchlv'.

        Parameters
        ----------
        hand_result : Object
            Landmarks obtained from mediapipe.
        controlHorizontal : callback function assosiated with horizontal
            pinch gesture.
        controlVertical : callback function assosiated with vertical
            pinch gesture.

        Returns
        -------
        None
        """
        if Niyantrana.framecount == 5:
            Niyantrana.framecount = 0
            Niyantrana.pinchlv = Niyantrana.prevpinchlv

            if Niyantrana.pinchdirectionflag == True:
                controlHorizontal()  # x

            elif Niyantrana.pinchdirectionflag == False:
                controlVertical()  # y

        lvx = Niyantrana.getpinchxlv(hand_result)
        lvy = Niyantrana.getpinchylv(hand_result)

        if abs(lvy) > abs(lvx) and abs(lvy) > Niyantrana.pinch_threshold:
            Niyantrana.pinchdirectionflag = False
            if abs(Niyantrana.prevpinchlv - lvy) < Niyantrana.pinch_threshold:
                Niyantrana.framecount += 1
            else:
                Niyantrana.prevpinchlv = lvy
                Niyantrana.framecount = 0

        elif abs(lvx) > Niyantrana.pinch_threshold:
            Niyantrana.pinchdirectionflag = True
            if abs(Niyantrana.prevpinchlv - lvx) < Niyantrana.pinch_threshold:
                Niyantrana.framecount += 1
            else:
                Niyantrana.prevpinchlv = lvx
                Niyantrana.framecount = 0

    def handle_controls(gesture, hand_result):
        """Impliments all gesture functionality."""
        x, y = None, None
        if gesture != Gest.PALM:
            x, y = Niyantrana.get_position(hand_result)

        # flag reset
        if gesture != Gest.FIST and Niyantrana.grabflag:
            Niyantrana.grabflag = False
            pyautogui.mouseUp(button="left")

        if gesture != Gest.PINCH_MAJOR and Niyantrana.pinchmajorflag:
            Niyantrana.pinchmajorflag = False

        if gesture != Gest.PINCH_MINOR and Niyantrana.pinchminorflag:
            Niyantrana.pinchminorflag = False

        # implementation
        if gesture == Gest.V_GEST:
            Niyantrana.flag = True
            pyautogui.moveTo(x, y, duration=0.1)

        elif gesture == Gest.FIST:
            if not Niyantrana.grabflag:
                Niyantrana.grabflag = True
                pyautogui.mouseDown(button="left")
            pyautogui.moveTo(x, y, duration=0.1)
            print("Trying to Drag")

        elif gesture == Gest.MID and Niyantrana.flag:
            pyautogui.click()
            Niyantrana.flag = False

        elif gesture == Gest.INDEX and Niyantrana.flag:
            pyautogui.click(button='right')
            Niyantrana.flag = False

        elif gesture == Gest.TWO_FINGER_CLOSED and Niyantrana.flag:
            print("drag");
            pyautogui.doubleClick()
            Niyantrana.flag = False

        elif gesture == Gest.PINCH_MINOR:
            if Niyantrana.pinchminorflag == False:
                Niyantrana.pinch_control_init(hand_result)
                Niyantrana.pinchminorflag = True
            Niyantrana.pinch_control(hand_result, Niyantrana.scrollHorizontal, Niyantrana.scrollVertical)

        elif gesture == Gest.PINCH_MAJOR:
            if Niyantrana.pinchmajorflag == False:
                Niyantrana.pinch_control_init(hand_result)
                Niyantrana.pinchmajorflag = True
            # Niyantrana.pinch_control(hand_result, Niyantrana.changesystembrightness, Niyantrana.changesystemvolume)
            Niyantrana.pinch_control(hand_result, Niyantrana.scrollHorizontal, Niyantrana.scrollVertical)