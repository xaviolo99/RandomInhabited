from PIL import Image
import numpy as np
from random import uniform
import math

Image.MAX_IMAGE_PIXELS = 649476000

## Choose desired number (code will only locate from specified level and above levels)
## 10 = WATER
## 11 = UNHABITED LAND
## 12 = SPARSELY HABITATED LAND
## 13 = RURAL VILLAGE
## 21 = SUBURBS
## 22 = SMALL TOWN
## 23 = BIG TOWN
## 30 = CITY

LEVEL = 30 # A level of 30 will return a random city

im = Image.open("settlement.tif")
settle = np.array(im, dtype='int8')

valid = False

while not valid:
    y = uniform(0, 8524)
    x = uniform(0, 14190)

    if settle[int(y)][int(x)] >= LEVEL:
        valid = True
        
y /= 8524
x /= 14190

max_lat = math.sin(math.acos(1 / math.sqrt(10)))

lat = math.asin((0.5 - y) * 2 * max_lat) * 180 / math.pi
lon = (x * 360) - 180

print(round(lat, 6), round(lon, 6))
