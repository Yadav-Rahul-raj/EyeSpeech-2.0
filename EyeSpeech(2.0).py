# This project is created on Jetson-Nano kit(4 Gb)

# Write text with the help of eye detection and at last converting text in Audio form

# Disable to create __pycache__
import sys
sys.dont_write_bytecode = True

# importing library
import os
import time
import cv2
import numpy as np
import dlib
from math import hypot
import pyglet
import time
from gtts import gTTS


#Blueprint of EyeSpeech
class EyeSpeech:
    #constructor 
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.board = np.zeros((500, 600), np.uint8)
        self.board[:] = 255
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.keyboard = np.zeros((600, 300, 3), np.uint8)
        self.keys_set_1 = {0: "Hungry", 1: "Thirsty", 2: "Bath", 3: "Washroom", 4: "Sleep", 5: "EXT"}
        self.sound = pyglet.media.load("sound.wav", streaming=False)
        self.frames = 0
        self.letter_index = 0
        self.blinking_frames = 0
        self.frames_to_blink = 6
        self.frames_active_letter = 5
        self.text = ""
        self.select_keyboard_menu = False
        self.keyboard_selection_frames = 0
        self.font = cv2.FONT_HERSHEY_PLAIN

    def draw_letters(self, letter_index, text, letter_light):
        # Keys
        if letter_index == 0:
            x = 0
            y = 0
        elif letter_index == 1:
            x = 00
            y = 100
        elif letter_index == 2:
            x = 00
            y = 200
        elif letter_index == 3:
            x = 00
            y = 300
        elif letter_index == 4:
            x = 00
            y = 400
        elif letter_index == 5:
            x = 00
            y = 500

        width = 300  # for key
        height = 100  # for key
        th = 3  # thickness

        # Text settings
        font_letter = cv2.FONT_HERSHEY_PLAIN
        font_scale = 2
        font_th = 4
        text_size = cv2.getTextSize(text, font_letter, font_scale, font_th)[0]
        width_text, height_text = text_size[0], text_size[1]
        text_x = int((width - width_text) / 2) + x  ## 2 is for the directoin of the text in the key
        text_y = int((height + height_text) / 2) + y

        if letter_light is True:
            cv2.rectangle(self.keyboard, (x + th, y + th), (x + width - th, y + height - th), (255, 0, 255), -1)
            cv2.putText(self.keyboard, text, (text_x, text_y), font_letter, font_scale, (51, 51, 51), font_th)
        else:
            cv2.rectangle(self.keyboard, (x + th, y + th), (x + width - th, y + height - th), (51, 51, 51), -1)
            cv2.putText(self.keyboard, text, (text_x, text_y), font_letter, font_scale, (255, 0, 255), font_th)

    def midpoint(self,p1 ,p2):
        return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)
    
    def get_blinking_ratio(self,eye_points, facial_landmarks):
        left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
        right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
        center_top = self.midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
        center_bottom = self.midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

        hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
        ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

        ratio = hor_line_lenght / ver_line_lenght
        return ratio

    def eyes_contour_points(self,facial_landmarks):
        left_eye = []
        right_eye = []
        for n in range(36, 42):
            x = facial_landmarks.part(n).x
            y = facial_landmarks.part(n).y
            left_eye.append([x, y])
        for n in range(42, 48):
            x = facial_landmarks.part(n).x
            y = facial_landmarks.part(n).y
            right_eye.append([x, y])
        left_eye = np.array(left_eye, np.int32)
        right_eye = np.array(right_eye, np.int32)
        return left_eye, right_eye
    
    # converting the text into audio
    def txtmp3(self,text_to_convert):
        fw = open("EyeSpeech.txt","w")
        fw.write(text_to_convert)
        fw.flush()
        language = 'en'
        myobj = gTTS(text=text_to_convert, lang=language, slow=False)
        myobj.save("EyeAudio.mp3")
        count =0
        while(count <3):
            wel = pyglet.media.load("EyeAudio.mp3", streaming=False)
            wel.play()
            time.sleep(2)
            count+=1

#Driver code
Eye = EyeSpeech()
while True:
    
    ret, frame = Eye.cap.read()
    if not ret:
        print("Failed to read frame from camera.")
        break
    rows, cols, _ = frame.shape
    Eye.keyboard[:] = (26,26,26)
    Eye.frames +=1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    frame[rows - 50: rows, 0: cols] = (255, 255, 255)

    keys_set = Eye.keys_set_1
    # print(keys_set)

    active_letter = keys_set[Eye.letter_index]
    # print(active_letter)

    faces = Eye.detector(gray)

    for face in faces:
        landmarks = Eye.predictor(gray, face)

        left_eye, right_eye = Eye.eyes_contour_points(landmarks)

        left_eye_ratio = Eye.get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = Eye.get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        # Eyes color
        cv2.polylines(frame, [left_eye], True, (0, 0, 255), 2)
        cv2.polylines(frame, [right_eye], True, (0, 0, 255), 2)

        # Detect the blinking to select the key that is lighting up
        if blinking_ratio > 4:
            Eye.blinking_frames += 1
            Eye.frames -= 1

            # Show green eyes when closed
            cv2.polylines(frame, [left_eye], True, (0, 255, 0), 2)
            cv2.polylines(frame, [right_eye], True, (0, 255, 0), 2)

            # Typing letter
            if Eye.blinking_frames == Eye.frames_to_blink:
                if active_letter != "EXT":
                    Eye.text += active_letter
                if active_letter == "EXT":
                    Eye.txtmp3(Eye.text)
                    Eye.cap.release()
                    cv2.destroyAllWindows()
                Eye.sound.play()
                select_keyboard_menu = False
        else:
            Eye.blinking_frames = 0


    # Display letters on the keyboard
    if Eye.select_keyboard_menu is False:
        if Eye.frames == Eye.frames_active_letter:
            Eye.letter_index += 1
            # print(Eye.letter_index)
            Eye.frames = 0
        if Eye.letter_index == 6:
            Eye.letter_index = 0
        for i in range(6):
            # print("Yes")
            if i == Eye.letter_index:
                light = True
                # print("No")
            else:
                light = False
            Eye.draw_letters(i, keys_set[i], light)

    # Show the text we're writing on the board
    cv2.putText(Eye.board, Eye.text, (0, 30), Eye.font, 2, 0, 2)

    # Blinking loading bar
    percentage_blinking = Eye.blinking_frames / Eye.frames_to_blink
    loading_x = int(cols * percentage_blinking)
    cv2.rectangle(frame, (0, rows - 50), (loading_x, rows), (51, 51, 51), -1)

    #pop up windows for camera,keyboard, board
    cv2.imshow("Camera", frame)
    cv2.imshow("Virtual keyboard", Eye.keyboard)
    cv2.imshow("Board", Eye.board)

    #If Enter key is pressed then the program will be terminated
    key = cv2.waitKey(1)
    if key == 27:
        break
    

#releasing camera and destroying all windows        
Eye.cap.release()
cv2.destroyAllWindows()

#function to convert text to mp3
Eye.txtmp3(Eye.text)