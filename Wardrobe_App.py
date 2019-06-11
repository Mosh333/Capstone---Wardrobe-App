# -*- coding: utf-8 -*
#For Examples, C:\Users\howla_000\AppData\Local\Programs\Python\Python37\share\kivy-examples
import numpy as np
#import cv2
import os
from os import listdir
from os.path import isfile, join
import sys
#import camera_opencv
#from win32api import GetSystemMetrics
import PIL.Image
from functools import partial
from google_images_download import google_images_download
import shutil
import time
import math
import re #for regex
#Below for sending email with attachment
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#:include kivy_opencv.kv
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
#from kivy.logger import Logger
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.textinput import TextInput
#from kivy.uix.camera import Camera
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.graphics import Color


class MyApp(App):
    #class variables
    title = "Wardrobe App with Kivy"
    size_hint = None, None #disable size inheritance from parent obj
    project_dir = "/home/pi/Magic_Mirror/Wardrobe_App/"
    height = 400#GetSystemMetrics(0)
    width = 500#GetSystemMetrics(1)
    searchShirtInput = ""
    GUI_widget = ""
    paths = None            #for use with loading images from the web
    allowed_keyboard_inputs = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n',
                               'o','p','q','r','s','t','u','v','w','x','y','z','A','B',
                               'C','D','E','F','G','H','I','J','K','L','M','N','O','P',
                               'Q','R','S','T','U','V','W','X','Y','Z','~','1','2','3',
                               '4','5','6','7','8','9','0','-','=','[',']','\\',':',"'",
                               ',','.','/','~','!','@','#','$','%','^','&','*','(',')',
                               '_','+','{','}','|',';','"','<','>','?','`',' ']
                              #actual allowed char inputs to input text field
    current_keyboard_input = []
    current_loaded_image_buttons = []
    #first index for loading image task
    #second index for ...
    #############Class Methods#######################
    def fullscreen_gui(self):
        Window.fullscreen = True
        Config.set('graphics', 'fullscreen', 'auto')
        Config.set('graphics', 'window_state', 'maximized')
        Config.write()   
        return
    
    def reset_gui(self, widget, instance):
        self.fullscreen_gui()
        #self.cameraObject.play       = False
        
        try:
            self.dispSelfieIntval.cancel()
        except:
            print("self.dispSelfieIntval event has never been scheduled!")
            
        self.clear_GUI(widget, instance)
        #print('Resetting GUI!')
        Config.set('graphics', 'fullscreen', 'auto')
        Config.write()
        #print("Configured Setting")
        self.height = 400#GetSystemMetrics(0)
        self.width = 500#GetSystemMetrics(1)
        #self.fullscreen_gui()
        #print("Issue Checkpoint 1")        
        self.boxlayout = BoxLayout()
        
        testButton = Button(text='Search Shirts',pos=(000,400), font_size=24)
        testButton2 = Button(text='Overlay Pic',pos=(220,400), font_size=24)
        testButton3 = Button(text='Send Pic',pos=(220*2,400), font_size=24)
        testButton4 = Button(text='Take Pic', pos=(220*3,400), font_size=24)
        testButton5 = Button(text='Exit',pos=(220*4,400), font_size=24)
        testButton.size = (220,200)
        testButton2.size = (220,200)
        testButton3.size = (220,200)
        testButton4.size = (220,200)
        testButton5.size = (220,200)
        #print("Issue Checkpoint 2")
##        self.cameraObject            = Camera(play=False)
##        self.cameraObject.play       = True
##        self.cameraObject.resolution = (0.9*640, 0.9*480) # Specify the resolution
##        self.cameraObject.pos = (0,400)
##        self.cameraObject.size = (0.8*640,0.8*480)
##        self.GUI_widget.add_widget(self.cameraObject)
        
        self.GUI_widget.add_widget(testButton)
        self.GUI_widget.add_widget(testButton2)
        self.GUI_widget.add_widget(testButton3)
        self.GUI_widget.add_widget(testButton4)
        self.GUI_widget.add_widget(testButton5)
        #print("Issue Checkpoint 3")
        update_GUI = partial(self.update_gui,self.GUI_widget)
        testButton.bind(on_press=update_GUI)
        testButton4.bind(on_press=update_GUI)       #possible to add additional callback functions
        testButton2.bind(on_press=update_GUI)
        testButton3.bind(on_press=update_GUI)
        reset_GUI = partial(self.reset_gui, self.GUI_widget)
        testButton5.bind(on_press=update_GUI)
        #print("Issue Checkpoint 4")
        
        try:
            self.cameraObject.play       = True
            self.GUI_widget.add_widget(self.cameraObject)
            print("Try to add camera")
        except:
            print("Failed to allocate resource for camera")
        
        return self.GUI_widget
    
    def close_app(self, instance):
        print('Closing App')
        App.get_running_app().stop()
        Window.close()
        quit()
        
    def clear_GUI(self, widget, instance): # *args
        self.cameraObject.play = False
        self.GUI_widget.remove_widget(self.cameraObject)
        print("IS it still on?", self.cameraObject)
        widget.clear_widgets()
        widget.canvas.clear()
        return
    def add_webcam(self):
        self.cameraObject            = Camera(play=False)
        self.cameraObject.play       = True
        self.cameraObject.resolution = (int(1.2*480), int(1.2*640)) # Specify the resolution
        self.cameraObject.pos = (256,1200)
        self.cameraObject.size = (int(1.2*480),int(1.2*640))
        self.GUI_widget.add_widget(self.cameraObject)
        return
    
    def update_gui(self, widget, instance):
        #All buttons call this function
        #Based on the instance name,
        #we will redirect to other appropriate functions
        #print("Button Instance Pressed", instance.text)
        if(instance.text == "Search Shirts"):
            self.reset_gui(self.GUI_widget, instance)
            shirtQuery_label = Label(text='Type T-Shirt Query Below:', pos=(850,275), font_size=30)
            self.GUI_widget.add_widget(shirtQuery_label)
            tshirt_query_input = TextInput(pos=(700,200), font_size=16)
            tshirt_query_input.size = (400,100)
            search_tshirt_button = Button(text='Search',pos=(700,100), font_size=30)
            self.searchShirtInput = tshirt_query_input
            search_tshirt_button.size = (400,100)
            widget.add_widget(tshirt_query_input)
            widget.add_widget(search_tshirt_button)
            keyboard = VKeyboard(pos=(0,0))
            widget.add_widget(keyboard)            
            #print("keyboard dimensions are: ", keyboard.height, keyboard.width)
            keyboard.size = (700,400)
            keyboard_press = partial(self.keyboard_press, widget, instance, self.searchShirtInput)
            keyboard.bind(on_key_up=keyboard_press)
            #load_tshirt_arg = partial(self.load_tshirt_buttons, self.searchShirtInput)
            search_tshirt_button.bind(on_release=self.load_tshirt_buttons)
            #Clock.schedule_once(self.add_webcam(),5)
        if(instance.text == "Overlay Pic"):
            self.overlay_picture(instance)
        if(instance.text == "Send Pic"):
            self.send_picture(instance)
        if(instance.text == "Take Pic"):
            self.prep_photoshoot(instance)
        if(instance.text == "Exit"):
            self.close_app(instance)
        return
    
    def keyboard_press(self, *args):
        #Here we will program a LUT to handle the keyboard presses
        #Apply appropriate event handles
        #print(*args)
##        if self.sendEmailInput != None:
##            self.searchShirtInput = self.sendEmailInput #terrible design but too lazy to redesign code
        self.current_keyboard_input = []
        for i in range(len(args)):
            self.current_keyboard_input.append(args[i])
        self.current_keyboard_input = self.current_keyboard_input[4:]
        #print("Testing the argument",self.current_keyboard_input)
        if(self.current_keyboard_input[0] == 'escape'):     #Clear Input when escape pressed
            self.searchShirtInput.text = ""
        if(self.current_keyboard_input[0] == 'enter'):     #Clear Input when escape pressed
            #print('enter entered')
            #load_tshirt_arg = partial(self.load_tshirt_buttons, self.searchShirtInput) #first argument is class method
            self.load_tshirt_buttons(self.load_tshirt_buttons)
        if(self.searchShirtInput.selection_text != ""):
            #print("Highlighted a section!")
            #If selected, erase that highlighted portion
            if(self.current_keyboard_input[0]=='backspace'):
                #print('Branch 1')
                if(self.searchShirtInput.text == "Search Tshirt Query Here"):
                    self.searchShirtInput.text = ""
                else:
                    #Delete the contigously selected text
                    begin = self.searchShirtInput.selection_from
                    end = self.searchShirtInput.selection_to
                    if(begin>end):
                        begin,end = end,begin #swap
                    textInputList = list(self.searchShirtInput.text)
                    #print("begin is: ",begin," and end is: ",end)
                    #print(textInputList)
                    del textInputList[begin:end]
                    #print(textInputList)
                    self.searchShirtInput.text = "".join(textInputList)
            elif(self.current_keyboard_input[1] in self.allowed_keyboard_inputs):
                #print('Branch 2')
                #Delete the contigously selected text and insert the new char
                begin = self.searchShirtInput.selection_from
                end = self.searchShirtInput.selection_to
                if(begin>end):
                    begin,end = end,begin #swap                
                textInputList = list(self.searchShirtInput.text)
                #print("begin is: ",begin," and end is: ",end)
                #print(textInputList)
                del textInputList[begin:end]
                #print(textInputList)
                textInputList.insert(begin,self.current_keyboard_input[1])
                self.searchShirtInput.text = "".join(textInputList)
            self.searchShirtInput.selection_text = ""
        elif(self.searchShirtInput.selection_text == ""):
            #print("No section highlighted!")
            if(self.current_keyboard_input[1] in self.allowed_keyboard_inputs):
                #print('Branch 3')
                if(self.searchShirtInput.text == "Search Tshirt Query Here"):
                    self.searchShirtInput.text = ""
                self.searchShirtInput.text += self.current_keyboard_input[1]
            elif(self.current_keyboard_input[0]=='backspace'):
                #print('Branch 4')
                #Delete the contigously selected text and insert the new char
                begin = self.searchShirtInput.selection_from
                end = self.searchShirtInput.selection_to             
                textInputList = list(self.searchShirtInput.text)
                #print("begin is: ",begin," and end is: ",end)
                #print(textInputList)
                if(begin==end):
                    del textInputList[begin-1:end]
                else:
                    del textInputList[begin:end]
                #print(textInputList)
                self.searchShirtInput.text = "".join(textInputList)
        return

    def keyboard_press_email(self, *args):
        #Here we will program a LUT to handle the keyboard presses
        self.searchShirtInput = self.sendEmailInput #terrible design but too lazy to redesign code
        self.current_keyboard_input = []
        for i in range(len(args)):
            self.current_keyboard_input.append(args[i])
        self.current_keyboard_input = self.current_keyboard_input[4:]
        #print("Testing the argument",self.current_keyboard_input)
        if(self.current_keyboard_input[0] == 'escape'):     #Clear Input when escape pressed
            self.searchShirtInput.text = ""
        if(self.current_keyboard_input[0] == 'enter'):     #Clear Input when escape pressed
            #print('enter entered')
            #load_tshirt_arg = partial(self.load_tshirt_buttons, self.searchShirtInput) #first argument is class method
            self.load_tshirt_buttons(self.load_tshirt_buttons)
        if(self.searchShirtInput.selection_text != ""):
            #print("Highlighted a section!")
            #If selected, erase that highlighted portion
            if(self.current_keyboard_input[0]=='backspace'):
                #print('Branch 1')
                if(self.searchShirtInput.text == "Type Your Email Here"):
                    self.searchShirtInput.text = ""
                else:
                    #Delete the contigously selected text
                    begin = self.searchShirtInput.selection_from
                    end = self.searchShirtInput.selection_to
                    if(begin>end):
                        begin,end = end,begin #swap
                    textInputList = list(self.searchShirtInput.text)
                    #print("begin is: ",begin," and end is: ",end)
                    #print(textInputList)
                    del textInputList[begin:end]
                    #print(textInputList)
                    self.searchShirtInput.text = "".join(textInputList)
            elif(self.current_keyboard_input[1] in self.allowed_keyboard_inputs):
                #print('Branch 2')
                #Delete the contigously selected text and insert the new char
                begin = self.searchShirtInput.selection_from
                end = self.searchShirtInput.selection_to
                if(begin>end):
                    begin,end = end,begin #swap                
                textInputList = list(self.searchShirtInput.text)
                #print("begin is: ",begin," and end is: ",end)
                #print(textInputList)
                del textInputList[begin:end]
                #print(textInputList)
                textInputList.insert(begin,self.current_keyboard_input[1])
                self.searchShirtInput.text = "".join(textInputList)
            self.searchShirtInput.selection_text = ""
        elif(self.searchShirtInput.selection_text == ""):
            #print("No section highlighted!")
            if(self.current_keyboard_input[1] in self.allowed_keyboard_inputs):
                #print('Branch 3')
                if(self.searchShirtInput.text == "Search Tshirt Query Here"):
                    self.searchShirtInput.text = ""
                self.searchShirtInput.text += self.current_keyboard_input[1]
            elif(self.current_keyboard_input[0]=='backspace'):
                #print('Branch 4')
                #Delete the contigously selected text and insert the new char
                begin = self.searchShirtInput.selection_from
                end = self.searchShirtInput.selection_to             
                textInputList = list(self.searchShirtInput.text)
                #print("begin is: ",begin," and end is: ",end)
                #print(textInputList)
                if(begin==end):
                    del textInputList[begin-1:end]
                else:
                    del textInputList[begin:end]
                #print(textInputList)
                self.searchShirtInput.text = "".join(textInputList)
        return
                
    def load_tshirt_buttons(self, instance):
        #Here download top 40 t-shirt query results
        #print('Time to load tshirt buttons!')
        self.current_loaded_image_buttons = []
        MyApp.title = "Currently Loading Image Data!"
        base_dir = self.project_dir + "downloads/"+self.searchShirtInput.text+"/" #search for images in this folder
        self.load_tshirt_images(self.searchShirtInput.text, instance)
        fileList = [f for f in listdir(base_dir) if isfile(join(base_dir, f))]
        loopCounter = 0
        for row in range(3):
            for col in range(8):
                try:
                    tempId = str((8*row)+col)
                    for child in widget.children:
                        if tempId==self.GUI_widget.child.id:
                            self.GUI_widget.remove_widget(child.id)
                except:
                    print("Button Does not Exist!")
                tempX = 0+col*95
                tempY = 1000-(row*175)-20
                tempText = str((8*row)+col)#"r"+str(row)+"c"+str(col)
                backgroundImage = base_dir+fileList[loopCounter]
                self.current_loaded_image_buttons.append(backgroundImage)
                #Resize Image Here
                #backgroundImage = "C:/Users/howla_000/Desktop/5th Year Engineering/Second Semester/Capstone II/kivy_show_opencv_pillow-master/circle2.jpg"
                #print('backgroundImage is: ',backgroundImage)
                buttonToAdd = Button(id=tempText, pos=(tempX,tempY), background_normal=backgroundImage) #,font_size=14, background_normal=backgroundImage
                #,pos=(tempX,tempY), size=(95,150)
                buttonToAdd.width = 95
                buttonToAdd.height = 150
                buttonToAdd.bind(on_press=self.saveClickedShirt)
                self.GUI_widget.add_widget(buttonToAdd)
                loopCounter+=1
        return
    
    def saveClickedShirt(self, instance):
        #Store Selected Shirt Image to "saved_images/" directory
        #print(instance.text)
        dispText = "Selected T-Shirt #"+str(int(instance.id)+1)
        labelAnimation = Label(text=dispText,pos=(850,900), font_size=26) #, color=(255,0,0,1)
        self.GUI_widget.add_widget(labelAnimation)
        Animation(opacity=0, duration=3).start(labelAnimation)
        #Move to Saved Image Directory
        fileToSave = self.current_loaded_image_buttons[int(instance.id)]
        fileName = fileToSave.split('/')
        fileName = fileName[len(fileName)-1]
        dirToSave = self.project_dir + "saved_images/" + fileName
        #print(dirToSave)
        #shutil.copyfile(fileToSave,dirToSave)
        self.filter_white_pixels(fileToSave, dirToSave)
        
        return
    
    def filter_white_pixels(self, fileToSave, dirToSave):
        img = PIL.Image.open(fileToSave)
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            elif item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        img.save(dirToSave, "PNG")
        print("Filtered out white pixels!")
        return
    
    def load_tshirt_images(self,query,instance):
        #########Load the actual files#######
        mydir = '/home/pi/Magic_Mirror/Wardrobe_App/downloads' #os.path.realpath(__file__)
        #mydir_resize = 'C:/Users/howla_000/Desktop/5th Year Engineering/Second Semester/Capstone II/kivy_show_opencv_pillow-master/resize'
        shutil.rmtree(mydir, ignore_errors=True)
##        mydir_savedImages = 'C:/Users/howla_000/Desktop/5th Year Engineering/Second Semester/Capstone II/kivy_show_opencv_pillow-master/saved_images'
##        shutil.rmtree(mydir_savedImages, ignore_errors=True)
        #shutil.rmtree(mydir_resize, ignore_errors=True)

        googleImage_query = query
        response = google_images_download.googleimagesdownload()   #class instantiation
        chromeDriverPath = "C:/Users/howla_000/AppData/Local/Programs/Python/Python37/Scripts" #/chromedriver.exe
        #arguments = {"keywords":str(googleImage_query),"limit":40,"print_urls":True, "-cd":chromeDriverPath, "socket_timeout":1}   #creating list of arguments
        arguments = {"keywords":str(googleImage_query),"limit":40,"print_urls":True, "socket_timeout":1}
        self.paths = response.download(arguments)   #passing the arguments to the function

        #shutil.copytree(mydir,mydir_resize)        
        return
    def generate_selfiePNG_name_callback(self, *args):
        #Count Number of Files in "selfies" folder
        selfieDir = "/home/pi/Magic_Mirror/Wardrobe_App/selfies"
        numFiles = len(os.listdir(selfieDir))
        fileName = "selfies/selfie_"+str(numFiles+1)+".png"

        return fileName        

    def load_latest_selfie_callback(self, *args):
        selfieDir = "/home/pi/Magic_Mirror/Wardrobe_App/selfies"
        numFiles = len(os.listdir(selfieDir))
        fileName = "selfies/selfie_"+str(numFiles)+".png"
        try:
            self.GUI_widget.remove_widget(self.previewLabel)
            self.GUI_widget.remove_widget(self.dispNewSelfie)
        except:
            print("previewLabel and dispNewSelfie does not exist in App!")
        
        self.previewLabel = Label(text="Preview:",pos=(50,1000), font_size=34) #, color=(255,0,0,1)
        self.GUI_widget.add_widget(self.previewLabel)
        self.dispNewSelfie = Image(source=fileName, pos=(250,675)) #, res=(512,384)
        self.dispNewSelfie.height = int(0.7*640)
        self.dispNewSelfie.width = int(0.7*480)
        self.GUI_widget.add_widget(self.dispNewSelfie)
        return
    
    def overlay_picture(self, instance):
        self.reset_gui(self.GUI_widget, instance)
##        self.cameraObject            = Camera(play=False)
##        self.cameraObject.play       = True
##        self.cameraObject.resolution = (int(1.2*480), int(1.2*640)) # Specify the resolution
##        self.cameraObject.pos = (256,1200)
##        self.cameraObject.size = (int(1.2*480),int(1.2*640))
        #self.GUI_widget.add_widget(self.cameraObject)    
        selfieDir = "/home/pi/Magic_Mirror/Wardrobe_App/selfies"
        numFiles = len(os.listdir(selfieDir))
        #print("Time to overlay image using radio sliders!")
        #print("numFiles is: ", numFiles)
        #if(numFiles<16):
        for i in range(8,0,-1):
            try:
                index = numFiles - i + 1
                fileName = selfieDir+"/selfie_"+str(index)+".png"
                #print(fileName)
                instanceId="overlay_"+str(index)
                #print("instanceId is: ", instanceId)
                tempX = (i-1)*157
                tempY = 900
                mySelfie = Button(id=instanceId, pos=(tempX,tempY), background_normal=fileName)
                mySelfie.width = 140
                mySelfie.height = 240                
                self.GUI_widget.add_widget(mySelfie)
                mySelfie.bind(on_press=self.setup_overlay_callback)
            except:
                print("Less than 8 images!")
            
        for i in range(8,0,-1):
            try:
                index = numFiles - i + 1 - 8
                fileName = selfieDir+"/selfie_"+str(index)+".png"
                #print(fileName)
                instanceId="overlay_"+str(index)
                #print("instanceId is: ", instanceId)
                tempX = (i-1)*157
                tempY = 625
                mySelfie = Button(id=instanceId, pos=(tempX,tempY), background_normal=fileName)
                mySelfie.width = 140
                mySelfie.height = 240                
                self.GUI_widget.add_widget(mySelfie)
                mySelfie.bind(on_press=self.setup_overlay_callback)
            except:
                print("Less than 16 images but more than 8!")
                
        pickSelfieLabel = Label(id="pickSelfieLabel", text="Pick a Selfie Below:", pos=(80,1125),font_size=26)
        self.GUI_widget.add_widget(pickSelfieLabel)
                #buttonToAdd = Button(id=tempText,pos=(tempX,tempY), background_normal=backgroundImage)
        #Load and Display latest 5 selfies

        return

    def setup_overlay_callback(self, instance):
        selfieDir = "/home/pi/Magic_Mirror/Wardrobe_App/selfies"
        instId = instance.id
        self.reset_gui(self.GUI_widget, instance)
        try:
            self.cameraObject.play = False
            self.GUI_widget.remove_widget(self.cameraObject)
        except:
            print("Webcam is not available for removal!")
        
        #print("instance.id is",instId)
        flagName = str(instId).split("_")     #contains flag and filename
        numFiles = len(os.listdir(selfieDir))
        caseFlag = flagName[0]
        fileIndex = flagName[1]
        fileName = selfieDir+"/selfie_"+str(fileIndex)+".png"
        self.dispNewSelfie = Image(source=fileName, pos=(256,1152)) #, res=(512,384)
        self.dispNewSelfie.height = int(1.2*640) #768
        self.dispNewSelfie.width = int(1.2*480) #576
        self.GUI_widget.add_widget(self.dispNewSelfie)
        #Radio Slider
        self.adjustXPosLabel = Label(text="Adjust Shirt X-Position", pos=(60,700+200), font_size=16)
        self.adjustYPosLabel = Label(text="Adjust Shirt Y-Position", pos=(60,700+150), font_size=16)
        self.adjustWidthLabel = Label(text="Adjust Shirt Width", pos=(60,700+100), font_size=16)
        self.adjustHeightLabel = Label(text="Adjust Shirt Height", pos=(60,700+50), font_size=16)
        rangeX = self.dispNewSelfie.pos[0] + self.dispNewSelfie.width - 100 - self.dispNewSelfie.pos[0]
        self.xPosImageSlider = Slider(id="xPosSlider", pos=(230,700+200),
                                      min=-(rangeX/2), max=(rangeX/2), value=0,
                                      background_width=60, width=150)
        self.yPosImageSlider = Slider(id="yPosSlider", pos=(230,700+150),
                                      min=0, max=(self.dispNewSelfie.height-100), value=0,
                                      background_width=60, width=150)
        self.widthImageSlider = Slider(id="widthSlider", pos=(230,700+100),
                                       min=100, max=self.dispNewSelfie.width, value=100,
                                       background_width=60, width=150)
        self.heightImageSlider = Slider(id="heightSlider", pos=(230,700+50),
                                        min=100, max=self.dispNewSelfie.height, value=100,
                                        background_width=60, width=150)
        
        
        self.xPosImageSlider.bind(on_touch_up=self.adjust_overlay_picture_callback) #on_touch_down, on_touch_move, on_touch_up
        self.yPosImageSlider.bind(on_touch_up=self.adjust_overlay_picture_callback) #this event bind seems to be the most optimal
        self.widthImageSlider.bind(on_touch_move=self.adjust_overlay_picture_callback)
        self.heightImageSlider.bind(on_touch_move=self.adjust_overlay_picture_callback)
        
        self.GUI_widget.add_widget(self.adjustXPosLabel)
        self.GUI_widget.add_widget(self.adjustYPosLabel)
        self.GUI_widget.add_widget(self.adjustWidthLabel)
        self.GUI_widget.add_widget(self.adjustHeightLabel)        
        self.GUI_widget.add_widget(self.xPosImageSlider)
        self.GUI_widget.add_widget(self.yPosImageSlider)
        self.GUI_widget.add_widget(self.widthImageSlider)
        self.GUI_widget.add_widget(self.heightImageSlider)
        #Saved T-Shirt Selection
        #get listing of saved_images, iterate through one by one by latest entry
        filesByDate = self.getDateSorted_directory("/home/pi/Magic_Mirror/Wardrobe_App/saved_images")
        filesByDate = filesByDate[::-1]
        #print(filesByDate)
##        if(len(filesByDate)<10):
##            numIter = len(filesByDate)
##        else:
        numIter = 15
        #print("numIter is: ", numIter)
        for i in range(numIter):
            shirt_dir = "/home/pi/Magic_Mirror/Wardrobe_App/saved_images/"
            shirtDir = shirt_dir+filesByDate[i]
            if i<5:
                tempX = (i)*125 + 425
                tempY = 970
            elif i<10:
                tempX = (i-5)*125 + 425
                tempY = 800
            else:
                tempX = (i-10)*125 + 425
                tempY = 630
            #print("tempX is: ", tempX)
            #print(filesByDate[i])
            try:
                tshirtGallery = Button(id="shirt"+str(i), pos=(tempX,tempY), background_normal=shirtDir)
                tshirtGallery.size = (120,140)
                self.GUI_widget.add_widget(tshirtGallery)
                tshirtGallery.bind(on_press=self.overlay_picture_callback)
            except:
                print("Less than 15 shirt files!")
        return
        
    def getDateSorted_directory(self, dirpath):
        a = [s for s in os.listdir(dirpath)
             if os.path.isfile(os.path.join(dirpath, s))]
        a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
        return a
    
    def truncate(self, number, digits) -> float:
        stepper = pow(10.0, digits)
        return math.trunc(stepper * number) / stepper

    def overlay_picture_callback(self, instance):
        #print("Time to Overlay Pictures")
        #print("instance.id is:", instance.id)
        #print("instance.background_normal is:", instance.background_normal)
        try:
            self.GUI_widget.remove_widget(self.overlayed_image)
        except:
            print("Widget does not exist!")

        self.overlayed_image = Image(source=instance.background_normal, pos=(906,320)) #considering filtering out white pixel here
        self.overlayed_image.height = 100
        self.overlayed_image.width = 100
        saveImageButton = Button(text="Save Image", pos=(100,1025), font_size=28)
        saveImageButton.size = (200,100)
        self.GUI_widget.add_widget(self.overlayed_image)
        self.GUI_widget.add_widget(saveImageButton)
        self.toggleFlag = False
        saveImageButton.bind(on_press=self.save_overlayed_picture_callback)
        print("self.overlayed_image height width: ", self.overlayed_image.height, self.overlayed_image.width)
        #self.overlayed_image.pos = (100,400)
        #print("Should have added a save button")
        return
    
    def adjust_overlay_picture_callback(self, instance, sliderData):
        print("instance.id is:", instance.id)
        #print("sliderData is:", sliderData)
        print("instance.value_normalized is", instance.value_normalized)
        defaultX = 256+50+int(576/2)      #To recentre if X or Y pos are being changed
        defaultY = 1152        
        try:
            (tempX, tempY) = self.overlayed_image.pos
            if(instance.id == "xPosSlider"):
                #print("self.adjustXPosLabel.text is: ", self.adjustXPosLabel.text)
                #print("self.xPosImageSlider.value is: ", self.truncate(instance.value,0))
                self.adjustXPosLabel.text = "Adjust Shirt X-Position "+str(100*self.truncate(instance.value_normalized,2))+"%"
                tempX = defaultX
                self.overlayed_image.pos = (tempX-int(self.overlayed_image.width/2)+self.truncate(instance.value,0),tempY)
            if(instance.id == "yPosSlider"):
                #print("self.adjustYPosLabel.text is: ", self.adjustYPosLabel.text)
                #print("self.yPosImageSlider.value is: ", self.truncate(instance.value,0))
                self.adjustYPosLabel.text = "Adjust Shirt Y-Position "+str(100*self.truncate(instance.value_normalized,2))+"%"
                tempY = defaultY
                self.overlayed_image.pos = (tempX, tempY+self.truncate(instance.value,0))
            if(instance.id == "widthSlider"):
                self.adjustWidthLabel.text = "Adjust Shirt Width "+str(self.truncate(instance.value,2))
                self.overlayed_image.width = instance.value
                self.overlayed_image.height = self.heightImageSlider.value

                #For preventing users from going out of bound
##                rangeX = 512 - self.overlayed_image.width
##                self.xPosImageSlider.min = -(rangeX/2)
##                self.xPosImageSlider.max = rangeX/2
                
                
            if(instance.id == "heightSlider"):
                self.adjustHeightLabel.text = "Adjust Shirt Height "+str(self.truncate(instance.value,2))
                self.overlayed_image.height = instance.value
                self.overlayed_image.width = self.widthImageSlider.value
                
##                rangeY = 384 - self.overlayed_image.height
##                self.yPosImageSlider.min = 0
##                self.yPosImageSlider.max = rangeY
                
        except:
            print("self.overlayed_image does not exist!")

        return

    def save_overlayed_picture_callback(self, instance):
        #Get class instance parameters and manually (using image filtering)
        #save the image
        dirShare = "/home/pi/Magic_Mirror/Wardrobe_App/share_images/"
        print("Selected Selfie pic is:", self.dispNewSelfie.source)
        numFiles = len(os.listdir(dirShare))+1
        fileName = dirShare+"/selfie_"+str(numFiles)+".png"
        print("Hello!")
        print(self.overlayed_image.source)
        print(self.overlayed_image.pos)
        print(self.overlayed_image.height)
        print(self.overlayed_image.width)
        print(self.overlayed_image)

        #Take a cropped screenshot of the overlayed two images and save using PIL's Image Processing Library
        self.GUI_widget.export_to_png(fileName)
        shareImg  = PIL.Image.open(fileName)
        #Crop the image and resave with the save name
        cropped = shareImg.crop((256, 0, 832, 768))   #X1 Y1 X2 Y2 topright is 0,0//////// 700,0,1210,380
        cropped.save(fileName)
        #Give Notification to User it has been saved
        #Label timeout
        dispText = "Saved Selfie #"+str(numFiles)
        labelAnimation = Label(text=dispText,pos=(100,1100), font_size=26) #, color=(255,0,0,1)
        self.GUI_widget.add_widget(labelAnimation)
        Animation(opacity=0, duration=3).start(labelAnimation)
        return
    
    def send_picture(self, instance):
        self.reset_gui(self.GUI_widget, instance)
        try:
            self.cameraObject.play = False
            self.GUI_widget.remove_widget(self.cameraObject)
        except:
            print("Failed To Remove CameraObject from GUI!")
        #Load Appropriate number of images, then bind them to event
        #Load Keyboard, and once the binded event (click of selfie)
        #send email if the email parameter is filled
        self.selected_selfie_source = None    
        emailAddr_label = Label(text='Type Your Email Below:', pos=(850,275), font_size=30)
        self.GUI_widget.add_widget(emailAddr_label)                        
        emailAddr_query_input = TextInput(pos=(700,200), font_size=16)
        emailAddr_query_input.size = (400,100)
        send_email_button = Button(text='Send Email',pos=(700,100), font_size=30)
        self.sendEmailInput = emailAddr_query_input
        send_email_button.size = (400,100)
        self.GUI_widget.add_widget(emailAddr_query_input)
        self.GUI_widget.add_widget(send_email_button)
        keyboard = VKeyboard(pos=(0,0))
        self.GUI_widget.add_widget(keyboard)            
        #print("keyboard dimensions are: ", keyboard.height, keyboard.width)
        keyboard.size = (700,400)
        keyboard_press = partial(self.keyboard_press_email, self.GUI_widget, instance, self.sendEmailInput)
        keyboard.bind(on_key_up=keyboard_press)
        #load_tshirt_arg = partial(self.load_tshirt_buttons, self.searchShirtInput)
        send_email_button.bind(on_release=self.prepare_selfie_email)
        self.load_selfies()
        return

    def load_selfies(self):
        #Load latest selfie images and bind them with event to load the enter button
        #Set the self.selected_selfie_source= "C://..."
        #Saved T-Shirt Selection
        #get listing of saved_images, iterate through one by one by latest entry
        select_selfie_label = Label(text="Select One of the Selfie Images from Above To Share!", font_size=30)
        select_selfie_label.pos = (500, 610)
        self.GUI_widget.add_widget(select_selfie_label)
        filesByDate = self.getDateSorted_directory("/home/pi/Magic_Mirror/Wardrobe_App/share_images")
        filesByDate = filesByDate[::-1]
        #print(filesByDate)
        if(len(filesByDate)<12):
            numIter = len(filesByDate)
        else:
            numIter = 12
        #print("numIter is: ", numIter)
        for i in range(numIter):
            selfie_dir = "/home/pi/Magic_Mirror/Wardrobe_App/share_images/"
            selfieDir = selfie_dir+filesByDate[i]
            baseOffset_Y = 400+200 #button_offset+button_height
            if i<4:
                tempX = (i)*270 + 30
                tempY = baseOffset_Y + 200 + 400 + 400
            elif i<8:
                tempX = (i-4)*270 + 30
                tempY = baseOffset_Y + 200 + 400
            else:
                tempX = (i-8)*270 + 30
                tempY = baseOffset_Y+ 200
            #print("tempX is: ", tempX)
            print(selfieDir)
            selfiePics = Button(id=str(filesByDate[i]), pos=(tempX,tempY), background_normal=selfieDir)
            selfiePics.size = (200, 300)
            self.GUI_widget.add_widget(selfiePics)
            selfiePics.bind(on_press=self.select_selfie_pic_callback)
        return

    def select_selfie_pic_callback(self, instance):
        selfie_dir = "/home/pi/Magic_Mirror/Wardrobe_App/share_images/"
        print(instance.id)
        try:
            self.GUI_widget.remove_widget(self.selfie_disp)
            self.GUI_widget.remove_widget(self.selectedSelfieLabel)
        except:
            print("That selfie pic does not exist!")
        self.selected_selfie_source = selfie_dir = selfie_dir + instance.id
        
        self.selectedSelfieLabel = Label(text="Selected Selfie:", pos=(700,700), font_size=26)
        self.selfie_disp = Image(id="selfieDisp", source=selfie_dir, pos=(600,425))
        self.selfie_disp.size = (600,300)
        self.GUI_widget.add_widget(self.selectedSelfieLabel)
        self.GUI_widget.add_widget(self.selfie_disp)

        return

    def prepare_selfie_email(self, instance):
        if(self.selected_selfie_source!=None):
            print("selected a selfie to send by email!")
            print("email address is:",self.sendEmailInput.text)
            if re.match("[^@]+@[^@]+\.[^@]+", self.sendEmailInput.text):
                print("Syntactically Valid Email Address!")
                print(self.selected_selfie_source)
##                dispText = "Sending Email to: "+self.sendEmailInput.text
##                labelAnimation = Label(text=dispText,pos=(700,0), font_size=26) #, color=(255,0,0,1)
##                self.GUI_widget.add_widget(labelAnimation)
##                Animation(opacity=0, duration=3).start(labelAnimation)
                #Start Email Transmission Procedure
                self.send_selfie_email(self.sendEmailInput.text, self.selected_selfie_source)
                dispText = "Sent Email to: "+self.sendEmailInput.text
                labelAnimation = Label(text=dispText,pos=(700,0), font_size=26) #, color=(255,0,0,1)
                self.GUI_widget.add_widget(labelAnimation)
                Animation(opacity=0, duration=5).start(labelAnimation)
            else:
                print("Syntactically Invalid Email Address!")
                dispText = "Invalid Email Syntax!"
                labelAnimation = Label(text=dispText,pos=(700,0), font_size=18) #, color=(255,0,0,1)
                self.GUI_widget.add_widget(labelAnimation)
                Animation(opacity=0, duration=5).start(labelAnimation)
        else:
            print("there is no selected selfie!")
            dispText = "Need To Select Selfie!"
            labelAnimation = Label(text=dispText,pos=(850,320), font_size=34) #, color=(255,0,0,1)
            labelAnimation.color = [1,0,0,1]
            self.GUI_widget.add_widget(labelAnimation)
            Animation(opacity=0, duration=5).start(labelAnimation)            
        return

    def send_selfie_email(self, receiver_email, file_to_send):
        subject = "Your Requested Selfie Image"
        body = "This is an email with attachment sent from Magic Mirror"
        sender_email = "magic.mirror.mcmaster@gmail.com"
        #receiver_email = "howladermoshiur@gmail.com"
        password = "$Stapler333"

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        #message["Bcc"] = sender_email  # Recommended for mass emails

        # Add body to email
        message.attach(MIMEText(body, "plain"))
        print("File to send is", file_to_send)
        filename = file_to_send  # In same directory as script

        # Open above file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            "attachment; filename= selfie.png"
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

        return
    
    def prep_photoshoot(self,instance):
        self.reset_gui(self.GUI_widget, instance)
        take_photo_button = Button(text="Smile!", pos=(860,1150), font_size=30)
        take_photo_button.size = (200,100)
        self.GUI_widget.add_widget(take_photo_button)
        take_photo_button.bind(on_press=self.take_photo)
        return
    
    def take_photo(self,instance):
        dispText = "Took Picture! Loading Preview."
        labelAnimation = Label(text=dispText,pos=(500,1050), font_size=34) #, color=(255,0,0,1)
        try:
            if self.dispNewSelfie != None:
                labelAnimation.pos = (800,1050)
        except:
            print("dispNewSelfie is not defined!")
        
        self.GUI_widget.add_widget(labelAnimation)
        Animation(opacity=0, duration=5).start(labelAnimation)
        exportFile = self.generate_selfiePNG_name_callback()
        Clock.schedule_once(partial(self.cameraObject.export_to_png,exportFile),5)
        self.dispSelfieIntval = Clock.schedule_interval(self.load_latest_selfie_callback, 5)        
        return
    
    def build(self):
        #print("Configured Setting")
        #Window.fullscreen = True
        self.height = 400#GetSystemMetrics(0)
        self.width = 500#GetSystemMetrics(1)
        self.fullscreen_gui()

        self.boxlayout = BoxLayout()
        self.GUI_widget = Widget()
        
        disclaimer_label = Label(text="Don't Make Rasp-pi Upset, Click Dark Part of Screen First!")
        disclaimer_label.font_size = 30
        disclaimer_label.pos = (500, 610)
        
        testButton = Button(text='Search Shirts',pos=(000,400), font_size=24)
        testButton2 = Button(text='Overlay Pic',pos=(220,400), font_size=24)
        testButton3 = Button(text='Send Pic',pos=(220*2,400), font_size=24)
        testButton4 = Button(text='Take Pic', pos=(220*3,400), font_size=24)
        testButton5 = Button(text='Exit',pos=(220*4,400), font_size=24)
        testButton.size = (220,200)
        testButton2.size = (220,200)
        testButton3.size = (220,200)
        testButton4.size = (220,200)
        testButton5.size = (220,200)
        
        self.cameraObject            = Camera(play=False)
        self.cameraObject.play       = True
        self.cameraObject.resolution = (int(1.2*480), int(1.2*640)) # Specify the resolution
        self.cameraObject.pos = (256,1152)
        self.cameraObject.size = (int(1.2*480),int(1.2*640))
        self.GUI_widget.add_widget(self.cameraObject)
        
        self.GUI_widget.add_widget(disclaimer_label)
        self.GUI_widget.add_widget(testButton)
        self.GUI_widget.add_widget(testButton2)
        self.GUI_widget.add_widget(testButton3)
        self.GUI_widget.add_widget(testButton4)
        self.GUI_widget.add_widget(testButton5)
        update_GUI = partial(self.update_gui,self.GUI_widget)
        testButton.bind(on_press=update_GUI)
        testButton4.bind(on_press=update_GUI)       #possible to add additional callback functions
        testButton2.bind(on_press=update_GUI)
        testButton3.bind(on_press=update_GUI)
        reset_GUI = partial(self.reset_gui, self.GUI_widget)
        testButton5.bind(on_press=update_GUI)

        return self.GUI_widget


if __name__ == '__main__':
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()    
    MyApp().run()





