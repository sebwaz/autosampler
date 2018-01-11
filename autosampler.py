# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 23:55:00 2017

@author: Sebastian
"""

import wave
import struct
import numpy as np
from math import floor

wfile   = wave.open('D:/GIT/autosampler/longforms/once_we_were_fish.wav', 'r')
write1_wav = wave.open('D:/GIT/autosampler/outputs/output_ONE.wav', 'w')
write2_wav = wave.open('D:/GIT/autosampler/outputs/output_TWO.wav', 'w')

# get the parameters of the input, use as parameters for the output
nchannels = wfile.getparams().nchannels
sampwidth = wfile.getparams().sampwidth
framerate = wfile.getparams().framerate
nframes   = wfile.getparams().nframes
comptype  = wfile.getparams().comptype
compname  = wfile.getparams().compname
params    = (nchannels, sampwidth, framerate, nframes, comptype, compname)
write1_wav.setparams(params)
write2_wav.setparams(params)


print(nchannels) # 1 for mono, 2 for stereo. MONO CASE NOT ADDRESSED
print(sampwidth) # number of bytes per sample
print(framerate) # number of samples per second
print(nframes)   # number of samples in file (1 sample carries as many values as channels)
print(comptype)
print(compname)


'''
CURRENT IDEA:
it seems likely that readframes is reading two 16bit shorts as one 32bit int
I will need to use some sort of bit masking to get two shorts which can then be
passed back into writeframes short by short (thus allowing me to work with interleaved
stereo information)
'''

# the number of samples to pull from the input
n=nframes

# the number of unique values a sample can take on, based on sampwidth
typerange=2**(8*sampwidth)

# note: WAV file byte order is little endian
read_data = wfile.readframes(n)

# parse the read data into lists of shorts
# TODO: change '<H' to '<...' based on sampwidth
y   = np.repeat(np.arange(n), sampwidth)*(2*sampwidth)
l_i = (y+np.tile(np.arange(sampwidth), n)).reshape(n, sampwidth)
r_i = (y+np.tile(np.arange(sampwidth, sampwidth*2), n)).reshape(n, sampwidth)
l_data = [struct.unpack('<H', read_data[x[0]:x[-1]+1])[0] for x in l_i]
r_data = [struct.unpack('<H', read_data[x[0]:x[-1]+1])[0] for x in r_i]

#### NOW ITS IN INTS! CONVERT TO [-1, 1] ### VALUES ASSUME 16BIT
l_norm = [x/((typerange/2)-1) if x<=((typerange/2)-1) else -((typerange-x)/(typerange/2)) for x in l_data]
r_norm = [x/((typerange/2)-1) if x<=((typerange/2)-1) else -((typerange-x)/(typerange/2)) for x in r_data]

# check
print(l_norm[:10])
print(r_norm[:10])

#### convert from [-1, 1] back to short ### VALUES ASSUME 16BIT
l_short = [int(floor(((x/2)+1)*typerange)) if x<0 else int(floor((x/2)*(typerange-1))) for x in l_norm]
r_short = [int(floor(((x/2)+1)*typerange)) if x<0 else int(floor((x/2)*(typerange-1))) for x in r_norm]

# check
print(l_short[:10])
print(l_data[:10])
print(r_short[:10])
print(r_data[:10])

merged       = l_short + r_short
merged[::2]  = l_short
merged[1::2] = r_short
#print(l_data[:10])
#print(r_data[:10])
#print(merged[:10])
byte_stream = b''.join([struct.pack('<H', merged[i]) for i in range(len(merged))])
print(byte_stream)


write1_wav.writeframes(byte_stream)
wfile.close()
write1_wav.close()
write2_wav.close()