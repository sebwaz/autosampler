# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 23:55:00 2017

@author: Sebastian
"""

import wave
import struct
import numpy as np
from math import floor

read_wav   = wave.open('D:/GIT/autosampler/longforms/shirleykwan.wav', 'r')
write1_wav = wave.open('D:/GIT/autosampler/outputs/output_ONE.wav', 'w')
write2_wav = wave.open('D:/GIT/autosampler/outputs/output_TWO.wav', 'w')

# get the parameters of the input, use as parameters for the output
nchannels = read_wav.getparams().nchannels
sampwidth = read_wav.getparams().sampwidth
framerate = read_wav.getparams().framerate
nframes   = read_wav.getparams().nframes
comptype  = read_wav.getparams().comptype
compname  = read_wav.getparams().compname
params    = (nchannels, sampwidth, framerate, nframes, comptype, compname)
write1_wav.setparams(params)
write2_wav.setparams(params)


print(nchannels) # 1 for mono, 2 for stereo. MONO CASE NOT ADDRESSED
print(sampwidth) # number of bytes per sample
print(framerate) # number of samples per second
print(nframes)   # number of samples in file

'''
print(comptype)
print(compname)
'''

'''
CURRENT IDEA:
it seems likely that readframes is reading two 16bit shorts as one 32bit int
I will need to use some sort of bit masking to get two shorts which can then be
passed back into writeframes short by short (thus allowing me to work with interleaved
stereo information)
'''

# the number of samples to pull from the input
n=framerate*15

# the number of unique values a sample can take on, based on sampwidth
shortrange=2**(8*sampwidth)

# note: WAV file byte order is little endian
read_data = read_wav.readframes(n)

# parse the read data into lists of shorts
# TODO: change '<H' to '<...' based on sampwidth
y   = np.repeat(np.arange(n), sampwidth)*(2*sampwidth)
l_i = (y+np.tile(np.arange(sampwidth), n)).reshape(n, sampwidth)
r_i = (y+np.tile(np.arange(sampwidth, sampwidth*2), n)).reshape(n, sampwidth)
l_data = [struct.unpack('<H', read_data[x[0]:x[-1]+1])[0] for x in l_i]
r_data = [struct.unpack('<H', read_data[x[0]:x[-1]+1])[0] for x in r_i]

#### NOW ITS IN INTS! CONVERT TO [-1, 1] ### VALUES ASSUME 16BIT
l_norm = [x/((shortrange/2)-1) if x<=((shortrange/2)-1) else -((shortrange-x)/(shortrange/2)) for x in l_data]
r_norm = [x/((shortrange/2)-1) if x<=((shortrange/2)-1) else -((shortrange-x)/(shortrange/2)) for x in r_data]

# check
print(l_norm[:10])
print(r_norm[:10])

#### convert from [-1, 1] back to short ### VALUES ASSUME 16BIT
l_short = [int(floor(((x/2)+1)*shortrange)) if x<0 else int(floor((x/2)*(shortrange-1))) for x in l_norm]
r_short = [int(floor(((x/2)+1)*shortrange)) if x<0 else int(floor((x/2)*(shortrange-1))) for x in r_norm]

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
read_wav.close()
write1_wav.close()
write2_wav.close()