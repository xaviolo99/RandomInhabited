import pickle
from PIL import Image
import numpy as np
import time

Image.MAX_IMAGE_PIXELS = 120955560
X = 14190
Y = 8524

# MAIN

# Load our files!

im = Image.open("source/countries.tif")
chunk_country = np.array(im, dtype='uint8')

im = Image.open("source/settlement.tif")
chunk_settle = np.array(im, dtype='int8')
 
##np.unique(chunk_country)
##np.unique(chunk_settle)

print("All Loaded!\n")

# Get candidates

print("Getting candidates...")
candidates = set()
for y in range(Y):
    if y % 1000 == 0:
        print(str(round(y/Y * 100))+"%")
    for x in range(X):
        if chunk_settle[y][x] != 10 and chunk_country[y][x] == 255:
            candidates.add(y * 14190 + x)
print("All candidates gotten!")
print("Total candidates:", len(candidates))

# Iterate updates until no changes

print("\nExpanding our countries...")
changes = 1
count = 0
while changes:
    print(len(candidates))
    changes = 0
    t = time.time()
    count += 1
    print("\nRound", count)
    for encoded in candidates.copy():
        y = encoded // 14190
        x = encoded % 14190
        
        if x > 0 and chunk_country[y][x - 1] != 255:
            chunk_country[y][x] = chunk_country[y][x - 1]
            candidates.remove(encoded)
            changes += 1
            continue
        if x < X - 1 and chunk_country[y][x + 1] != 255:
            chunk_country[y][x] = chunk_country[y][x + 1]
            candidates.remove(encoded)
            changes += 1
            continue
        if y > 0 and chunk_country[y - 1][x] != 255:
            chunk_country[y][x] = chunk_country[y - 1][x]
            candidates.remove(encoded)
            changes += 1
            continue
        if y < Y - 1 and chunk_country[y + 1][x] != 255:
            chunk_country[y][x] = chunk_country[y + 1][x]
            candidates.remove(encoded)
            changes += 1
            continue

        if x > 0 and y > 0 and chunk_country[y - 1][x - 1] != 255:
            chunk_country[y][x] = chunk_country[y - 1][x - 1]
            candidates.remove(encoded)
            changes += 1
            continue
        if x < X - 1 and y < Y - 1 and chunk_country[y + 1][x + 1] != 255:
            chunk_country[y][x] = chunk_country[y + 1][x + 1]
            candidates.remove(encoded)
            changes += 1
            continue
        if y > 0 and x < X - 1 and chunk_country[y - 1][x + 1] != 255:
            chunk_country[y][x] = chunk_country[y - 1][x + 1]
            candidates.remove(encoded)
            changes += 1
            continue
        if y < Y - 1 and x > 0 and chunk_country[y + 1][x - 1] != 255:
            chunk_country[y][x] = chunk_country[y + 1][x - 1]
            candidates.remove(encoded)
            changes += 1
            continue
        
    print("Changes:", changes)
    print("Candidates Left:", len(candidates))
    print("Time: "+str(round(time.time() - t, 1))+"s")

# Save Results

result = Image.fromarray(chunk_country, mode='L')
result.save("countries.tif", compression='tiff_deflate')
