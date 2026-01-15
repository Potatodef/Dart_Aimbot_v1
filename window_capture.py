import cv2
import numpy as np
import pyautogui
from time import time,sleep
import win32gui, win32ui, win32con
import math



hwnd = win32gui.FindWindow(None, "Legends Of Idleon")
win32gui.MoveWindow(hwnd,0,0,960,575,True)
window_rect = win32gui.GetWindowRect(hwnd)
win32gui.SetForegroundWindow(hwnd)
w = window_rect[2]-window_rect[0]
h = window_rect[3]-window_rect[1] 

def capture():
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)

    #save screenshot in variable by converting bitmap to opencv img
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h,w,4)
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    return img

# given opencv img, returns list of 3 values of current x, y, angle
def coord(img):
    frame_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    frame_threshold_tail = cv2.inRange(frame_hsv,(18,56,43),(28,255,255))  # LH,LS,LV  HH,HS,HV
    frame_threshold_tip = cv2.inRange(frame_hsv,(0,0,17),(180,8,241))
    masked_roi = np.zeros(frame_threshold_tail.shape,dtype = np.uint8)
    cv2.rectangle(masked_roi,(100,150),(1030,600),255,-1)
    frame_threshold_tail = cv2.bitwise_and(frame_threshold_tail,frame_threshold_tail,mask=masked_roi)
    frame_threshold_tip = cv2.bitwise_and(frame_threshold_tip,frame_threshold_tip,mask=masked_roi)
    contours_tail, _ = cv2.findContours(frame_threshold_tail,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours_tip, _ = cv2.findContours(frame_threshold_tip,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cx_tip=0
    cy_tip=0
    cx_tail=0
    cy_tail =0
    angle = 0
    for cnt in contours_tip: 
        if cv2.contourArea(cnt) > 110: 
            cv2.drawContours(screenshot,cnt,-1,(255,0,0),5)

            M = cv2.moments(cnt)
            cx_tip = (M['m10']/ M['m00'])
            cy_tip = (M['m01']/ M['m00'])

    for cnt in contours_tail: 
        if cv2.contourArea(cnt) > 50:
            cv2.drawContours(screenshot,cnt,-1,(0,255,0),5)  
            M = cv2.moments(cnt)
            cx_tail = (M['m10']/ M['m00'])
            cy_tail = (M['m01']/ M['m00']) 
    if (cx_tail !=0):
        angle = math.atan(-(cy_tip-cy_tail)/(cx_tip-cx_tail))

    coordinates_angle = [(cx_tail+cx_tip)/2,(cy_tail+cy_tip)/2,angle]
    return coordinates_angle

fired = False
second_fired_calc = False
second_fired = False
x_list = []
y_list = []
coord_list = []
diff = 0
a =0
b=0
prev_angle = 0
sa = 0
tracking = False
avg_diff = []
avg_a = []
slept = False
while 1:
    screenshot = capture() 
    screenshot = cv2.resize(screenshot,(1200,720))
    current_x, current_y, current_angle = coord(screenshot)
    cv2.imshow("frame",screenshot)
    if (prev_angle == 0):
        prev_angle = current_angle
        continue
    if (fired or tracking):
        if (not coord_list):
            pass
        elif (current_x < coord_list[-1][0]): # dart is out of ROI and is gonna go back to start
            fired = False
            tracking = False
            second_fired_calc = True
            continue
        coord_list.append((current_x,-1*current_y))
    elif (second_fired_calc): # atp dart is either out of ROI or at start
        if (current_x == 0):
            continue
        else: # dart is at the new start
            coord_list = list(dict.fromkeys(coord_list))
            for i in coord_list:
                x_list.append(i[0])
                y_list.append(i[1])
            x_coord = np.array(x_list)
            y_coord = np.array(y_list)
            x_coord -= x_coord[0]
            y_coord -= y_coord[0]
            a,b,c = np.polyfit(x_coord,y_coord,2)
            x_list = []
            y_list = []
            coord_list =[]
            avg_a.append(a)
            #since its swinging downwards actual < measured
            diff = sa - math.atan(b)
            avg_diff.append(diff)
            second_fired_calc = False
            second_fired = True
    elif (tracking):
        if (not x_list): #empty
            coord_list.append((current_x,current_y))

    elif (second_fired):
        a = sum(avg_a)/len(avg_a)
        diff = sum(avg_diff)/len(avg_diff)
        xf = 1090 - current_x
        yf1 = -410 - (-1*current_y) 
        yf2 = -420 - (-1*current_y)
        b1 = math.atan((yf1 - a*(xf**2))/xf)
        b2 = math.atan((yf2 - a*(xf**2))/xf)
        if (not slept):
            slept = True
            sleep(2)
        if (current_angle < b1+diff and current_angle > b2+diff and prev_angle > current_angle):
            pyautogui.click(400,400)
            sa = current_angle
            tracking = True
            slept = False

            
    elif (current_angle <0.4668133  and current_angle > 0.449183 and prev_angle > current_angle): 
        pyautogui.click(400,400)
        fired = True
        sa = current_angle
    prev_angle = current_angle
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        cv2.destroyAllWindows()
        break
