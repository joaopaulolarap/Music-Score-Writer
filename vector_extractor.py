import cv2
import numpy as np

img = cv2.imread('dot.png')

a = []
b = []

x_offset = 4
y_offset = 0

def get_image_dimentions(img):
    rows = len(img)
    columns = len(img[0])
    return rows, columns

rows, columns = get_image_dimentions(img)

for i in range (rows):
    for j in range (columns):
            if img[i][j][0] == 0:
                a.append(i - x_offset)
                b.append(j - y_offset)

c = [a, b]

with open("dot.txt", "w") as file:
    for x in zip(*c):
        file.write("{0}\t{1}\n".format(*x))

cv2.imshow("lala", img)
cv2.waitKey()



