# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 23:42:13 2017

@author: Sebastian
"""

from struct import pack
from math import sin, pi
import wave
import random

RATE=44100

## GENERATE MONO FILE ##
wv = wave.open('D:/GIT/autosampler/outputs/output_mono.wav', 'wb')
wv.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
maxVol=2**15-1.0 #maximum amplitude
wvData=b""
for i in range(0, RATE*3):
	wvData+=str(pack('h', int(float(maxVol*sin(i*500.0/RATE))))) #500Hz
wv.writeframes(bytearray(wvData, 'ascii'))
wv.close()

## GENERATE STERIO FILE ##
wv = wave.open('D:/GIT/autosampler/outputs/output_stereo.wav', 'wb')
wv.setparams((2, 2, RATE, 0, 'NONE', 'not compressed'))
maxVol=2**15-1.0 #maximum amplitude
wvData=b""
for i in range(0, RATE*3):
	wvData+=str(pack('h', int(float(maxVol*sin(i*500.0/RATE))))) #500Hz left
	wvData+=str(pack('h', int(float(maxVol*sin(i*200.0/RATE))))) #200Hz right
# print(wvData)
wv.writeframes(bytearray(wvData, 'ascii'))
wv.close()