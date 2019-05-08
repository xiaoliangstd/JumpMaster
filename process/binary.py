import cv2 as cv 
import numpy as np 

mask = cv.imread('mask.png',-1)


cv.imshow('mask',mask)

cv.waitKey(0)
cv.destroyAllWindows()

