import requests #URL
import os #Borrar pantalla
from geopy.geocoders import Nominatim #Geolocalización
import pandas as pd #Leer csv
import matplotlib.pyplot as plt #Mostrar graficos
import cv2 #Analisis de imagen
import numpy as np #Analisis de imagen
from geopy.exc import GeocoderServiceError #Excepciones
from geopy.distance import geodesic #Medir distancias
from geopy.geocoders import Nominatim #Geolocalización

GEOLOCATOR = Nominatim(user_agent = 'TP_ALGORITMOS')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_IMAGEN = os.path.join(BASE_DIR, 'radar.png')
RUTA_CSV = os.path.join(BASE_DIR, 'tabla_de_datos.csv')

URLS_P_EXTENDIDO = {
                    'dia_uno': "https://ws.smn.gob.ar/map_items/forecast/1", 
                    'dia_dos': "https://ws.smn.gob.ar/map_items/forecast/2", 
                    'dia_tres': "https://ws.smn.gob.ar/map_items/forecast/3"
                  }
URL_ALERTAS = "https://ws.smn.gob.ar/alerts/type/AL"
URL_ESTADO_ACTUAL = "https://ws.smn.gob.ar/map_items/weather"

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

def borrar_pantalla():
    if os.name == "posix":
       os.system ("clear")
    elif os.name == "ce" or os.name == "nt" or os.name == "dos":
       os.system ("cls")

def validar_entrada(numero_opciones):
    '''
        Valida las opciones que el programa le entrega al usuario y
        luego las convierte en tipo int.
        #Parametros
        numeros_opciones(int): Cantidad de opciones posibles
        #Retorno
        respuesta(int): La opción elegida por el usuario.

    '''
    respuesta = input("Ingrese su opción: ")
    while(not respuesta.isnumeric() or 0>=int(respuesta) or int(respuesta)>numero_opciones):
        print("Opción inválida, intente nuevamente")
        respuesta = input("Ingrese su opción: ")
    return int(respuesta)

def hallar_coordenadas(contorno_blanco, imagen_original):
    '''
        Halla los centroides de los contornos blancos que representan las ciudades,
        esto se logra mediante el metodo cv2.moments() dentro del for que utiliza
        enumerate(contorno_blanco), es decir, enumero las iteraciones de los contornos.
        Esto representa la cantidad de ciudades encontradas(16).
        el metodo cv2.moments() retorna un diccionario con los momentos de la imagen,
        donde solo me interesan las claves 'm00', 'm10', 'm01' con las cuales hallo
        las coordenadas x e y de la imagen.

        #Parametros 
        contorno_blanco(numpy arrays): Contiene los arrays de los contornos de las ciudades.
        imagen_original(numpy arrays): Contiene la imagen procesada como arrays de numpy.
        #Retorno
        Retorna un diccionario donde sus claves son el nombre de una ciudad y las coordenadas
        de la misma.
    '''
    coordenadas = {}
    for (i,c) in enumerate(contorno_blanco):
        momentos_b = cv2.moments(c)
        if(momentos_b['m00'] == 0): #Evito divisiones por cero
            momentos_b['m00'] = 1
        coordenada_x_b = int(momentos_b['m10']/momentos_b['m00'])
        coordenada_y_b = int(momentos_b['m01']/momentos_b['m00'])
        coordenadas[PROVINCIAS_CENTRO[i]] = [coordenada_x_b, coordenada_y_b]
    return coordenadas

def hallar_contornos_blancos(imagen_original):
    '''
        Crea mascaras de color blanco(Usando la composición de colores BGR) usando cv2.inRange(..), hallando los pequeños circulos que
        representan las ciudades en la imagen ingresada, usando cv2.findContours(..).
        con cv2.morphologyEx(..) elimino el ruido que aparezca en la mascara, es decir
        los pequeños puntos que interfieran con la  mascarad deseada.

        #Nota:el guión de contorno,_ representa la jerarquía del contorno,
        es decir, los contornos que están dentro de otro contorno, como no los necesito,
        la librería me pide escribirlo de esa forma

        #Parametros
        imagen_original(nunpy array): La imagen procesada con cv2 son arrays de numpy
        #Retorno
        contorno(numpy array): La mascara que se devuelve está hecha con arrays de numpy

    '''
    mascara_blanca = cv2.inRange(imagen_original, BLANCO_BGR_MIN, BLANCO_BGR_MAX)
    mascara_blanca = cv2.morphologyEx(mascara_blanca, cv2.MORPH_CLOSE, KERNEL_CAP)
    mascara_blanca = cv2.morphologyEx(mascara_blanca, cv2.MORPH_OPEN, KERNEL_CAP)
    contorno,_ = cv2.findContours(mascara_blanca, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) 
    return contorno

def analizar_tormenta(imagen_original, gama_baja, gama_alta, mensaje_metereologico, coordenadas_ciudades):
    '''
       Primero, convierte la imagen ingresada a la gama HSV de colores,
       luego hace el mismo procedimiento que en hallar_contornos_blancos
       (Hallar mascarás del color y filtraciones de ruido).
        El primer for iterará en el diccionario coordenadas_ciudades
        y el segundo en los contornos del color correspondiente.
        Luego se hace un pequeño calculo de conversión de escalas 
        y se muestra en pantalla que precipitaciones a las ciudades.

        #Parametros
        imagen_original(nunpy array): La imagen procesada con cv2 son arrays de numpy
        gama_baja(numpy array): Limite inferior del color correspondiente, 
        el array representa  [Tono, Saturación, Brillo]
        gama_alta(numpy array): Limite superrior del color correspondiente, 
        el array representa [Tono, Saturación, Brillo]
        mensaje_metereologico(str): String que posee la precipitación indicada por el color
        coordenadas_ciudades(dic): Diccionario que posee de clave el nombre de la ciudad y las coordenadas de la misma en la imagen

    '''

    imagen_hsv = cv2.cvtColor(imagen_original, cv2.COLOR_BGR2HSV)

    mascara = cv2.inRange(imagen_hsv, gama_baja, gama_alta)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, KERNEL)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, KERNEL)

    contorno,_ = cv2.findContours(mascara, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
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
            if(distancia_real <= 10  and aviso == False): #Si la distancia real es menor a 10km
                aviso = True
                print(f"Se aproximan {mensaje_metereologico} a la ciudad de {ciudad} a una distancia de {distancia_real} km")
    
def iterar_colores():
    '''
        Verifica la existencia de la imagen en el directorio del programa,
        si existe, empezará leyendo esa imagen con la librería OPEN-CV.
        Luego, haré el llamado de la función analizar_tormenta dentro del for
        con el cuál iteraré cada uno de los colores que aparezcan en la imagen.
        Muestra la imagen de radar en una ventana emergente.
    '''   
    if(os.path.exists(RUTA_IMAGEN) == True):
        imagen_original = cv2.imread("radar.png")
        contorno_blanco = hallar_contornos_blancos(imagen_original)
        coordenadas_ciudades = hallar_coordenadas(contorno_blanco, imagen_original)
        for color in COLORES.values(): #
            analizar_tormenta(imagen_original, color[0], color[1],color[2], coordenadas_ciudades)
        print("Se abrío una ventana con la imagen ingresada \n Presione una tecla para cerrar la ventana...")
        cv2.imshow("Imagen", imagen_original)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No se ha encontrado la imagen en el directorio")

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
            if año in read:
                posicion = años.index(año)
                
        if historico[busqueda][i]>datos[posicion]:
            datos[posicion]=historico[busqueda][i]#temperatura o milimetros de lluvia maximo en dia
            fechas[posicion]=historico["Date"][i]
            
        if i==len(historico["Date"])-1:
            for i in range(0,len(fechas)):
                años[i]=fechas[i]

def estudio_datos_promedios(años,datos,busqueda,historico):
    '''
        Pre:Recibe una lista con los años, una lista datos para sumar los datos, una palabra para
        hacer la busqueda en el dataframe.
        Post:Ninguna, deja a la funcion que le llama con la lista datos a utilizar completa.
    '''
    cantidad_dias = [0,0,0,0,0]
    for i in range(0,len(historico["Date"])-1):
        read = historico["Date"][i]
        posicion = 0
        for año in años:
            if año in read:
                posicion = años.index(año)
        datos[posicion] += historico[busqueda][i]
        cantidad_dias[posicion] += 1
        
    for i in range (0,len(cantidad_dias)):
        datos[i] = datos[i]/cantidad_dias[i]
                
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
    datos= [0,0,0,0,0]
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

def iniciar_csv(historico):
    '''
        Pre:Recibe el archivo csv
        Post:Muestra en pantalla las opciones a usuario.
    '''
    entrada = True  
    while entrada == True:
        print("\n------GRAFICADORA DE ARCHIVOS CSV------\n")
        print("1)Marque 1 para ver el gráfico con el promedio de datos de temperatura anuales de los últimos 5 años.")
        print("2)Marque 2 para ver el gráfico con el promedio de humedad de los últimos 5 años.")
        print("3)Marque 3 para ver el gráfico con los milímetros máximos de lluvia de los últimos 5 años.")
        print("4)Marque 4 para ver el gráfico con la temperatura máxima de los últimos 5 años.")
        print("5)Marque 5 para salir.")
        opcion = validar_entrada(5)
        print("Cargando...")
        borrar_pantalla()
        if opcion == 1:
            busqueda = "Max Temperature"
            temperatura_humedad(historico,busqueda)
        elif opcion == 2:
            busqueda = "Relative Humidity"
            temperatura_humedad(historico,busqueda)
        elif opcion == 3:
            busqueda="Precipitation"
            temperatura_lluvia_max(historico,busqueda)
        elif opcion == 4:
            busqueda="Max Temperature"
            temperatura_lluvia_max(historico,busqueda)
        elif opcion == 5:
            entrada = False

def archivo_csv():
    '''
        Pre: Verifica si el archivo csv está en la carpeta
        Post: Muestra en pantalla un mensaje de no encontrar el archivo.
    '''
    ruta_csv = os.getcwd() + '\\tabla_de_datos.csv'
    if(os.path.exists(ruta_csv) == True):
        historico = pd.read_csv("tabla_de_datos.csv")
        iniciar_csv(historico)
    else:
        print("No existe o no se ha encontrado el archivo en el directorio")

def ubicar_provincia():
    '''
        Post: Devuelve la provincia indicada mediante el diccionario, de tipo str
    '''
    print("Ingrese la abreviación de su provincia \nEjemplo: Buenos Aires se abrevia como BA, Catamarca como CA. \nIngrese aquí: ")
    caracteres_provincia = input().upper()
    while(len(caracteres_provincia) != 2 or caracteres_provincia not in PROVINCIAS):
        print("Ingreso erróneo o provincia inexistente, intente nuevamente")
        caracteres_provincia = input('Provincia: ').upper()
    provincia = PROVINCIAS[caracteres_provincia]
    return provincia

def geolocalizacion_por_nombre():
    """
        Intenta definir la ubicacion del usuario usando geolocator, si falla devulve None.
        Post: Retorna un diccionario.
    """
    lugar = input('Ingrese su ubicacion(EJEMPLO: Moreno, Ezeiza, Buenos Aires): ')
    locacion = None

    try:
        locacion = GEOLOCATOR.geocode(lugar, country_codes='ar', addressdetails=True)
    except AttributeError:
        print(f'No se encontro {lugar}')
    except GeocoderServiceError:
        print('Fallo la conexión...')

    if locacion is None:  
        diccionario = {'Ciudad': None, 'Provincia': None, 'Lugar': None}
        return diccionario

    provincia = None
    ciudad = None
    ubicacion = locacion.raw
    if "address" in ubicacion:
        if "state" in ubicacion["address"]:
            provincia = ubicacion['address']['state']
        if "city" in ubicacion["address"]:
            ciudad = ubicacion["address"]["city"]
        elif "city" not in ubicacion["address"] and "village" in ubicacion["address"]:
            ciudad = ubicacion["address"]["village"]
    diccionario = {'Ciudad': ciudad, 'Provincia': provincia, 'Lugar': locacion}
    return diccionario

def geolocalizacion_por_coordenadas():
    """
        Post: Devuelve la ciudad y la provincia de una lat y long ingresados en un diccionario, ante un error retorna None
    """
    print('Ingrese a continuacion las coordenadas')
    coordenadas_validas = False
    while not coordenadas_validas:
        try:
            latitud = float(input('Latitud: '))
            if latitud <= 90 and latitud >= -90:
                longitud = float(input('Longitud: '))
                coordenadas = (latitud, longitud)
                coordenadas_validas = True
            else:
                print('La latitud debe estar en el rango [90, -90]')
        except ValueError:
            print('Entrada invalida, intente nuevamente...')
            coordenadas_validas = False
            
    ubicacion = None
    locacion =  None
    try:
        locacion = GEOLOCATOR.reverse(coordenadas)
        ubicacion = locacion.raw
    except TypeError:
        print('No se encontró la ubicación...')
    except GeocoderServiceError:
        print('Fallo la conexión...')

    ciudad = None
    provincia = None
    if ubicacion != None:
        if 'address' in ubicacion:
            if 'state' in ubicacion['address']:
                provincia = ubicacion['address']['state']
            if 'city' in ubicacion['address']:
                ciudad = ubicacion['address']['city']
            elif "city" not in ubicacion["address"] and "town" in ubicacion["address"]:
                ciudad = ubicacion["address"]["town"]

    diccionario = {'Ciudad': ciudad, 'Provincia': provincia, 'Lugar': locacion}
    return diccionario

def hallar_al_usuario_manualmente():
    '''
        Pre: Ninguna, luego pide al usuario los datos de su localización
        Post: Retorna un diccionario con la clave Ciudad y Provincia con los datos del usuario
    '''
    print("A continuación ingrese la ubicación desde la cuál está usando nuestra aplicación, primero la abreviación de su provincia y luego su ciudad")
    provincia_usuario = ubicar_provincia()
    ciudad_usuario = input("Ingrese el nombre de la ciudad: ").title()
    ciudad_usuario = ciudad_usuario.replace("De", "de")
    ciudad_usuario = ciudad_usuario.replace("Del", "del")
    diccionario = {"Ciudad":ciudad_usuario, "Provincia": provincia_usuario}
    return diccionario

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

        if ubicacion['Ciudad'] == None or ubicacion['Provincia'] == None:
            print('Algo salio mal, ingrese su ubicacion nuevamente\n')
            ubicacion = hallar_al_usuario_manualmente()
            lugar = ubicacion['Ciudad'] + ', ' + ubicacion['Provincia']
        
        print(f'Usted está en {lugar}? \n1. Si\n2. No')
        opcion = validar_entrada(2)
        if opcion == 1:
            ubicacion_correcta = True
        else:
            borrar_pantalla()
            print('Agregue informacion. Revise la escritura.\n')
            ubicacion_correcta = False
    return ubicacion

def verificar_ciudad(respuesta_json, ciudad, provincia):
    '''
        Pre: Recibe un json de la url weather, la ciudad y la provincia del usuario
        Post: Retorna una lista de diccionarios. Esta, contiene un solo diccionarion si se encotro la ciudad exacta, 
              o, los diccionarios de todas las ciudades parecidas en la misma provincia
    '''
    ciudad_encontrada = False
    lista = []
    n_dic = 0
    while ciudad_encontrada == False and n_dic < len(respuesta_json):
        if ciudad == respuesta_json[n_dic]["name"] and provincia == respuesta_json[n_dic]["province"]:
            lista = [respuesta_json[n_dic]]
            ciudad_encontrada = True
        elif ciudad in respuesta_json[n_dic]['name'] and provincia == respuesta_json[n_dic]["province"]:
            lista.append(respuesta_json[n_dic])
        n_dic += 1
    return lista

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

def mostrar_pronostico_ciudad(lista_pronosticos):
    '''
        Pre: Recibe una lista que contiene al menos un diccionario proveniente de los datos json de la url weather
        Post: Muestra el pronostico da la o las ciudades
    '''
    for ciudad in lista_pronosticos:
        print("-"*80)
        print(f"A CONTINUACIÓN SE DARÁ EL PRONÓSTICO DE LA CIUDAD DE: {ciudad['name']}")
        print("-"*80)
        print(f"Fecha y Hora: {ciudad['forecast']['date_time']}")
        print(f"Temperatura mínima: {ciudad['forecast']['forecast']['0']['temp_min']}°C")
        print(f"Temperatura máxima: {ciudad['forecast']['forecast']['0']['temp_max']}°C")
        print(f"Humedad: {ciudad['weather']['humidity']}% \nVelocidad del viento: {ciudad['weather']['wind_speed']} km/h")
        print(f"Pronóstico de la mañana: {ciudad['forecast']['forecast']['0']['morning']['description']}")
        print(f"Pronóstico de la tarde: {ciudad['forecast']['forecast']['0']['afternoon']['description']}\n")
        print("-"*80)

def pronostico_usuario(ubicacion_usuario):
    '''
        Pre: Recibe el diccionario con la ubicación del usuario
        Post: Ninguno, sigue una serie de procesos para mostrar el pronóstico de la locación del usuario
    '''
    conexion = verificar_conexion(URL_ESTADO_ACTUAL) 
    conexion_exitosa = conexion['conexion']

    if conexion_exitosa == True:
        respuesta_json = conexion['respuesta'].json()
        ciudad_verificada = verificar_ciudad(respuesta_json, ubicacion_usuario['Ciudad'], ubicacion_usuario['Provincia'])

        if len(ciudad_verificada) == 0:
            mostrar_pronostico_provincia(respuesta_json, ubicacion_usuario['Provincia'])
        elif len(ciudad_verificada) == 1:
            mostrar_pronostico_ciudad(ciudad_verificada)
        else:
            print('No se encontró la ciudad exacta\nSe encontraron las siguientes ciudades\n')
            mostrar_pronostico_ciudad(ciudad_verificada)
    else:
        print('No se pudo establecer conexion con el Servicio Meteorológico Nacional.')

def alertas_nacionales():
    '''
        Pre:Ninguno, primero recibe los datos de la url indicada en el modulo y luego las muestra
        Post:Niguno, muestra las alertas a nivel nacional
    '''
    conexion = verificar_conexion(URL_ALERTAS) 
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

def mostrar_pronostico_extendido_ciudad(lista_pronostico, dia_pronostico):
    '''
        Pre: Recibe una lista de diccionarios y el numero de dias desde la fecha.
        Post: Muestra el pronostico extendido para cada ciudad.
    '''
    for ciudad in lista_pronostico:
        print("-"*80)
        print(f"PRONÓSTICO PARA DENTRO DE {dia_pronostico} DÍAS DE LA CIUDAD DE: {ciudad['name']}")
        print("-"*80)
        print(f'MAÑANA:\nTemperatura: {ciudad["weather"]["morning_temp"]}°C\nDescripción: {ciudad["weather"]["morning_desc"]}')
        print(f'TARDE:\nTemperatura: {ciudad["weather"]["afternoon_temp"]}°C\nDescripción: {ciudad["weather"]["afternoon_desc"]}')
        print("-"*80,'\n')


def pronostico_extendido(ubicacion_usuario):
    '''
        Pre: Recibe el diccionario con la ubicación del usuario
        Post: Ninguno, sigue una serie de procesos para mostrar el pronóstico extendido de la locación del usuario
    '''
    contador = 1
    for ruta in URLS_P_EXTENDIDO:
        conexion = verificar_conexion(URLS_P_EXTENDIDO[ruta]) 
        conexion_exitosa = conexion['conexion']

        if conexion_exitosa == True:
            respuesta_json = conexion['respuesta'].json()
            ciudad_verificada = verificar_ciudad(respuesta_json, ubicacion_usuario['Ciudad'], ubicacion_usuario['Provincia'])

            if len(ciudad_verificada) == 0:
                print(f'No hay información disponible para {ubicacion_usuario["Ciudad"]}')
            elif len(ciudad_verificada) == 1:
                mostrar_pronostico_extendido_ciudad(ciudad_verificada, contador)
            else:
                print('No se encontró la ciudad exacta\nSe encontraron las siguientes ciudades\n')
                mostrar_pronostico_extendido_ciudad(ciudad_verificada, contador)
        else:
            print(f'Fallo la conexión para el pronóstico de dentro de {contador} días')

        contador += 1

def mostrar_alertas(ubicacion_usuario):
    '''
        Pre: Recibe la localizacion 
        Post: Muestra las alertas para la localizacion ingresada
    '''
    conexion = verificar_conexion(URL_ALERTAS) 
    conexion_exitosa= conexion['conexion']

    if conexion_exitosa == True:
        respuesta_json = conexion['respuesta'].json()
        localizacion = ubicacion_usuario['Provincia']

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
    else:
        print('No se pudo establecer conexion con el Servicio Meteorológico Nacional.')

def menu_de_acciones(opcion, ubicacion_usuario):
    '''
        Procedimiento que determina que camino seguir al programa mediante la opción ingresada
        por el usuario.
        #Parametros
        opcion(int): La opcioón ingresada por el usuario
        
    '''
    if opcion == 1:
        pronostico_usuario(ubicacion_usuario)
    elif opcion == 2:
        mostrar_alertas(ubicacion_usuario)
    elif opcion == 3:
        alertas_nacionales()
    elif  opcion == 4:
        archivo_csv()
    elif opcion == 5:
        pronostico_extendido(ubicacion_usuario)
    elif(opcion == 6):
        iterar_colores()

def main():
    '''
        Muestra el menú principal
        El programa termina si el usuario ingresa la opción número 8.
    '''
    print("\n¡Bienvenidos a la aplicación del servicio metereológico de Tormenta!\n")
    cerrar_programa = False

    while cerrar_programa == False:
        cerrar_menu = False
        ubicacion_usuario = hallar_usuario()
        borrar_pantalla()
        print(f'UBICACIÓN: {ubicacion_usuario["Ciudad"]}, {ubicacion_usuario["Provincia"]}')

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
            borrar_pantalla()
            if opcion == 7 or opcion == 8:
                cerrar_menu = True
            else:
                menu_de_acciones(opcion,ubicacion_usuario)
                cerrar_menu = False

        if opcion == 8:
            cerrar_programa = True
        else:
            cerrar_programa = False
    print('Fin del programa\nHasta la proxima!')
main()
