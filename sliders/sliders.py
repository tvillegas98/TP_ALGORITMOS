import cv2 as cv
import numpy as np

imagen = cv.imread("radar.jpg")
hsv = cv.cvtColor(imagen, cv.COLOR_BGR2HSV)

def nothing(x):
    pass

#Creo una ventana de sliders
cv.namedWindow('Parametros')
cv.createTrackbar('Hue Minimo','Parametros',0,179,nothing)
cv.createTrackbar('Hue Maximo','Parametros',0,179,nothing)
cv.createTrackbar('Saturation Minimo','Parametros',0,255,nothing)
cv.createTrackbar('Saturation Maximo','Parametros',0,255,nothing)
cv.createTrackbar('Value Minimo','Parametros',0,255,nothing)
cv.createTrackbar('Value Maximo','Parametros',0,255,nothing)
cv.createTrackbar('Kernel X', 'Parametros', 1, 30, nothing)
cv.createTrackbar('Kernel Y', 'Parametros', 1, 30, nothing)

print("\nPulsa 'ESC' para salir")

while True:
    #Leemos los sliders y guardamos los valores de H,S,V para construir los rangos:
  hMin = cv.getTrackbarPos('Hue Minimo','Parametros')
  hMax = cv.getTrackbarPos('Hue Maximo','Parametros')
  sMin = cv.getTrackbarPos('Saturation Minimo','Parametros')
  sMax = cv.getTrackbarPos('Saturation Maximo','Parametros')
  vMin = cv.getTrackbarPos('Value Minimo','Parametros')
  vMax = cv.getTrackbarPos('Value Maximo','Parametros')

  color_bajos=np.array([hMin,sMin,vMin])
  color_altos=np.array([hMax,sMax,vMax])
 
  kernelx = cv.getTrackbarPos('Kernel X', 'Parametros')
  kernely = cv.getTrackbarPos('Kernel Y', 'Parametros')

  kernel = np.ones((kernelx,kernely),np.uint8)

  mascara = cv.inRange(hsv, color_bajos, color_altos)
  mascara = cv.morphologyEx(mascara, cv.MORPH_CLOSE, kernel)
  mascara = cv.morphologyEx(mascara, cv.MORPH_OPEN, kernel)

  cv.imshow('Original',imagen)
  cv.imshow('Mascara',mascara)
  k = cv.waitKey(5) & 0xFF
  if k == 27:
    break
cv.destroyAllWindows()