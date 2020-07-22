import requests
from geopy.distance import geodesic #Medir distancias
from geopy.geocoders import Nominatim #Geolocalización
geolocator = Nominatim(user_agent="TP_ALGORITMOS")
import cv2
import numpy as np
from PIL import Image


#location = geolocator.geocode(ubicacion, country_codes='ar')
PROVINCIAS = {
        "BA": "Buenos Aires", "CA": "Catamarca", "CH":"Chubut",
        "CB":"Córdoba", "CR":"Corrientes", "ER":"Entre Ríos",
        "FO":"Formosa", "JY":"Jujuy", "LP":"La Pampa", "LR":"La Rioja",
        "MZ": "Mendoza", "MI":"Misiones", "NQ":"Neuquén", "RN":"Río Negro",
        "SA":"Salta", "SJ":"San Juan", "SL":"San Luis", "SC":"Santa Cruz",
        "SF":"Santa Fe", "SE":"Santiago del Estero", 
        "TF":"Tierra del Fuego, Antártida e Islas del Atlántico Sur", 
        "TU":"Tucumán"
        }

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

CONSTANTE_REGLA_3_SIMPLES = 30.747223602 #Equivale a 100km reales (En el archivo de texto adjunto explico de donde sale)
BLANCO_BGR_MIN = np.array([245,245,245])
BLANCO_BGR_MAX = np.array([255,255,255])
KERNEL_CAP = np.ones((3,3), np.uint8)
KERNEL = np.ones((1,1), np.uint8)

def verificar_imagen():
    '''
        Verifica si existe imagen en el directorio del programa
    '''
    try:
        Image.open("radar.png","r")
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
        imagen_original = cv2.imread("radar.png")
        contorno_blanco = hallar_contornos_blancos(imagen_original)
        coordenadas_ciudades = hallar_coordenadas(contorno_blanco, imagen_original)
        for color in COLORES.values():
            analizar_tormenta(imagen_original, color[0], color[1],color[2], coordenadas_ciudades)
        print("Presione una tecla para cerrar la ventana...")
        cv2.imshow("Imagen", imagen_original)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def verificar_conexion(ruta):
    '''
        Pre: Recibe la ruta, verifica la conexión a internet mediante un try y except
        Post: Retorna un diccionario con un valor booleano en función de si hubo una conexión exitosa o no, y, la respuesta.    
    '''
    print("Conectando...")
    respuesta = None
    valor = False

    try:
        respuesta = requests.get(ruta, timeout = 1)
        valor = True
    except requests.exceptions.Timeout:
        print("Error. La conexión tardo demasiado...  ")
    except requests.exceptions.ConnectionError: 
        print('Error de conexión, revise su conexión de internet.')

    diccionario_respuesta = {'respuesta': respuesta, 'conexion': valor}
    return diccionario_respuesta

def validar_entrada(numero_opciones):
    '''
        Pre: Recibe la cantidad de opciones de entrada
        Post: Retorna la opción validada de tipo int
    '''
    respuesta = input("Ingrese su opción: ")
    while(not respuesta.isnumeric() or 0>=int(respuesta) or int(respuesta)>numero_opciones):
        print("Opción inválida, intente nuevamente")
        respuesta = input("Ingrese su opción: ")
    return int(respuesta)
    
def ubicar_provincia(mensaje_determinado):
    '''
        Pre:Recibe un mensaje determinado para el input, luego mediante la clave ingresada se buscará en el diccionario la provincia
        Post: Devuelve la provincia indicada mediante el diccionario, de tipo str
    '''
    caracteres_provincia = input(mensaje_determinado).upper()
    while(len(caracteres_provincia) != 2 or caracteres_provincia not in PROVINCIAS):
        print("Ingreso erróneo o provincia inexistente, intente nuevamente")
        caracteres_provincia = input(mensaje_determinado).upper()
    provincia = PROVINCIAS[caracteres_provincia]
    return provincia

def ciudad_en_mayusculas(mensaje_determinado):
    """
        PRE: Recibe un mensaje para mostrar por pantalla, la fucion pide el ingrese de una ciudad.
        Post: Devuelve el nombre de la ciudad en mayúsculas.
    """
    entrada = input(mensaje_determinado)
    entrada_lista = entrada.split()

    for i in range(len(entrada_lista)):
        if entrada_lista[i] not in ['de', 'del']:
            entrada_lista[i] = (str(entrada_lista[i]).capitalize())

    salida = " ".join(entrada_lista)
    return salida

def hallar_al_usuario():
    '''
        Pre: Ninguna, luego pide al usuario los datos de su localización
        Post: Retorna un diccionario con la clave Ciudad y Provincia con los datos del usuario
    '''
    ubicacion_ingresada = False
    while(ubicacion_ingresada == False):
        print("A continuación ingrese la ubicación desde la cuál está usando nuestra aplicación, primero la abreviación de su provincia y luego su ciudad")
        provincia_usuario = ubicar_provincia("Ingrese la abreviación de su provincia \nEjemplo: Buenos Aires se abrevia como BA, Catamarca como CA. \nIngrese aquí: ")
        ciudad_usuario = ciudad_en_mayusculas("Ingrese el nombre de la ciudad: ")
        print(f"¿Ústed está en la ciudad de {ciudad_usuario} en la provincia de {provincia_usuario}?\n 1.Si \n 2.No")
        opcion = validar_entrada(2)
        if(opcion == 1):
            ubicacion_ingresada = True
        else:
            print("Si su ubicación no es la indicada, intente nuevamente")
    return {"Ciudad":ciudad_usuario, "Provincia": provincia_usuario}

def verificar_ciudad(respuesta_json, ubicacion_usuario):
    '''
        Pre: Recibe un json de la url weather y el diccionario con la ubicación del usuario, luego compara con los datos del json
        Post: Retorna un valor booleano indicando si la ciudad estaba en los datos json o no
    '''
    ciudad_encontrada = False
    for diccionario in respuesta_json:
        if ubicacion_usuario["Ciudad"] in diccionario["name"] and ciudad_encontrada == False:
            ciudad_encontrada = True
    return ciudad_encontrada

def mostrar_pronostico_provincia(respuesta_json, provincia):
    '''
        Pre:Recibe los datos json de la url weather y la provincia del usuario
        Post:Ninguna, muestra el pronóstico general de la provincia indicada
    '''
    contador = 1
    print("La ciudad no pudo ser encontrada en la base de datos del servicio metereológico, a continuación mostraremos las ciudades más cercanas")
    for diccionarios in respuesta_json:
        if(diccionarios['province'] == provincia and len(respuesta_json)!= 0):
            print("-"*80)
            print(f"AVISOS A NIVEL PROVINCIAL. \n AVISO NÚMERO #{contador}")
            print("-"*80)
            print(f"Provincia: {diccionarios['province']} \nCiudad: {diccionarios['name']} Fecha y Hora: {diccionarios['forecast']['date_time']}")
            print(f"Temperatura mínima: {diccionarios['forecast']['forecast']['0']['temp_min']}°C \nTemperatura máxima: {diccionarios['forecast']['forecast']['0']['temp_max']}°C")
            print(f"Humedad: {diccionarios['weather']['humidity']} % \nVelocidad del viento: {diccionarios['weather']['wind_speed']}km/h")
            print(f"Pronóstico de la mañana: {diccionarios['forecast']['forecast']['0']['morning']['description']}")
            print(f"Pronóstico de la tarde: {diccionarios['forecast']['forecast']['0']['afternoon']['description']}\n")
            print("-"*80)
            contador += 1

def mostrar_pronostico_ciudad(respuesta_json, ciudad, provincia):
    '''
        Pre:Recibe los datos json de la url weather y la ciudad del usuario
        Post: Muestra el pronóstico de la ciudad del usuario, debido a que fue encontrada en los datos json
    '''
    for diccionarios in respuesta_json:
        if(ciudad == diccionarios['name'] and provincia == diccionarios['province']):
            print("-"*80)
            print(f"A CONTINUACIÓN SE DARÁ EL PRONÓSTICO DE LA CIUDAD DE: {ciudad}")
            print("-"*80)
            print(f"Fecha y Hora: {diccionarios['forecast']['date_time']}")
            print(f"Temperatura mínima: {diccionarios['forecast']['forecast']['0']['temp_min']}°C \nTemperatura máxima: {diccionarios['forecast']['forecast']['0']['temp_max']}°C")
            print(f"Humedad: {diccionarios['weather']['humidity']}% \nVelocidad del viento: {diccionarios['weather']['wind_speed']} km/h")
            print(f"Pronóstico de la mañana: {diccionarios['forecast']['forecast']['0']['morning']['description']}")
            print(f"Pronóstico de la tarde: {diccionarios['forecast']['forecast']['0']['afternoon']['description']}\n")
            print("-"*80)
        elif(ciudad in diccionarios['name'] and provincia == diccionarios['province']):
            print("-"*80)
            print(f"No sé encontro la ciudad exacta pero lo más parecido es la ciudad de {diccionarios['name']} ")
            print(f"A CONTINUACIÓN SE DARÁ EL PRONÓSTICO DE LA CIUDAD DE: {diccionarios['name']}")
            print("-"*80)
            print(f"Fecha y Hora: {diccionarios['forecast']['date_time']}")
            print(f"Temperatura mínima: {diccionarios['forecast']['forecast']['0']['temp_min']}°C \nTemperatura máxima: {diccionarios['forecast']['forecast']['0']['temp_max']}°C")
            print(f"Humedad: {diccionarios['weather']['humidity']}% \nVelocidad del viento: {diccionarios['weather']['wind_speed']} km/h")
            print(f"Pronóstico de la mañana: {diccionarios['forecast']['forecast']['0']['morning']['description']}")
            print(f"Pronóstico de la tarde: {diccionarios['forecast']['forecast']['0']['afternoon']['description']}\n")
            print("-"*80)

def pronostico_usuario(ubicacion_usuario):
    '''
        Pre: Recibe el diccionario con la ubicación del usuario
        Post: Ninguno, sigue una serie de procesos para mostrar el pronóstico de la locación del usuario
    '''
    conexion = verificar_conexion("https://ws.smn.gob.ar/map_items/weather") 
    conexion_exitosa = conexion['conexion']

    if conexion_exitosa == True:
        respuesta_json = conexion['respuesta'].json()
        ciudad_verificada = verificar_ciudad(respuesta_json, ubicacion_usuario)

        if ciudad_verificada == False:
            mostrar_pronostico_provincia(respuesta_json, ubicacion_usuario['Provincia'])
        else:
            mostrar_pronostico_ciudad(respuesta_json, ubicacion_usuario['Ciudad'], ubicacion_usuario['Provincia'])
    else:
        print('No se pudo establecer conexion con el Servicio Meteorológico Nacional.')

def alertas_nacionales():
    '''
        Pre:Ninguno, primero recibe los datos de la url indicada en el modulo y luego las muestra
        Post:Niguno, muestra las alertas a nivel nacional
    '''
    conexion = verificar_conexion("https://ws.smn.gob.ar/alerts/type/AL") 
    conexion_exitosa= conexion['conexion']
    
    if conexion_exitosa == True:
        respuesta_json = conexion['respuesta'].json()
        contador = 1

        if len(respuesta_json) != 0:
            print("-"*80)
            print(f"A CONTINUACIÓN SE DARÁ EL PRONÓSTICO A NIVEL NACIONAL")
            print("-"*80)
            for alertas in respuesta_json:
                zonas = [zona for zona in alertas['zones'].values()]
                print("-"*80)
                print(f"AVISO NÚMERO°{contador}")
                print("-"*80)
                print(f"Titulo: {alertas['title']} \nFecha: {alertas['date']} \nHora: {alertas['hour']}")
                print(f"Aviso: {alertas['description']} \n Zonas afectadas: {zonas[0::]}")
                print("-"*80)
                contador += 1
        else:
            print("-"*80, "\n")
            print("NO HAY ALERTAS ACTUALES")
            print("-"*80, "\n")

    else:
        print('No se pudo establecer conexion con el Servicio Meteorológico Nacional.')
        print("-"*80, "\n")
        print("NO HAY ALERTAS ACTUALES")
        print("-"*80, "\n")

def mostrar_pronostico_extendido_ciudad(respuesta_json, ciudad, provincia, dia_pronostico):
    '''
        Pre:Recibe los datos json de la url de pronosticos extendidos, la ciudad del usuario y el nuemero de dias desde la fecha.
        Post: Muestra el pronostico extendido de la ciudad del usuario, debido a que fue encontrada en los datos json
    '''
    for diccionario in respuesta_json:
        if(ciudad == diccionario['name'] and provincia == diccionario['province']):
            print("-"*80)
            print(f"PRONÓSTICO PARA DENTRO DE {dia_pronostico} DÍAS DE LA CIUDAD DE: {ciudad}")
            print("-"*80)
            print(f'MAÑANA:\nTemperatura: {diccionario["weather"]["morning_temp"]}°C\nDescripción: {diccionario["weather"]["morning_desc"]}')
            print(f'TARDE:\nTemperatura: {diccionario["weather"]["afternoon_temp"]}°C\nDescripción: {diccionario["weather"]["afternoon_desc"]}')
            print("-"*80,'\n')
        elif(ciudad in diccionario['name'] and provincia == diccionario['province']):
            print("-"*80)
            print(f"No sé encontro la ciudad exacta pero lo más parecido es la ciudad de {diccionarios['name']} ")
            print(f"PRONÓSTICO PARA DENTRO DE {dia_pronostico} DÍAS DE LA CIUDAD DE: {ciudad}")
            print("-"*80)
            print(f'MAÑANA:\nTemperatura: {diccionario["weather"]["morning_temp"]}\nDescripción: {diccionario["weather"]["morning_desc"]}')
            print(f'TARDE:\nTemperatura: {diccionario["weather"]["afternoon_temp"]}\nDescripción: {diccionario["weather"]["afternoon_desc"]}')
            print("-"*80,'\n')


def pronostico_extendido(ubicacion_usuario):
    '''
        Pre: Recibe el diccionario con la ubicación del usuario
        Post: Ninguno, sigue una serie de procesos para mostrar el pronóstico extendido de la locación del usuario
    '''
    pronosticos = {
                    'dia1': "https://ws.smn.gob.ar/map_items/forecast/1", 
                    'dia2': "https://ws.smn.gob.ar/map_items/forecast/2", 
                    'dia3': "https://ws.smn.gob.ar/map_items/forecast/3"
                  }

    contador = 1
    for ruta in pronosticos:
        conexion = verificar_conexion(pronosticos[ruta]) 
        conexion_exitosa = conexion['conexion']

        if conexion_exitosa == True:
            respuesta_json = conexion['respuesta'].json()
            ciudad_verificada = verificar_ciudad(respuesta_json, ubicacion_usuario)

            if ciudad_verificada == False:
                print(f'No hay información disponible para {ubicacion_usuario["Ciudad"]}')
            else:
                mostrar_pronostico_extendido_ciudad(respuesta_json, ubicacion_usuario['Ciudad'], ubicacion_usuario['Provincia'], contador)

        else:
            print(f'Fallo la conexión para el pronóstico de dentro de {contador} días')

        contador += 1

def geolocalizacion_por_coordenadas():
    """
        Post: Devuelve la provincia de una latitud y longitud ingresadas, en caso de no exitir tal informacion, devuelve el lugar ingresado
    """
    print('Ingrese a continuacion las coordenadas')

    latitud = input('Latitud: ')
    longitud = input('Longitud: ')
    coordenadas = (latitud, longitud)

    coordanadas_validas = False
    while coordanadas_validas == False:
        try:
            location = geolocator.reverse(coordenadas)
            ubicacion = location.raw
            coordanadas_validas = True
        except ValueError:
            print('Coordenadas invalidas, intente nuevamente')
            latitud = input('Latitud: ')
            longitud = input('Longitud: ')
            coordenadas = (latitud, longitud)
            coordanadas_validas = False
    try:
        provincia = ubicacion['address']['state']
    except KeyError:
        dic = ubicacion['address']
        clave = (list(dic.keys()))[0]
        provincia = dic[clave]
    return provincia

def mostrar_alertas(ubicacion_usuario):
    '''
        Pre: Recibe la localizacion 
        Post: Muestra las alertas para la localizacion ingresada
    '''
    conexion = verificar_conexion("https://ws.smn.gob.ar/alerts/type/AL") 
    conexion_exitosa= conexion['conexion']

    if conexion_exitosa == True:
        respuesta_json = conexion['respuesta'].json()
        localizacion = ubicacion_usuario['Provincia']
        terminar = False

        while terminar == False:
            contador = 1

            for diccionario in respuesta_json:
               for region in diccionario['zones']:
                   if localizacion in diccionario['zones'][region]:
                       print("-"*80)
                       print(f'ALERTA NÚMERO° {contador}: {diccionario["zones"][region]}\n')
                       print(f'Fecha: {diccionario["date"]} Hora: {diccionario["hour"]}\n')
                       print(f'Descripción: {diccionario["description"]}\n')
                       print("-"*80)
                       contador += 1

            if contador == 1:
                print(f'\nNo hay alertas para {localizacion}\n')

            print('1. Si desea ver alertas para otra ubicacion por geolocalización')
            print('2. Para salir')
            opcion = validar_entrada(2)
            if opcion == 1:
                localizacion = geolocalizacion_por_coordenadas()
                terminar = False
            else:
                terminar = True
            
    else:
        print('No se pudo establecer conexion con el Servicio Meteorológico Nacional.')

def menu_de_acciones(opcion, ubicacion_usuario):
    '''
        Pre: Opcion de tipo int y ubicación del usuario
        Post: Ninguno.
    '''
    if opcion == 1:
        pronostico_usuario(ubicacion_usuario)
    elif opcion == 2:
        mostrar_alertas(ubicacion_usuario)
    elif opcion == 3:
        alertas_nacionales()
    elif opcion == 5:
        pronostico_extendido(ubicacion_usuario)
    elif(opcion == 6):
        iterar_colores()

def main():
    '''
        Muestra el menú principal
        El programa termina si el usuario ingresa la opción número 7.
    '''
    print("\n¡Bienvenidos a la aplicación del servicio metereológico de Tormenta!\n")
    cerrar_programa = False

    while cerrar_programa == False:
        cerrar_menu = False
        ubicacion_usuario = hallar_al_usuario()

        while cerrar_menu == False:
            print("\n¿Que desea hacer?")
            print("1.Ver el pronóstico para su ciudad(En caso de no haber para su ciudad, se mostrarán las ciudades mas cercanas)")
            print("2.Ver el pronóstico de una ciudad ubicada por geolocalización")
            print("3.Listar las alertas a nivel Nacional") 
            print("4.Graficar el archivo CSV ingresado")
            print("5.Pronóstico extendido de 1,2 y 3 días de una ciudad ingresada por el usuario")
            print("6.Informe de precipitaciones mediante analisis de imagenes de radar")
            print("7.Cambiar su ubicación")
            print("8.Cerrar el programa\n")
            opcion = validar_entrada(8)

            if opcion == 7 or opcion == 8:
                cerrar_menu = True
            elif  opcion == 4:
                #llamar a funcion de graficos
                pass
            else:
                menu_de_acciones(opcion,ubicacion_usuario)
                cerrar_menu = False

        if opcion == 8:
            cerrar_programa = True
        else:
            cerrar_programa = False
    print('Fin del programa\nHasta la proxima!')
main()
#geopy.exc.GeocoderUnavailable:







