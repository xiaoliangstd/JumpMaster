import cv2 as cv 
import numpy as np 


img = cv.imread('41.png',-1)


cv.rectangle(img,(20,20),(150,150),(255,25,25),5)


cv.imwrite('41resave.png',img)
cv.waitKey(0)
cv.destroyAllWindows()