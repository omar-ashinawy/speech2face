# -*- coding: utf-8 -*-
"""Audio_Encoder_Dataset_Ashinawy.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_I9feUPtgIpaHf9DgDP0PidQ0_neUBNz
"""

import os
from google.colab import drive
drive.mount('/content/drive')

faces_files = [int(f[f.find('_') + 1: f.find('.')]) for f in os.listdir('/content/drive/MyDrive/face_npy') if os.path.isfile(os.path.join('/content/drive/MyDrive/face_npy', f))]
faces_files.sort()
with open('/content/drive/MyDrive/face_indices.txt', 'w') as f:
    f.write('Number of files: ' + str(len(faces_files)) + '\n')
    for file_name in faces_files:
        f.write(str(file_name) + '\n')
audios_files = [int(f[f.find('_') + 1: f.find('.')]) for f in os.listdir('/content/drive/MyDrive/audio_npy') if os.path.isfile(os.path.join('/content/drive/MyDrive/audio_npy', f))]
audios_files.sort()
with open('/content/drive/MyDrive/audio_indices.txt', 'w') as f:
    f.write('Number of files: ' + str(len(audios_files)) + '\n')
    for file_name in audios_files:
        f.write(str(file_name) + '\n')

!pip install youtube_dl
!pip install ffmpeg-python 
!pip install moviepy --upgrade
!pip install keras_vggface
!pip install keras_applications

!pip install keras_vggface
!pip install keras_applications
from keras_vggface.vggface import VGGFace

# Based on VGG16 architecture -> old paper(2015)
vggface = VGGFace(model='vgg16') # or VGGFace() as default

!pip install face_recognition

import os
import pickle
from sys import stdout
import moviepy.editor as mp
import pandas as pd
import time
import youtube_dl
import ffmpeg
from PIL import Image
import numpy as np
from keras.applications.vgg16 import VGG16
from keras.models import Sequential
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras_vggface.vggface import VGGFace
import cv2
import dlib
import tensorflow as tf
import librosa
import librosa.display
import IPython.display as ipd
import matplotlib.pyplot as plt

import cv2
import dlib
import argparse
import time
import numpy as np
hog_face_detector = dlib.get_frontal_face_detector()
from mlxtend.image import extract_face_landmarks
import skimage.draw
from PIL import Image 
import PIL 
def detect(frame):
    """
    
    THIS FUNCTION DETECTS THE FACE IN GREY IMAGE AND CROP IT THEN PREDICT ITS  FACE FEATURE
    
    PAPAMETER:
    GREY:  np array; THE GREY SCALE OF IMAGE
    FRAME: np array; ACTUAL IMAGE
    
    RETURNS:
    FACE_FEATURE: np.array; PREDICTED ARRAY OF SIZE (1,2048)
    FRAME_CROP: np array; CROPED IMAGE
    
    """
    landmarks = extract_face_landmarks(frame)
    min_x = np.min(landmarks[:,0])
    max_x = np.max(landmarks[:,0])
    min_y = np.min(landmarks[:,1])
    max_y = np.max(landmarks[:,1])
    cropped_img = frame[min_y:max_y,min_x:max_x]
    cropped_img = cv2.resize(cropped_img, (224,224))

    return cropped_img

class Audio_Preprocessor:

	def __init__(self, wav_path = "",Processed_path="",sr = 16000, frSize = 512, HopLength = 160, HannWindow = 400):
		# Preprocessing Parameters
		self.Processed_path ="Processed Audio\\"

		if not os.path.exists(self.Processed_path):	
			os.makedirs(self.Processed_path,mode=0o777,exist_ok = False)
		
		self.Sampling_Rate = sr
		self.Frame_Size = frSize
		self.Hop_Length = HopLength
		self.Hann_Window = HannWindow

	def Complex_Spectrogram(self,Audio_Path):

		# load Audio File
		input_data = tf.io.read_file(Audio_Path)
		audio , sr= tf.audio.decode_wav(input_data, desired_channels=1, desired_samples=self.Sampling_Rate)
		# check the Audio duration 
		if(audio.shape[0] < self.Sampling_Rate*6):
			print("Audio clip is Smaller")
			audio = np.resize(audio,(self.Sampling_Rate*6,))
		
		elif(audio.shape[0] > self.Sampling_Rate*6):
			print("Audio clip is Bigger")
			audio = audio[0:self.Sampling_Rate*6-1]
		
		# calculate the STFT
		Frequency_Components = tf.signal.stft(audio, fft_length = self.Frame_Size, frame_step = self.Hop_Length, frame_length = self.Hann_Window, window_fn = tf.signal.hann_window )
		# print(Frequency_Components.shape)

		# seperate the Real and imaginary parts and apply the Power low
		Real_Part      = np.real(Frequency_Components)
		Imaginary_Part = np.imag(Frequency_Components)

		Real_Part      = np.sign(Real_Part) * ( np.abs(Real_Part) ** 0.3 )
		Imaginary_Part = np.sign(Imaginary_Part) * ( np.abs(Imaginary_Part) ** 0.3 )

		return Real_Part,Imaginary_Part


	def Draw_Spectrograms(self,Real_Part,Imaginary_Part):
		fig = plt.figure(figsize=(25, 10))

		ax1=fig.add_subplot(121)
		librosa.display.specshow(librosa.power_to_db(Real_Part),sr=self.Sampling_Rate, hop_length=self.Hop_Length,x_axis="time",y_axis="log")

		ax1.set_title('Real')

		ax2=fig.add_subplot(122)

		ax2.set_title('Imaginary')

		librosa.display.specshow(librosa.power_to_db(Imaginary_Part),sr=self.Sampling_Rate, hop_length=self.Hop_Length,x_axis="time",y_axis="log")

		plt.colorbar(format="%+2.f")
		plt.show()

	def write(self, Real_Part, Imaginary_Part, Name):
		
		output_Path = self.Processed_path + Name + ".txt"
		#with open(output_Path,"w+") as output:
		np.savetxt(output_Path,np.r_[Real_Part,Imaginary_Part])

	def read(self, Name):
		input_Path = Name + ".txt"
		real=[]
		imaginary=[]
		counter = 0
		with open(input_Path,"r") as file:
			for line in file:
				if(counter<257):
					real.append(np.float_(line.split(' ')))
				else:
					imaginary.append(np.float_(line.split(' ')))
				counter= counter+1
		return real,imaginary

# Testing
# Preprocessor = Audio_Preprocessor()

# Put the Audio File Path
# Audio_Path = "../audios/akwvpAiLFk0.wav"

# Real_Part, Imaginary_Part = Preprocessor.Complex_Spectrogram(Audio_Path)

# print(np.array([Real_Part, Imaginary_Part]).reshape((598, 257, 2)).shape)
# Preprocessor.Draw_Spectrograms(Real_Part, Imaginary_Part)
class Face_Detector():
  def __init__(self, face_detector_weights_path):
    self.__cnn_face_detector = dlib.cnn_face_detection_model_v1(face_detector_weights_path)
    self.__vgg16_model = VGGFace(model = 'vgg16')
  def detect(self,frame):
    """
    
    THIS FUNCTION DETECTS THE FACE IN GREY IMAGE AND CROP IT THEN PREDICT ITS  FACE FEATURE
    
    PAPAMETER:
    GREY:  np array; THE GREY SCALE OF IMAGE
    FRAME: np array; ACTUAL IMAGE
    
    RETURNS:
    FACE_FEATURE: np.array; PREDICTED ARRAY OF SIZE (1,2048)
    FRAME_CROP: np array; CROPED IMAGE
    
    """
    landmarks = extract_face_landmarks(frame)
    min_x = np.min(landmarks[:,0])
    max_x = np.max(landmarks[:,0])
    min_y = np.min(landmarks[:,1])
    max_y = np.max(landmarks[:,1])
    cropped_img = frame[min_y:max_y,min_x:max_x]
    cropped_img = cv2.resize(cropped_img, (224,224))

    return cropped_img


  def feature_vector(self, picturename= '', PIL_image = None): #picturename like 'mug.jpg' with the single quates
      model = Sequential()

      for layer in self.__vgg16_model.layers[:-3]:

          model.add(layer)

      for layer in model.layers:

          layer.trainable = False

      if not (PIL_image is None):
          image = PIL_image.resize((224, 224))
      else:
          image = load_img(picturename, target_size=(224, 224))
      image = img_to_array(image)
      image = image.reshape((1,image.shape[0], image.shape[1], image.shape[2]))
      image = preprocess_input(image)
      return model.predict(image)


class GetDataset:

  Dataset = ""
  AudioFolder = ""
  PhotoFolder = ""
  VideoFolder = "videos"
  Batch=1
  Audio_Preprocessor = Audio_Preprocessor()
  Face_Detector = Face_Detector('/content/drive/MyDrive/mmod_human_face_detector.dat')
  numberconverted = 0
  startpos=0
  def start_from(self, from_prev_pos= True, start_pos= 0):
      start_from = start_pos
      if from_prev_pos:
          with open('stopPos.txt', 'r') as f:
              start_from = int(f.read())
      self.startpos = start_from
      
  def extractAudio(self,vid_path): #extract audio from a video
    try:
      clip=mp.VideoFileClip(vid_path)
      frameName=vid_path[vid_path.find("/")+1:-4]
      audioName=vid_path[vid_path.find("/")+1:-4]
      outputPath = self.AudioFolder+"/"+str(self.numberconverted+self.startpos)+".wav"   
      clip.audio.write_audiofile(outputPath, logger=None)
      clip.close()
      real_part, imaginary_part = self.Audio_Preprocessor.Complex_Spectrogram(outputPath)
      audio_features = np.array([real_part, imaginary_part]).reshape(((598, 257, 2)))
      file_path = "/content/drive/MyDrive/audio_npy"+"/"+"audio_"+str(self.numberconverted+self.startpos)+".npy"
      with open(file_path, 'wb') as f:
          np.save(f, audio_features)
    except Exception as e:
      print('Audio Error:', e)
      clip.close()
      with open ("errorAudios.txt","a+") as err:
        err.write("Vid: " + frameName + " Error Extracting Audio \n")
      
  def extractFrame(self,vid_path):
    try:
      clip=mp.VideoFileClip(vid_path)
      frameName=vid_path[vid_path.find("/")+1:-4]
      imgarray = clip.get_frame(2)
      face = self.Face_Detector.detect(imgarray)
      face_features = self.Face_Detector.feature_vector(PIL_image = Image.fromarray(face)).reshape((4096))
      #Image.fromarray(imgarray).save("/content/drive/MyDrive/uncropped_photos"+"/"+"face_"+str(self.numberconverted+self.startpos)+".png")
      Image.fromarray(face).save("/content/drive/MyDrive/cropped_photos"+"/"+"face_"+str(self.numberconverted+self.startpos)+".png")
      clip.close()
      file_path = '/content/drive/MyDrive/face_npy'+"/"+"face_"+str(self.numberconverted+self.startpos)+".npy"
      with open(file_path, 'wb') as f:
          np.save(f, face_features)
    except Exception as e:
      print('Face Error:', e)
      clip.close()
      with open ("errorFrames.txt","a+") as err:
        err.write("Vid: " + frameName + " Error Extracting Frame \n")
  
  def setDatasetCSV(self,filename):
    self.Dataset = filename
  def setAudioOutputFolder(self,foldername):
    self.AudioFolder = foldername
    try:
      if not os.path.exists(self.AudioFolder):
         os.mkdir(self.AudioFolder)
    except:
     stdout.write("\r[!]Couldn't Make New Folder For Audios")
     pass     
         

  def setPhotoOutputFolder(self,foldername):
    self.PhotoFolder = foldername
    try:
      if not os.path.exists(self.PhotoFolder):
        os.mkdir(self.PhotoFolder)
    except:
     stdout.write("\r[!]Couldn't Make New Folder For Photos")
     pass
  def convertVideos(self):
      vids_dir = "videos"
      if not os.path.exists(vids_dir):    
             os.mkdir(vids_dir)

      train_set = pd.read_csv(self.Dataset,names=["video_ID", "start_t", "end_t","x","y"]) 
        
      
        
      endpos=self.startpos+self.Batch
      self.numberconverted=0
      #startpos=0
      
      #for i in range(len(train_set)):
      for i in range(self.startpos,endpos):
        
        self.numberconverted += 1
        video_ID= train_set.iloc[i]['video_ID']
        start_t,end_t  = train_set.iloc[i]['start_t'],train_set.iloc[i]['end_t']
        video_name=video_ID+".mp4"


       # if(self.isAlreadyConverted(video_name) == 0): #avoid downloading same video again

        #Download Video:
        try:
            stdout.write("\n[+]Downloading video: %s" % video_ID)
            start_t_f = time.strftime("%H:%M:%S", time.gmtime(start_t))  #hh:mm:ss
            end_t_f   = time.strftime("%H:%M:%S", time.gmtime(end_t))  #hh:mm:ss        
            duration = end_t -start_t
            #print(duration)    
            downloadstate=Youtube.downloadvideo(video_ID,start_t_f,duration)
            print(downloadstate)
        except Exception as e:
            print(e)
            stdout.write("\r[!]Couldn't Download: %s" % video_ID)
            with open ('error.txt','a+') as err:
              err.write(video_ID + " Download Failed \n")
            continue

        if (downloadstate[-5:]!="DONE!"):
          with open ('error.txt','a+') as err:
              err.write(video_ID + " Download Failed \n")
          continue
        
        stdout.write("\b\r[+]Converting video: %s" % video_ID)
                
        vid_path = vids_dir + "/" + video_ID + ".mp4"  # Video Location 
        
        # extract audio and frame :
        try:
           self.extractAudio(vid_path)
           self.extractFrame(vid_path)
           stdout.write("\t[!]Video %s converted " % video_ID)
        except Exception as e:
           print(e)
           stdout.write("\t[!]Video %s not found " % video_ID)

        try:   
          os.remove(os.path.join("videos", video_ID +'.mp4'))
        except:
          pass

        
        if (self.numberconverted == endpos):  # number of videos to download and convert every single run
          with open ('stopPos.txt','w') as stop:
              stop.write(str(self.startpos+self.numberconverted))
              break
 
class Youtube:
  
 def downloadvideo(video_ID,start_t,end_t):

    yt_base_url = 'https://www.youtube.com/watch?v='
    
    
    yt_url = yt_base_url + video_ID
    
    
    outputfile= os.path.join("videos", video_ID +'.mp4')

    ydl_opts = {
        'format': '22/18',
        'quiet': True,
        'ignoreerrors': True,
        'no_warnings': True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            download_url = ydl.extract_info(url=yt_url, download=False)['url']
    except:
        return_msg = '{}, ERROR (youtube)!'.format(video_ID)
        return return_msg
    try:
      (
        ffmpeg
        .input(download_url, ss=start_t, t=end_t)
        .output(outputfile, format='mp4', r=25, vcodec='libx264',crf=18, preset='veryfast', pix_fmt='yuv420p', acodec='aac', audio_bitrate=128000,strict='experimental')
        .global_args('-y')
        .global_args('-loglevel', 'trace')
        .run(capture_stdout=True, capture_stderr=True)
      )
    except:
        return_msg = '{}, ERROR (ffmpeg)!'.format(video_ID)
        return return_msg

    return '{}, DONE!'.format(video_ID)
    

#print(downloadvideo("307DK9nGQhw","00:01:30","00:01:33"))

x= GetDataset()
x.Batch= 10000
x.start_from(from_prev_pos = True)
x.setDatasetCSV("/content/drive/MyDrive/avspeech_train.csv")
x.setAudioOutputFolder("/content/drive/MyDrive/audio_files")
x.setPhotoOutputFolder("/content/drive/MyDrive/uncropped_photos")
x.convertVideos()

