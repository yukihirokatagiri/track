import cv2

img = cv2.imread("UnityChan.png")

size = 64
for y in range(4):
    yy = y * size

    for x in range(7):
        xx = x * size

        copied = img.copy()
        cropped = copied[yy:yy+size, xx:xx+size]
        resized = cv2.resize(cropped, (size, size))

        cv2.imwrite(f"{y}-{x}.png", resized)
        print(x * size, y * size)
