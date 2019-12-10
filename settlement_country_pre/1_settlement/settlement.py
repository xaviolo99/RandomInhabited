from PIL import Image
import numpy as np
import math

import time
import os
import psutil

Image.MAX_IMAGE_PIXELS = 649476000
EPSI_PI = math.pi - 0.00000000001

# -200 = Undefined -> 0
# 10 = Water
# 11 = Mostly Uninhabited
# 12 = Rural Dispersed Area
# 13 = Village
# 21 = Suburbs
# 22 = Semi-Dense Town
# 23 = Dense Town
# 30 = City

# Input: relative x, y in range [0, 1] in the mollweide projection
# Output: latitude and longitude of that point (in radians)
def invMollweide(x, y, theta): 
    x = x * 2 - 1
    y = y * 2 - 1
    
    theta = math.asin(y)
    lat = math.asin((2 * theta + math.sin(2 * theta)) / math.pi)
    lon = math.pi * x / math.cos(theta)
    
    if abs(lon) > math.pi:
        return "OOB", 0
    
    return lat, lon

# Input: latitude and longitude of a point (in radians)
# Output: relative x, y in range [0, 1] in ParkInk's projection of the point
park_constant = 2 * math.sin(math.acos(1 / math.sqrt(10)))
park_limit = math.acos(1 / math.sqrt(10))
def toParkInk(lat, lon):
    return math.sin(lat) / park_constant + 0.5, lon / math.pi + 0.5

# MAIN

# Open image and create 'pixel'

t = time.time()

im = Image.open("source/settlement.tif")#, mode='F')
pixel = np.array(im, dtype='int16')
pixel[pixel == -200] = -1
pixel = pixel.astype('int8')

# Convert to a genuine mollweide (basically, we want a 36080x18040 image instead of a 36082x18000 one)

pixel = pixel[:, 1:-1]
mask = np.full([20, 36080], -1, dtype='int8')
pixel = np.concatenate((mask, pixel), axis=0)
pixel = np.concatenate((pixel, mask), axis=0)

print("Image Loaded! (" + str(round(time.time() - t, 2)) + "s)")
process = psutil.Process(os.getpid())
print("Memory used:", round(process.memory_info().rss/1024/1024), "MB\n")

# Create and populate 'chunk_first' and 'chunk_delta'

t = time.time()
print("Imputating...")

chunk = np.zeros([8524, 14190], dtype='int8')

point_offset = 1117 # extracted manually, those are the pixels in parkinks latitude range (with code below)
##for i in range(point_offset, len(pixel) - point_offset + 1): 
##    theta = math.asin(i / len(pixel) * 2 - 1)
##    cos_theta = math.cos(theta)
##    
##    lat = math.asin((2 * theta + math.sin(2 * theta)) / math.pi)
##    y_park = (math.sin(lat) / park_constant + 0.5) * 8524
##    print(y_park)

for i in range(point_offset, len(pixel) - point_offset + 1): 
    theta = math.asin(i / len(pixel) * 2 - 1)
    cos_theta = math.cos(theta)
    
    lat = math.asin((2 * theta + math.sin(2 * theta)) / math.pi)
    y_park = (math.sin(lat) / park_constant + 0.5) * 8524
    
    if i % 300 == 0:
        print(str(round((i - point_offset) / (len(pixel) - 2 * point_offset) * 100, 1)) + "%")
        
    for j in range(len(pixel[0]) + 1):
        lon = math.pi * (j / len(pixel[0]) * 2 - 1) / cos_theta
        
        if abs(lon) < EPSI_PI:
            x_park = (lon / (2 * math.pi) + 0.5) * 14190

            x_chunk = math.floor(x_park)
            y_chunk = math.floor(y_park)
            
            if i != len(pixel):
                if j != len(pixel[0]) and chunk[y_chunk, x_chunk] < pixel[i, j]:
                    chunk[y_chunk, x_chunk] = pixel[i, j]
                if j != 0 and chunk[y_chunk, x_chunk] < pixel[i, j - 1]:
                    chunk[y_chunk, x_chunk] = pixel[i, j - 1]
            if i != 0:
                if j != len(pixel[0]) and chunk[y_chunk, x_chunk] < pixel[i - 1, j]:
                    chunk[y_chunk, x_chunk] = pixel[i - 1, j]
                if j != 0 and chunk[y_chunk, x_chunk] < pixel[i - 1, j - 1]:
                    chunk[y_chunk, x_chunk] = pixel[i - 1, j - 1]

print("All chunks imputated! (" + str(round(time.time() - t, 2)) + "s)")
print("Memory used:", round(process.memory_info().rss/1024/1024), "MB\n")

# Save the results

t = time.time()
print("Saving...")

np.save('settlement.npy', chunk)

result = Image.fromarray(chunk, mode='L')
result.save("settlement.tif", compression='tiff_deflate')

print("All saved! (" + str(round(time.time() - t, 2)) + "s)")
##print("Memory used:", round(process.memory_info().rss/1024/1024), "MB\n")

