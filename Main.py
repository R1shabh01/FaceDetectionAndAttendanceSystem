import csv
import json
import os
from pathlib import Path
import pickle
import shutil
import time
import tkinter as tk
from datetime import date, datetime
from tkinter.filedialog import askopenfile
from csv import writer
import cvzone
import face_recognition
import numpy as np
import pandas as pd
import requests
import cv2
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager,Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from plyer import filechooser
from kivy.uix.image import Image
from kivy.clock import Clock
from firebase_admin import storage
from kivymd.uix.boxlayout import MDBoxLayout
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


KV= """
ScreenManager:
    Main_screen:
    Student_entry:
        id:sc2
    Frasscreen:
        id:sc3
    Camerascreen:

<Main_screen>:
    name:"main"
    MDScreen:
        BoxLayout:
            orientation: 'vertical'
            MDTopAppBar:
                title: "Attendance Management System"
                md_bg_color: app.theme_cls.primary_color
                elevation: 5
                left_action_items:[["school", lambda x: x]]
            MDFloatLayout:
                orientation:"horizontal"
                MDFloatingActionButton:
                    icon: "resources/icons/add.png"
                    elevation: 0
                    md_bg_color: app.theme_cls.primary_color
                    pos_hint: {"center_x": .2, "center_y": .6}
                    size_hint: .2,.2
                    icon_size:"150dp"
                    on_release: root.manager.current = "student_entry"
                    md_bg_color: 1, 1, 1, 1
    
                    
                MDFloatingActionButton:
                    icon: "resources/icons/view.png"
                    elevation: 0
                    opposite_color: True
                    md_bg_color: app.theme_cls.primary_color
                    pos_hint: {"center_x": .5, "center_y": .6}
                    icon_size:"150dp"
                    size_hint: .2,.2
    
                    on_release: root.manager.current = "frasscreen"
                    md_bg_color: 1, 1, 1, 1
                        
                MDFloatingActionButton:
                    icon: "resources/icons/exit.png"
                    elevation: 0
                    opposite_color: True
                    md_bg_color: app.theme_cls.primary_color
                    pos_hint: {"center_x": .8, "center_y": .6}
                    icon_size:"150dp"
                    size_hint: .2, .2
                    md_bg_color: 1, 1, 1, 1
    
                    on_release: app.Exit()
                
            
<Student_entry>:
    name:"student_entry"
    MDScreen:
        MDBoxLayout:
            orientation:"vertical"
            md_bg_color:app.theme_cls.primary_color
            MDTopAppBar:
                title: "   Add Student"
                md_bg_color: app.theme_cls.primary_color
                elevation:5
                font_name:"resources/font/Eczar-Bold.ttf"
                left_action_items:[["keyboard-backspace", lambda x:app.return_to_main()]]
            MDFloatLayout:
                pos_hint:{"center_x":.5,"center_y":.45}
                size_hint:1,.8
                md_bg_color:1,1,1,1        
                MDTextField:
                    hint_text:"STUDENT NAME"
                    id:name
                    helper_text: "Full Name And Use _ for space"
                    helper_text_mode: "on_focus"
                    pos_hint:{"center_x":.3,"center_y":.8}
                    size_hint_x:None
                    fill_color:1,1,1,1
                    font_size:"20dp"
                    size_hint:.35,.15
                    font_name:"resources/font/Eczar-Regular.ttf"
                MDTextField:
                    hint_text:"DEPARTMENT"
                    id:dept
                    helper_text: "Use _ for space"
                    pos_hint:{"center_x":.3,"center_y":.6}
                    size_hint_x:None
                    font_size:"20dp"
                    size_hint:.35,.15
                    font_name:"resources/font/Eczar-Regular.ttf"
                MDTextField:
                    hint_text:"SEMESTER"
                    id:year
                    helper_text: "Semester with Your Section"
                    pos_hint:{"center_x":.7,"center_y":.6}
                    size_hint_x:None
                    font_size:"20dp"
                    size_hint:.35,.15
                    font_name:"resources/font/Eczar-Regular.ttf"
                MDTextField:
                    hint_text:"ENROLLMENT NUMBER"
                    id:rollno
                    pos_hint:{"center_x":.7,"center_y":.8}
                    size_hint_x:None
                    font_size:"20dp"
                    size_hint:.35,.15
                    font_name:"resources/font/Eczar-Regular.ttf"
                MDTextField:
                    hint_text:"GENDER"
                    id:gender
                    pos_hint:{"center_x":.7,"center_y":.4}
                    size_hint_x:None
                    font_size:"20dp"
                    helper_text_mode: "on_focus"
                    helper_text: "Enter M for Male And F for Female"
                    size_hint:.35,.15
                    font_name:"resources/font/Eczar-Regular.ttf"
                
                MDRaisedButton:
                    text: "UPLOAD IMAGE"
                    md_bg_color:app.theme_cls.primary_color
                    size_hint:.35,.06
                    font_size:"20dp"
                    pos_hint:{"center_x":.3,"center_y":.4}
                    font_name:"resources/font/Eczar-SemiBold.ttf"
                    on_release:
                        app.upload_img()
                MDLabel:
                    id:uploaded_path
                    text:""
                    pos_hint:{"center_x":.3,"center_y":.32}
                    size_hint:.35,.05
                    font_size:"15dp"
                    theme_text_color:"Custom"
                    text_color:0,1,0,1
                MDRaisedButton:
                    text: "CAPTURE IMAGE"
                    md_bg_color:app.theme_cls.primary_color
                    size_hint:.35,.05
                    font_size:"20dp"
                    pos_hint:{"center_x":.3,"center_y":.2}
                    font_name:"resources/font/Eczar-SemiBold.ttf"
                    on_release:app.open_camera()
                MDRaisedButton:
                    text: "SAVE"
                    md_bg_color:app.theme_cls.primary_color
                    size_hint:.20,.05
                    font_size:"20dp"
                    pos_hint:{"center_x":.85,"center_y":.2}
                    font_name:"resources/font/Eczar-SemiBold.ttf"
                    on_release:
                        app.add_to_db()
                MDRaisedButton:
                    text: "Train"
                    md_bg_color:app.theme_cls.primary_color
                    size_hint:.20,.05
                    font_size:"20dp"
                    pos_hint:{"center_x":.62,"center_y":.2}
                    font_name:"resources/font/Eczar-SemiBold.ttf"
                    on_release:
                        app.train_img()
                MDLabel:
                    id:train
                    text:""
                    pos_hint:{"center_x":.62,"center_y":.12}
                    size_hint:.35,.05
                    font_size:"15dp"
                    theme_text_color:"Custom"
                    text_color:0,1,0,1

<Frasscreen>:
    name:"frasscreen"
    MDScreen:
        MDBoxLayout:
            orientation:"vertical"
            MDTopAppBar:
                size_hint:1,.3
                title: "   Mark Your Attendance"
                md_bg_color: app.theme_cls.primary_color
                elevation: 5
                left_action_items:[["keyboard-backspace", lambda x:app.return_to_main()]]

            MDBoxLayout:
                MDFloatingActionButton:
                    icon: "resources/icons/attendance.png"
                    elevation: 0
                    md_bg_color: app.theme_cls.primary_color
                    pos_hint: {"center_x": .2, "center_y": .4}
                    size_hint: .3,.3
                    icon_size:"250dp"
                    on_release:
                        app.Start_Attendance()
                    md_bg_color: 1, 1, 1, 1
                MDFloatingActionButton:
                    icon: "resources/icons/Download CSV.png"
                    elevation: 0
                    md_bg_color: app.theme_cls.primary_color
                    pos_hint: {"center_x": .2, "center_y": .4}
                    size_hint: .3,.3
                    icon_size:"280dp"
                    on_release:
                        app.save_attendance()
                    md_bg_color: 1, 1, 1, 1
                
            MDBoxLayout:
                MDLabel:
                    id:marked
                    text:""
                    pos_hint:{"center_x":.62,"center_y":.12}
                    size_hint:.35,.05
                    font_size:"25dp"
                    theme_text_color:"Custom"
                    text_color:0,1,0,1
            
            
                    
    
    
                                      
<Camerascreen>:
    name:"camerascreen"
    MDScreen:
        MDBoxLayout:
            orientation:"vertical"
            MDTopAppBar:
                size_hint:1,.3
                title: "  Take Your Photo"
                md_bg_color: app.theme_cls.primary_color
                elevation: 5
                left_action_items:[["keyboard-backspace", lambda x:app.return_to_Stu()]]
            MDBoxLayout:
                id:cambox
            MDBoxLayout:
                id:cambutton
                spacing:"5dp"
                size_hint:.1,0
                height:40
                pos_hint:{"center_x":.5}
                MDFloatingActionButton:
                    icon: "camera"
                    user_font_size:"64dp"
                    pos_hint:{"center_x":.5}
                    elevation_normal: 12
                    md_bg_color: app.theme_cls.primary_color
                    on_release:
                        root.capture()
                        app.return_to_Stu()
                        
            MDBoxLayout:
                size_hint_y:0
                height:15
                
        
    
    
    
 """

#Image:
#                id:uploaded_img


class Frasscreen(MDScreen):
    pass





class Camerascreen(MDScreen):
    def on_pre_enter(self):
        self.camera = Capture_camera(size_hint=(1,.9))
        self.ids["cambox"].add_widget(self.camera)

    def capture(self):
        self.camera.capture_img()
        self.camera.stop_camera()

class Capture_camera(Image):

    def __init__(self,**kwargs):
        super(Capture_camera,self).__init__(**kwargs)
        self.record = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update,0.01)

    def update(self,dt):
        ret, self.frame = self.record.read()
        buf = cv2.flip(self.frame,0).tobytes()
        texture = Texture.create(size=(self.frame.shape[1],self.frame.shape[0]),colorfmt="bgr")
        texture.blit_buffer(buf,colorfmt="bgr",bufferfmt="ubyte")
        self.texture = texture
    def stop_camera(self):
        self.record.release()
        Clock.schedule(self.update())

    def capture_img(self):
        timestr = time.strftime("%Y%m%d_%H%M%S")
        id = MDApp.get_running_app().root.ids.sc2.ids["rollno"].text
        print(id)
        name = MDApp.get_running_app().root.ids.sc2.ids["name"].text
        print(name)
        cv2.imwrite(f"resources/images/{id}_{name}.png".format(timestr),self.frame)
        return f"resources/images/{id}_{name}.png".format(timestr)





class Student_entry(MDScreen):
    pass

class Main_screen(MDScreen):
    pass

class ScreenManagement (ScreenManager):
    pass

class FaceDetection(MDApp):
    cred = credentials.Certificate("fras-e9b16-firebase-adminsdk-e9hf8-c88cab8e3e.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://fras-e9b16-default-rtdb.firebaseio.com/",
        "storageBucket": "fras-e9b16.appspot.com"})

    def build(self):
        screen = Builder.load_string(KV)
        self.shud_we_train = False


        return screen


    def save_attendance(self):

        todays_date = date.today()
        downloads_path = str(Path.home()/"Downloads")
        dt = pd.read_csv(fr"resources/AttendenceRegister/{todays_date}.csv")
        print(dt)
        dt.to_csv(fr'{downloads_path}\{todays_date}.csv',index = False)
        val = []
        for i, row in dt.iterrows():
            for r in row:
                val.append(r)
        ref = db.reference("Attendance")
        data = {val[3]:{"rollno": val[1], "Name": val[0],"Time":val[2],"Department":val[4],"Semester":val[5]}}
        for key, value in data.items():
            ref.child(key).set(value)




    def upload_img(self):
        files = [('text file', '*.png')]
        root = tk.Tk()
        root.withdraw()
        source = askopenfile()
        if source == None:
            self.root.screens[1].ids.uploaded_path.text_color = 1, 0, 0, 1
            self.root.ids.screens[1].uploaded_path.text = "Failed to Upload"
        else:
            source = source.name
            l = source.split('/')
            folder_type = l[len(l) - 1].split('.')[1]
            file_name = 'resources/images'
            student_rollnumber = self.root.screens[1].ids["rollno"].text
            cname = self.root.screens[1].ids["name"].text
            parent_dir = os.getcwd()
            path = os.path.join(parent_dir, file_name)
            destination = f'{path}\{student_rollnumber}_{cname}.{folder_type}'
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
            shutil.move(source, destination)
            self.shud_we_train = True
            self.root.screens[1].ids.uploaded_path.text="Uploaded Successfully"




    def Start_Attendance(self):
        if (self.shud_we_train == True):
            self.popup(title='Note', text='Please Proceed to train to update the changes')

        else:
            cur_dir = os.getcwd()
        try:
            loading = pickle.loads(open('encodings.pickle', 'rb').read())
        except FileNotFoundError:
            self.opening_dialogue_bos(title='Error', text='First Add Image and then click on Train Images')



        encodeListKnown = loading['encodings']
        classNames = loading['names']
        todays_date = date.today()

        def giving_heading_to_csv():
            todays_date = date.today()
            # with open(f'C:/Users/user/PycharmProjects/deletesoon/AttendenceRegister/{todays_date}.csv', 'w+') as f:
            with open(fr'{cur_dir}\resources\AttendenceRegister\{todays_date}.csv', 'w+') as f:
                l = f.readline()
                if l != 'Name,Time\n':
                    csv_writer = writer(f)
                    csv_writer.writerow(['Name', 'RollNumber', 'Time','Date','Department','Semester'])

        giving_heading_to_csv()

        def markAttendance(name):
            rollnumber = name.split('_')[0]
            name = name.split('_')[1]

            with open(f'{cur_dir}/resources/AttendenceRegister/{todays_date}.csv', 'r+') as f:
                myDataList = f.readlines()
                # print(myDataList)

                self.nameList = []
                for line in myDataList:
                    entry = line.split(',')

                    self.nameList.append(entry[0])

                if name not in self.nameList:
                    now = datetime.now()
                    ref1 = db.reference(f"students/{rollnumber}").get()
                    s = str(ref1["Semester"])
                    d = str(ref1["Department"])
                    dtString = now.strftime('%H:%M:%S')
                    f.writelines(f'{name},{rollnumber},{dtString},{todays_date},{d},{s}')
                    f.write('\n')


        cap = cv2.VideoCapture(0)
        while True:
            success, img = cap.read()
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # converting each frame to smaller size for speed
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(imgS)  # list of region of interest of all faces in the current frame
            encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)  # the encodings of the current faces in frame

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown,encodeFace)  # comparing encoding btw the current frame pic and the list of uploaded images
                faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)  # will give any array showing accuracy of the current image in frame with all pictures saved
                matchIndex = np.argmin(faceDis)  # gives the index of the smallest number in the distance list, ie smallest will be matching person
                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, name, (x1 - 12, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name)
                else:
                    name = "unknown"
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, name, (x1 - 12, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow('Webcam', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def train_img(self):
        path = 'resources/images'
        images = []  # array of numpy values of images
        classNames = []  # an array of just names of ppl
        myList = os.listdir(path)
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList
        encodeListKnown = findEncodings(images)
        # print('Encoding complete')
        self.shud_we_train = False
        self.root.screens[1].ids.train.text="Done"
        data = {'encodings': encodeListKnown, 'names': classNames}
        f = open('encodings.pickle', 'wb')
        f.write(pickle.dumps(data))
        f.close()

    def open_camera(self):
        self.root.current ="camerascreen"
        """show = Capture_camera()
        camera_window = Popup(title="Camera",content="show")
        camera_window.open()"""

    def return_to_Stu(self):
        self.root.current = "student_entry"
    def return_to_main(self):
        self.root.current = "main"

    def add_to_db(self,**args):
        name = self.root.screens[1].ids["name"].text
        dept = self.root.screens[1].ids["dept"].text
        rollno = self.root.screens[1].ids["rollno"].text
        year = self.root.screens[1].ids["year"].text
        gender = self.root.screens[1].ids["gender"].text
        ref = db.reference("students")
        data = {rollno: {"Name": name, "Department": dept,
                         "Semester": year, "Gender": gender, "Attendance": ""}}
        for key, value in data.items():
            ref.child(key).set(value)

    def Exit(self):
        self.stop()






FaceDetection().run()