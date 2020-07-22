import cv2
import numpy as np
from PIL import Image

PROVINCIAS_CENTRO= [ 
    "Viedma", "Neuquen", "Bahía Blanca", 
    "Mar del Plata", "Santa Rosa", "La Plata",
    "C.A.B.A", "Pergamino", "San Luis", "Mendoza",
    "Paraná", "Santa Fe", "San Juan", "Cordoba",
    "La Rioja", "Mercedes"
]

COLORES = {
    "Azul": [np.array([110,130,200]), np.array([125,255,255]), "lloviznas"],
    "Celeste":[np.array([75,130,130]), np.array([110,200,255]), "lluvias débiles"],
    "Verde": [np.array([45,130,130]), np.array([65,200,255]) ,"lluvias suaves"],
    "Amarillo" : [np.array([20,130,130]), np.array([35,200,255]), "lluvias moderadas"],
    "Rojo bajo":[np.array([0,70,70]),np.array([10,255,255]), "lluvias intensas"],
    "Rojo alto": [np.array([166,255,130]), np.array([179,255,255]), "tormentas"],
    "Magenta": [np.array([140,255,130]), np.array([165,255,255]), "chubascoso o granizos"]
}

CONSTANTE_REGLA_3_SIMPLES = 30.747223602 #Equivale a 100km reales
BLANCO_BGR_MIN = np.array([245,245,245])
BLANCO_BGR_MAX = np.array([255,255,255])
KERNEL_CAP = np.ones((3,3), np.uint8)
KERNEL = np.ones((1,1), np.uint8)

def verificar_imagen():
    '''
        Verifica si existe imagen en el directorio del programa
    '''
    try:
        Image.open("Radar_4.png","r")
        return True
    except FileNotFoundError:
        print("No se ha podido detectar la imagen en la carpeta")
        return False

def hallar_coordenadas(contorno_blanco, imagen_original):
    '''
        Pre: Recibe la imagen original y los arrays del contorno, luego
        halla los centroides en la imagen
        Post: Retorna un diccionario con las coordenadas de las ciudades ubicadas en la imagen
    '''

    coordenadas = {}
    for (i,c) in enumerate(contorno_blanco):
        momentos_b = cv2.moments(c)
        if(momentos_b['m00'] == 0):
            momentos_b['m00'] = 1
        coordenada_x_b = int(momentos_b['m10']/momentos_b['m00'])
        coordenada_y_b = int(momentos_b['m01']/momentos_b['m00'])
        #cv2.putText(imagen_original,f"{str(i+1)}",(coordenada_x_b-15,coordenada_y_b+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0,0,255],1,cv2.LINE_AA)
        coordenadas[PROVINCIAS_CENTRO[i]] = [coordenada_x_b, coordenada_y_b]
    return coordenadas

def hallar_contornos_blancos(imagen_original):
    '''
        Pre:Recibe la iamgen original, luego crea una mascara binaria
        con el color blanco para hallar el contorno de las ciudades
        Post: Retorna el contorno blanco en forma de arrays de numpy
    '''
    mascara_blanca = cv2.inRange(imagen_original, BLANCO_BGR_MIN, BLANCO_BGR_MAX)
    mascara_blanca = cv2.morphologyEx(mascara_blanca, cv2.MORPH_CLOSE, KERNEL_CAP)
    mascara_blanca = cv2.morphologyEx(mascara_blanca, cv2.MORPH_OPEN, KERNEL_CAP)
    contorno,_ = cv2.findContours(mascara_blanca, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return contorno

def analizar_tormenta(imagen_original, gama_baja, gama_alta, mensaje_meteoreologico, coordenadas_ciudades):
    '''
        Pre: Recibe la imagen_original, la gama baja de colores y la alta,
        un mensaje de alerta dependiendo del color y las coordenadas de las 
        ciudades en la imagen
        Post: No retorna nada, halla las mascaras binarias color por color, luego
        halla las coordenadas del color y halla las distancias de la ciudad respecto un color,
        si esta cerca del color, lo muestra en pantalla       
    '''
    imagen_hsv = cv2.cvtColor(imagen_original, cv2.COLOR_BGR2HSV)

    mascara = cv2.inRange(imagen_hsv, gama_baja, gama_alta)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, KERNEL)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, KERNEL)
    
    contorno,_ = cv2.findContours(mascara, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    aviso = False
    for ciudad,coordenadas in coordenadas_ciudades.items():
        aviso = False
        for c in contorno:
            m = cv2.moments(c)
            if(m['m00'] == 0):
                m['m00'] = 1
            coordenada_x = int(m['m10']/m['m00'])
            coordenada_y = int(m['m01']/m['m00'])
            vector_ciudad = np.array([coordenadas])
            vector_color = np.array([coordenada_x,coordenada_y])
            norma = np.linalg.norm(vector_ciudad-vector_color)
            distancia_real = (norma * CONSTANTE_REGLA_3_SIMPLES)/100
            if(distancia_real <= 20  and aviso == False):
                aviso = True
                print(f"Se aproximan {mensaje_meteoreologico} a la ciudad de {ciudad} a una distancia de {distancia_real} km")
    
def iterar_colores():
    '''
        Pre: Ninguna, carga la imagen y luego hace llamados de funciones para trabajar en la imagen
        Post: Ninguno.
    '''   
    imagen_detectada = verificar_imagen()
    if(imagen_detectada == True):
        imagen_original = cv2.imread("Radar_4.png")
        contorno_blanco = hallar_contornos_blancos(imagen_original)
        coordenadas_ciudades = hallar_coordenadas(contorno_blanco, imagen_original)
        for color in COLORES.values():
            analizar_tormenta(imagen_original, color[0], color[1],color[2], coordenadas_ciudades)
        print("Presione una tecla para cerrar la ventana...")
        cv2.imshow("Imagen", imagen_original)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

iterar_colores()