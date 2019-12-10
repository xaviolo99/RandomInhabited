import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import math

import pickle
from PIL import Image

# AUX

prk_const = 2 * math.sin(math.acos(1 / math.sqrt(10)))
def toParkInk(array):
    array[:, 0] = (array[:, 0] / 360 + 0.5) * 14190
    array[:, 1] = (np.sin(array[:, 1] / 180 * math.pi) / prk_const + 0.5) * 8524

def parsePolygon(polygon):
    struct = []
    struct.append(np.array(polygon.exterior))
    toParkInk(struct[0])
    struct.append([])
    for interior in polygon.interiors:
        struct[1].append(np.array(interior))
        toParkInk(struct[1][-1])
    return struct

def getArea(polygon):
    area = 0
    for e in range(len(polygon)):
        area += polygon[e - 1][0] * polygon[e][1]
        area -= polygon[e - 1][1] * polygon[e][0]
    return abs(area) / 2 * 4

def parseEdge(breaks, x1, y1, x2, y2):
    min_y, max_y = (y1, y2) if y1 < y2 else (y2, y1)
            
    val = math.ceil(min_y + 0.5) - 0.5
    while val < max_y:
        breaks[int(val) - start].append(x1 + (val - y1) / (y2 - y1) * (x2 - x1))
        val += 1
    

# MAIN

# Extract data and polygons (plus convert to ParkInk projection) for each country

shapefile = gpd.read_file("source/ne_10m_admin_0_countries_lakes.shp")

selection = shapefile.loc[:, ['NAME_EN', 'SUBREGION', 'POP_EST', 'geometry']]
p_countries = selection.values.tolist()

for i in range(len(p_countries)):
    outp = []
    try:
        for j in range(len(p_countries[i][-1])):
            outp.append(parsePolygon(p_countries[i][-1][j]))
    except:
        outp.append(parsePolygon(p_countries[i][-1]))
    p_countries[i][-1] = outp

bounds = selection.bounds.values
mins = bounds[:, :2]
maxs = bounds[:, 2:]
toParkInk(mins)
toParkInk(maxs)

countries = []
for country in p_countries:
    
    area = 0
    for m_poly in country[-1]:
        area += getArea(m_poly[0])
        for inner in m_poly[1]:
            area -= getArea(inner)
    
    countries.append([country[0], country[1], round(area, 2), country[2], round(country[2] / area, 2), country[-1]])

# COUNTRIES : NAME SUBREGION AREA POP POP_DENSITY GEOMETRY

# Imputate a country to each pixel

chunk_country = np.full([8524, 14190], 255, dtype='uint8')

for c in range(len(countries)):
    lower = math.ceil(mins[c][1] + 0.5) - 0.5
    upper = math.floor(maxs[c][1] + 0.5) - 0.5
    start = int(lower)
    print(start)
    print(upper)
    duration = int(upper - lower + 1)
    
    breaks = [[] for i in range(duration)]

    for m_poly in countries[c][5]:
        for i in range(len(m_poly[0])):
            parseEdge(breaks, *m_poly[0][i - 1], *m_poly[0][i])
        for ext in m_poly[1]:
            for i in range(len(ext)):
                parseEdge(breaks, *ext[i - 1], *ext[i])

    for b in range(duration):
        if start + b < 0 or start + b > 8523:
            continue
        breaks[b] = sorted(breaks[b])
        cntr = 0
        pntr = 0
        for i in range(len(breaks[b])):
            cntr += 1
            if cntr % 2 == 1:
                beg = math.ceil(breaks[b][i] - 0.5)
                end = math.floor(breaks[b][i + 1] + 0.5)
                for j in range(beg, end):
                    chunk_country[8523 - (start + b), j] = c
        
    
    print(countries[c][0], duration)
    
# Save the data

outp_countries = []
for country in countries:
    outp_countries.append(country[:5])
filehandler = open("countries.pickle", 'wb')
pickle.dump(outp_countries, filehandler)
filehandler.close()

##filehandler = open(filename, 'rb') 
##object = pickle.load(filehandler)

result = Image.fromarray(chunk_country, mode='L')
result.save("countries.tif", compression='tiff_deflate')
