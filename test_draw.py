import cv2

img = cv2.imread('pautas-1.jpg')

cv2.imshow("lala", img)
cv2.waitKey()

f = open("half_note_down.txt", "r")

x, y = [], []
for l in f:
    row = l.split()
    x.append(row[0])
    y.append(row[1])

lenght = len(x)

for i in range(lenght):
    #for j in range (11):
    
    img[187 + int(x[i])][225 + int(y[i])] = [0, 0, 0]


cv2.imshow("lala", img)
cv2.waitKey()
