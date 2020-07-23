import requests
import geopy
import os
from geopy.distance import geodesic #Medir distancias
from geopy.geocoders import Nominatim #Geolocalización
geolocator = Nominatim(user_agent="TP_ALGORITMOS")
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image

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

def grafico_caracteristicas_precipitacion(años,datos):
    '''
        Pre:Recibe una lista con los años, una lista datos para ubicarlos en el grafico.
        Post:Ninguna, demarca instrucciones en el grafico a mostrar la funcion que le llama.
    '''
    plt.bar(años[0],datos[0], label= f"{datos[0]}Mm", width=0.5, color = "blue")
    plt.bar(años[1],datos[1], label= f"{datos[1]}Mm", width=0.5, color = "orange")
    plt.bar(años[2],datos[2], label= f"{datos[2]}Mm", width=0.5, color = "black")
    plt.bar(años[3],datos[3], label= f"{datos[3]}Mm", width=0.5, color = "pink")
    plt.bar(años[4],datos[4], label= f"{datos[4]}Mm", width=0.5, color = "red")    

def grafico_caracteristicas_humedad(años,datos):
    '''
        Pre:Recibe una lista con las fechas, una lista datos para ubicarlos en el grafico.
        Post:Ninguna, demarca instrucciones en el grafico a mostrar la funcion que le llama.
    '''
    plt.bar(años[0],datos[0], label= f"{datos[0]}%", width=0.5, color = "blue")
    plt.bar(años[1],datos[1], label= f"{datos[1]}%", width=0.5, color = "orange")
    plt.bar(años[2],datos[2], label= f"{datos[2]}%", width=0.5, color = "black")
    plt.bar(años[3],datos[3], label= f"{datos[3]}%", width=0.5, color = "pink")
    plt.bar(años[4],datos[4], label= f"{datos[4]}%", width=0.5, color = "red")

def grafico_caracteristicas_temperatura(años,datos):
    '''
        Pre:Recibe una lista con los años o fechas, una lista datos para ubicarlos en el grafico.
        Post:Ninguna, demarca instrucciones en el grafico a mostrar la funcion que le llama.
    '''
    plt.bar(años[0],datos[0], label= f"{datos[0]}°C", width=0.5, color = "blue")
    plt.bar(años[1],datos[1], label= f"{datos[1]}°C", width=0.5, color = "orange")
    plt.bar(años[2],datos[2], label= f"{datos[2]}°C", width=0.5, color = "black")
    plt.bar(años[3],datos[3], label= f"{datos[3]}°C", width=0.5, color = "pink")
    plt.bar(años[4],datos[4], label= f"{datos[4]}°C", width=0.5, color = "red")
    
def estudio_datos_max(años,datos,busqueda, historico):
    '''
        Pre:Recibe una lista con los años, una lista datos para colocar los maximos, una palabra para
        hacer la busqueda en el dataframe.
        Post:Ninguna, deja a la funcion que le llama con la lista datos a utilizar completa y la lista
        años con la fecha con maxima temperatura.

    '''
    fechas = [0,0,0,0,0]#Fecha en que hubo mayor temperatura y mayor milimetros de lluvia
    for i in range(0,len(historico["Date"])):
        read = historico["Date"][i]
        posicion = 0
        
        for año in años:
            if (año in read) == True:
                posicion = años.index(año)
                
        if historico[busqueda][i]>datos[posicion]:
            datos[posicion]=historico[busqueda][i]#temperatura o milimetros de lluvia maximo en dia
            fechas[posicion]=historico["Date"][i]
            
        if i==len(historico["Date"])-1:
            for i in range(0,len(fechas)):
                años[i]=fechas[i]

def estudio_datos_promedios(años,datos,busqueda,historico):
    cantidad_dias = [0,0,0,0,0]
    '''
        Pre:Recibe una lista con los años, una lista datos para sumar los datos, una palabra para
        hacer la busqueda en el dataframe.
        Post:Ninguna, deja a la funcion que le llama con la lista datos a utilizar completa.

    '''
    for i in range(0,len(historico["Date"])-1):
        read = historico["Date"][i]
        posicion = 0
        for año in años:
            if (año in read) == True:
                posicion = años.index(año)
        datos[posicion] += historico[busqueda][i]
        cantidad_dias[posicion] += 1
        
    for i in range (0,len(cantidad_dias)):
        datos[i]=datos[i]/cantidad_dias[i]
                
def temperatura_lluvia_max(historico,busqueda):
    '''
        Pre:Recibe un dataframe y una palabra para estudiar una columna en el dataframe.
        Post:Muestra en pantalla un grafico.

    '''
    años = ["2013","2014","2015","2016","2017"]
    datos=[0,0,0,0,0]
    estudio_datos_max(años,datos,busqueda,historico)
    if busqueda=="Precipitation":
        #Caractersticas del grafico
        grafico_caracteristicas_precipitacion(años,datos)
        #titulo y nombre de ejes
        plt.title("Dia Maximo en mm de lluvia")
        plt.ylabel("Mm de lluvia")
        plt.xlabel("Dia")
        #mostrar
        plt.legend()
        plt.show()
    elif busqueda == "Max Temperature" :
        #Caractersticas del grafico
        grafico_caracteristicas_temperatura(años,datos)
        #titulo y nombre de ejes
        plt.title("Dia con max temperatura en un año")
        plt.ylabel("Temperatura")
        plt.xlabel("Dia")
        #mostrar
        plt.legend()
        plt.show()
        
        
def temperatura_humedad(historico,busqueda):
    '''
        Pre:Recibe un dataframe y una palabra para estudiar una columna en el dataframe.
        Post:Muestra en pantalla un grafico.

    '''
    años = ["2013","2014","2015","2016","2017"]
    datos=[0,0,0,0,0]
    estudio_datos_promedios(años,datos,busqueda,historico)
    if busqueda == "Relative Humidity":
        datos = list(map(lambda x:x*100//1, datos))
    #Caracteristicas del grafico
    if busqueda == "Max Temperature":
        grafico_caracteristicas_temperatura(años,datos)
    else:
        grafico_caracteristicas_humedad(años,datos)
    #titulo y nombre de ejes
    plt.title(f"Promedio de {busqueda}")
    plt.ylabel(busqueda)
    plt.xlabel("Año")
    #mostrar
    plt.legend()
    plt.show()   

def inicio():
    '''
        Pre:Ninguna
        Post:Muestra en pantalla las opciones a usuario.

    '''
    historico = pd.read_csv("weatherdata--389-603.csv")
    entrada = True
    while entrada == True:
        print("\n------BIENVENIDO A CONOCER LOS REGISTROS DE LA ZONA FERTIL Y PRODUCTORA ARGENTINA------\n")
        print("1)Marque 1 para ver el gráfico con el promedio de datos anuales de los últimos 5 años.")
        print("2)Marque 2 para ver el gráfico con el promedio de humedad de los últimos 5 años.")
        print("3)Marque 3 para ver el gráfico con los milímetros máximos de lluvia de los últimos 5 años.")
        print("4)Marque 4 para ver el gráfico con la temperatura máxima de los últimos 5 años.")
        print("0)Marque 0 para salir.")
        opcion=input("Marque la opcion deseada: ")
        while opcion!="1" and opcion!="2" and opcion!="3" and opcion!="4" and opcion!="0":
            opcion=input("Marque una opcion valida: ")
        if opcion == "1":
            busqueda = "Max Temperature"
            temperatura_humedad(historico,busqueda)
        elif opcion=="2":
            busqueda = "Relative Humidity"
            temperatura_humedad(historico,busqueda)
        elif opcion=="3":
            busqueda="Precipitation"
            temperatura_lluvia_max(historico,busqueda)
        elif opcion=="4":
            busqueda="Max Temperature"
            temperatura_lluvia_max(historico,busqueda)
        elif opcion=="0":
            entrada=False

def validacion_csv():
    '''
        Pre: Ninguna.
        Post: Muestra en pantalla un mensaje de no encontrar el archivo.
    '''
    try:
        archivo=open("weatherdata--389-603.csv")
        inicio()
    except:
        print("\nHAY PROBLEMAS DE CONEXION\n")

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

def borrarPantalla(): #Definimos la función estableciendo el nombre que queramos
    if os.name == "posix":
       os.system ("clear")
    elif os.name == "ce" or os.name == "nt" or os.name == "dos":
       os.system ("cls")

def geolocalizacion_por_nombre():
    lugar = input('Ingrese su ubicacion: ')
    try:
        location = geolocator.geocode(lugar, country_codes='ar', addressdetails=True)
    except AttributeError:
        print(f'No se encontro {lugar}')
        location = None
    except geopy.exc.GeocoderServiceError:
        print('Fallo la conexión...')
        location = None

    if location != None:
        ubicacion = location.raw
        provincia = ubicacion['address']['state']
        try:
            ciudad = ubicacion['address']['city']
        except KeyError:
            try:
                ciudad = ubicacion['address']['village']
            except KeyError:
                ciudad = None
    else:
        ciudad = None
        provincia = None

    diccionario = {'Ciudad': ciudad, 'Provincia': provincia, 'Lugar': location}
    return diccionario

def verificar_coordenadas(coordenadas):
    """
        Pre: Recibe una tupla con las coordenadas
        Post: Devulve un diccionario con un booleano, segun si la conexion fue exitosa o no, y la ubicacion en forma de diccionario
    """
    coordanadas_validas = False
    problemas_conexion = False
    conexion = False
    ubicacion = None
    while coordanadas_validas == False and problemas_conexion == False:
        try:
            location = geolocator.reverse(coordenadas)
            ubicacion = location.raw
            conexion = True
            coordanadas_validas = True
            
        except TypeError:
            print('Direccion invalida...')
            latitud = input("lat: ")
            longitud = input('long: ')
            coordenadas = (latitud, longitud)
            coordanadas_validas = False
        except ValueError:
            print('Coordenadas invalidas, intente nuevamente')
            latitud = input("lat: ")
            longitud = input('long: ')
            coordenadas = (latitud, longitud)
            coordanadas_validas = False
        except geopy.exc.GeocoderServiceError:
            print('Fallo la conexión...')
            problemas_conexion = True
        
    return {'conexion': conexion, 'ubicacion': ubicacion, 'Lugar': location}
            

def geolocalizacion_por_coordenadas():
    """
        Post: Devuelve la ciudad y la provincia de una lat y long ingresados en un diccionario, ante un error retorna None
    """
    print('Ingrese a continuacion las coordenadas')
    latitud = input('Latitud: ')
    longitud = input('Longitud: ')
    coordenadas = (latitud, longitud)
    
    geolocalizacion = verificar_coordenadas(coordenadas)
    if geolocalizacion['conexion'] == True:
        ubicacion = geolocalizacion['ubicacion']

        try:
            provincia = ubicacion['address']['state']
        except KeyError:
            dic = ubicacion['address']
            clave = (list(dic.keys()))[0]
            provincia = dic[clave]

        try:
            ciudad = ubicacion['address']['city']
        except KeyError:
            try:
                ciudad = ubicacion['address']['town']
            except KeyError:
                ciudad = None
        
    else:
        print('Error de conexion...')
        provincia = None
        ciudad = None

    return {'Ciudad': ciudad, 'Provincia': provincia, 'Lugar': geolocalizacion['Lugar']}

def hallar_al_usuario_manualmente():
    '''
        Pre: Ninguna, luego pide al usuario los datos de su localización
        Post: Retorna un diccionario con la clave Ciudad y Provincia con los datos del usuario
    '''
    print("A continuación ingrese la ubicación desde la cuál está usando nuestra aplicación, primero la abreviación de su provincia y luego su ciudad")
    provincia_usuario = ubicar_provincia("Ingrese la abreviación de su provincia \nEjemplo: Buenos Aires se abrevia como BA, Catamarca como CA. \nIngrese aquí: ")
    ciudad_usuario = ciudad_en_mayusculas("Ingrese el nombre de la ciudad: ")
    return {"Ciudad":ciudad_usuario, "Provincia": provincia_usuario}

def hallar_usuario():
    """
        Pre: Ninguna, permiter hallar la ubicacion por geolocalizacion, y, en caso de un fallo ingresando los datos manualmente
        Post: Retorna, en ambos casos, un diccionario con la ciudad y provincia del usuario
    """
    ubicacion_correcta = False
    while ubicacion_correcta == False:
        print('Elija como ingresar su ubicación: ')
        print('1. Por nombre | 2. Por geolocalización\n')
        opcion = validar_entrada(2)

        if opcion == 1:
            ubicacion = geolocalizacion_por_nombre()
            lugar = ubicacion['Lugar']
        else:
            ubicacion = geolocalizacion_por_coordenadas()
            lugar = ubicacion['Lugar']

        if ubicacion['Ciudad'] == None:
            print('Algo salio mal, ingrese su ubicacion nuevamente\n')
            ubicacion = hallar_al_usuario_manualmente()
            lugar = ubicacion['Ciudad'] + ', ' + ubicacion['Provincia']
        
        print(f'Usted está en {lugar}? \n1. Si\n2. No')
        opcion = validar_entrada(2)
        if opcion == 1:
            ubicacion_correcta = True
        else:
            borrarPantalla()
            print('Agregue informacion. Revise la escritura.\n')
            ubicacion_correcta = False
    return ubicacion

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
            print(f"No sé encontro la ciudad exacta pero lo más parecido es la ciudad de {diccionario['name']} ")
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
                diccionario = geolocalizacion_por_coordenadas()
                print(diccionario)
                localizacion = diccionario['Ciudad']
                if localizacion == None:
                    terminar = True
                else:
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
        ubicacion_usuario = hallar_usuario()

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
                validacion_csv()
            else:
                menu_de_acciones(opcion,ubicacion_usuario)
                cerrar_menu = False

        if opcion == 8:
            cerrar_programa = True
        else:
            cerrar_programa = False
    print('Fin del programa\nHasta la proxima!')
main()








