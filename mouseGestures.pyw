# %%
from pynput import mouse
import time
import keyboard as kb
import pyautogui as km
import ctypes
import numpy as np
import math
from pynput.keyboard import Key,Controller
keyboardController = Controller()

km.FAILSAFE = False
km.PAUSE = 0

# %%
def getNumLockState():
    hllDll = ctypes.WinDLL ("User32.dll")
    VK_NUMLOCK = 0x90
    return hllDll.GetKeyState(VK_NUMLOCK)

# %%
def toggle_numlock():
    km.press("numlock")

# %%
lastX, lastY = 1,1
isPaused = False
isAltDown = False, # manages only those alt events which are triggered/modified in this script
xLen = 1920
yLen = 1080
taskBarLength = 60
chromeTabBarLength = 40

# %%
lastTime = 0
startTime = time.time() # used for 10sec termination safety

def onScroll(x,y, dx, dy):
    global lastX, lastY, isPaused, lastTime, isAltDown, xLen, yLen, taskBarLength, chromeTabBarLength

    
    if(dy>0): dy=1
    elif(dy<0): dy=-1
    
    if(dy==-1): # wheel down
        wheelDown = True
        wheelUp = False
    else: # wheel up
        wheelDown = False
        wheelUp = True

    # fail safe option
    if(False and time.time()-startTime > 10):
        return False
    
    # spam checking
    if(time.time() - lastTime < 0.2):
        isSpamEvent = True
    else:
        isSpamEvent = False


    # keep x and y withing limits
    x=min(max(x,0),xLen-1)
    y=min(max(y,0),yLen-1)
    
    lastTime = time.time()
    lastX, lastY = x, y
    
    
    if(x<10 and y<10): # top left corner
        if(isSpamEvent):
            return
        
        shouldToglePause = kb.is_pressed("win")
        shouldTerminate = kb.is_pressed('win')   and   kb.is_pressed('alt')
        if(shouldTerminate):
            return False
        elif(shouldToglePause):
            isPaused = not(isPaused)
            return
        elif(isPaused):
            return
        
        if(wheelUp or wheelDown):
            km.hotkey('win','tab')

    elif(isPaused):
        return 
    
    elif(0.1<=x/xLen<=0.9 and y>=yLen-taskBarLength): # mid bottom, taskbar        
        if(wheelUp):
            if(isAltDown):
                km.hotkey('shift','tab')
            elif(not(isSpamEvent)):
                km.hotkey('alt', 'tab')

        elif(wheelDown):
            if(not isAltDown):
                km.keyDown('alt')
                isAltDown = True
            km.hotkey('tab')


    elif(x<10 and 0.1<=y/yLen<=0.5): # upper of leftside
        if(isSpamEvent):
            return
        if(wheelUp):
            km.hotkey('alt','left')
        elif(wheelDown):
            km.hotkey('alt','right')

    elif(y<chromeTabBarLength and 0.1<=x/xLen<=0.9): # mid of upperside, chrome tab bar
        if(wheelUp):
            km.hotkey('ctrl','shift','tab')
        elif(wheelDown):
            km.hotkey('ctrl','tab')

    elif(x>xLen-1-10 and 0.1<=y/yLen<=0.5): # upper rightside
        ...

    elif(x<10 and 0.5<y/yLen<=0.90): # lower leftside
        ...
        
        
    else: # all other cases
        if(isAltDown):
            km.keyUp('alt')
            isAltDown = False

    # } end if

# } end def

def emptyFunction(*arr):
    return

# %%
rightDownTime = -1
isRightClickDown = False
centralKnob = dict()
centralKnob['center'] = [xLen//2, yLen//2]
centralKnob['isActive'] = False
centralKnob['initialAngle'] = 0
centralKnob['lastAngle'] = 0
centralKnob['value'] = 0
centralKnob['lastDelValue'] = 0
centralKnob['unflushedDelValue'] = 0

def onClick(x,y,button,pressed):
    global isAltDown, rightDownTime, isRightClickDown, centralKnob, isPaused
    if(isPaused):
        return
    
    if(isAltDown and button == mouse.Button.middle   and   pressed==True):
        km.keyUp('alt')
        isAltDown=False
    elif(button == mouse.Button.right):
        if(pressed == True):
            rightDownTime = time.time()
            isRightClickDown = True
        elif(pressed == False):
            rightDownTime = -1
            isRightClickDown = False
            centralKnob['isActive'] = False

# %%
isNumLockHanging = False
clickHoldThreshold = 0.25
isNumpadFullyOn = True

def onMove(x,y):
    global isAltDown, xLen, yLen, taskBarLength, isPaused, isNumLockHanging, isRightClickDown, clickHoldThreshold, centralKnob, isNumpadFullyOn
    
    if(isPaused):
        return
    
    if(y<yLen-taskBarLength): # out of taskbar
        if(isAltDown):
            km.keyUp('alt')
            isAltDown = False

    if(y<40 and 0.1<=x/xLen<=0.9): # mid of upperside, chrome tab bar
        if(False and not isNumpadFullyOn):
            kb.unremap_key('7')
            kb.unremap_key('1')
            isNumpadFullyOn = True

        
    if(y>40 and 0.1<=x/xLen<=0.9): # out of "mid of upperside, chrome tab bar"
        if(False and isNumpadFullyOn):
            kb.remap_key('7','home')
            kb.remap_key('1', 'end')
            isNumpadFullyOn = False

                
    if(True): # always execute
        if(isRightClickDown and (time.time()-rightDownTime)>=clickHoldThreshold): # if right click is click-and-hold
            center = centralKnob['center']
            if(not centralKnob['isActive']):
                centralKnob['isActive'] = True

                centralKnob['initialAngle'] = math.degrees( math.atan2(y-center[1], x-center[0]) )
                centralKnob['lastAngle'] = centralKnob['initialAngle']
                centralKnob['value'] = 0
                centralKnob['lastDelValue'] = 0
                centralKnob['unflushedDelValue'] = 0

            else: # if was already active
                delTheta = (math.degrees( math.atan2(y-center[1], x-center[0]) ) - centralKnob['lastAngle'] +360+360)%360
                if(delTheta>180):
                    delTheta -= 360
                centralKnob['value'] += delTheta
                centralKnob['lastDelValue'] = delTheta
                centralKnob['unflushedDelValue'] += delTheta
                centralKnob['lastAngle'] = math.degrees( math.atan2(y-center[1], x-center[0]) )

                if(centralKnob['unflushedDelValue'] >= 30):
                    keyboardController.press(Key.media_volume_up)
                    keyboardController.release(Key.media_volume_up)
                    centralKnob['unflushedDelValue'] -= 30
                elif(centralKnob['unflushedDelValue'] <= -30):
                    keyboardController.press(Key.media_volume_down)
                    keyboardController.release(Key.media_volume_down)
                    centralKnob['unflushedDelValue'] += 30

            

# %%
listener = mouse.Listener(
    on_move=onMove,
    on_click=onClick,
    on_scroll=onScroll)
listener.start()
listener.join()

# %%



