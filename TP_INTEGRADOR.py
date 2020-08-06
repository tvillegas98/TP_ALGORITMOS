import os  # Borrar pantalla y chequear rutas
import cv2  # Analisis de imagen
import matplotlib.pyplot as plt  # Mostrar graficos
import numpy as np  # Analisis de imagen
import pandas as pd  # Leer csv
import requests  # URL
from geopy.distance import geodesic  # Medir distancias
from geopy.exc import GeocoderServiceError  # Excepciones
from geopy.geocoders import Nominatim  # Geolocalización
from matplotlib.ticker import MultipleLocator  # Arreglar ejes de grafico

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
        Verifica que la URL responda correctamente o que el usuario
        posea conexión a internet

        #Parametros
        ruta(str): URL a verificar
        #Retorno
        diccionario_respuesta(dicc): retorna un diccionario con una
        key que representa la respuesta de URL y la otra con un valor booleano
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

def arreglo_label(anio_dias, datos,palabra):
    '''
    Pre:Recibe una lista ya sea con año o dias y una palabra que le permitira agregar el simbolo correcto al texto.
    Arregla el texto que se mostrara en la legenda.
    Post:Devuelve una cadena de caracteres.
    '''
    texto_label = ""
    simbolo = ""
    if palabra == "MaxTemperature":
        simbolo = "°C"
    elif palabra == "Relative Humidity":
        simbolo = "%"
    elif palabra =="Precipitation":
        simbolo = "mm"
    for i in range(0,len(anio_dias)):
        texto_label += str(anio_dias[i]) + ": " + str(datos[i]) + simbolo + "\n"
    return texto_label

def dibujar_grafico(datos,anios,busqueda):
    '''
    Pre: Recibe dos listas, uno con los datos a proyectar y otra con los años o dias, arregla el grafico para mostrarlo
    Post:Muestra por pantalla una grafico de lineas.
    '''
    #Dibujar grafico
    label = arreglo_label(anios, datos,busqueda)
    fig, ax = plt.subplots()
    g = ax.plot(anios,datos)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    g[0].set_label(f"{label}")
    g[0].set_marker(".")
    g[0].set_markersize(12)
    #titulo y nombre de ejes
    if busqueda=="MaxTemperature":
        g[0].set_color("blue")
        plt.title("Promedio de Temperatura", color="blue")
        plt.ylabel("Temperatura", color="blue")
        plt.xlabel("Año", color="blue")
    elif busqueda=="Relative Humidity":
        g[0].set_color("red")
        plt.title("Promedio de Humedad", color="red")
        plt.ylabel("Humedad", color="red")
        plt.xlabel("Año", color="red")
    elif busqueda=="Precipitation":
        g[0].set_color("red")
        plt.title("Milimetros Maximos de lluvia",color="blue")
        plt.ylabel("Milimetros",color="blue")
        plt.xlabel("Dias",color="blue")
    elif busqueda=="TemperaturaMax":
        g[0].set_color("red")
        plt.title("Temperatura Maxima",color="red")
        plt.ylabel("Temperatura",color="red")
        plt.xlabel("Dias",color="red")
    #Mostrar
    plt.legend()
    plt.show()
    
    
def temperatura_lluvia_maxima(anio,datos,dias,historico,busqueda):
    '''
    Pre:Recibe 3 listas, una con los años de estudio y otras dos vacias para ser llenadas, un dataframe
    y una palabra para filtrar. llena las listas con la humedad o temperatura maxima y el dia en que esto ocurrio por año.
    Post:No retorna algo.
    '''
    for i in range(0,len(anio)):
        nuevo = historico[historico.anio.isin([anio[i]])]
        valor = nuevo[busqueda].max()
        if busqueda=="Precipitation":
            nuevo = nuevo[nuevo.Precipitation.isin([valor])]
        elif busqueda=="MaxTemperature":
            nuevo = nuevo[nuevo.MaxTemperature.isin([valor])]
        posicion=nuevo.index[nuevo[busqueda]==valor].tolist()
        dias.append(nuevo.loc[posicion[0],"Dia"])
        datos.append(valor)
    
def temperatura_milimetros_maximos(anio, historico, busqueda):
    '''
    Pre:Recibe una lista con los años a trabajar, un dataframe con los datos y una palabra para filtrar.
    Reduce aun mas el dataframe para optimizar el uso y prepara las condiciones para la lectura de datos necesarios.
    Post:No retorna algo.
    '''
    dias = []
    datos = []
    historico["MaxTemperature"]=historico["Max Temperature"]
    historico = historico.drop(["Relative Humidity","Max Temperature","Min Temperature"], axis=1)
    historico["Dia"]=historico["Date"].astype(str)
    temperatura_lluvia_maxima(anio,datos,dias,historico,busqueda)
    datos = list(map(lambda x:x//1, datos))
    dibujar_grafico(datos,dias,busqueda)

    
def promedia_temperatura_humedad(promedios,cantidad_dias,datos,busqueda,anio):
    '''
    Pre:Recibe un dataframe con datos sumados para poder promediarlos con la cantidad de dias, y agregarla a la lista de datos.
    Recibe una palabra para dicernir lo que se desea promediar. 
    Post:No retorna algo
    '''
    for i in range(0,len(anio)):
        if busqueda=="MaxTemperature":
            promedios.loc[i,"Promedio Temperatura"] = promedios.loc[i,"Promedio Temperatura"]//(cantidad_dias[i]*2)
            datos.append(promedios.loc[i,"Promedio Temperatura"])
        elif busqueda=="Relative Humidity":
            promedios.loc[i,"Relative Humidity"]=promedios.loc[i,"Relative Humidity"]*100//(cantidad_dias[i])
            datos.append(promedios["Relative Humidity"][i])
    
def promedio_temperatura_humedad(anio, cantidad_dias, historico,busqueda):
    '''
    pre:Recibe una lista con los años a trabajar, la cantidad de dias de cada año, un dataframe y una palabra para fitrar.
    Crea las condiciones dentro del dataframe para el mejor manejo y lectura de datos concisos.
    post:No retorna algo
    '''
    datos = []
    historico = historico.drop(["anio","Precipitation"], axis=1)    
    promedios = historico.resample("Y", on="Date").sum()
    promedios["Promedio Temperatura"] = (promedios["Max Temperature"] + promedios["Min Temperature"])
    promedios.reset_index(inplace=True)
    promedia_temperatura_humedad(promedios,cantidad_dias,datos,busqueda,anio)
    dibujar_grafico(datos,anio,busqueda)
    
def cantidad_anio(anio, cantidad_dias, historico,csv_headers):
    '''
    Pre: Recibe dos listas vacias que llenara con los años y cantidad de dias de cada años desde el dataframe,
    un dataframe y una tupla con los headers a trabajar.
    Post:Devuelve un dataframe solo con las columnas que se utilizaran, la fecha como datatime, una columna con los años.
    '''
    historico["Date"] = pd.to_datetime(historico["Date"])  # La columna Date ahora la tenemos en formato fecha para que la utilicemos con pandas
    historico = historico.loc[:, csv_headers]  # Nos quedamos solo con los datos que trabajaremos
    historico["anio"] = historico["Date"].dt.year  # Agregamos una columna de anio segun la columna Date
    anio_maximo = historico["anio"].max()
    anio_minimo = historico["anio"].min()
    cantidad = historico.groupby("anio").count()
    for i in range(0, 5):
        if anio_maximo - i >= anio_minimo:
            cantidad_dias.append(cantidad["Date"][anio_maximo - i])
            anio.append(anio_maximo - i)
    anio.reverse()
    cantidad_dias.reverse()
    historico = historico[historico["anio"] >= int(anio[0])]
    historico = historico.sort_values("anio")
    return historico 

def inicio(nombre_csv,csv_headers,historico):
    '''
    pre:Recibe dos variables con el nombre del documento y el nombre de las columnas a utilizar.
    post:Muestra por pantalla las opciones disponibles para el usuario.
    '''
    anio = []
    cantidad_dias = []
    historico = cantidad_anio(anio, cantidad_dias, historico,csv_headers)
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
            promedio_temperatura_humedad(anio, cantidad_dias, historico,"MaxTemperature")
        elif opcion == 2:
            promedio_temperatura_humedad(anio, cantidad_dias, historico,"Relative Humidity")
        elif opcion == 3:
            temperatura_milimetros_maximos(anio, historico, "Precipitation")
        elif opcion == 4:
            temperatura_milimetros_maximos(anio, historico, "MaxTemperature")
        elif opcion == 5:
            entrada = False

def validar_csv(nombre_csv):
    '''
    Pre:Recibe el nombre del csv, y verifica que la fila no termine en coma
    para eevitar errores de lectura.
    Post:valida que la primer fila del csv termine sin coma, de terminar con coma agrega un nombre a la ultima columna.
    '''
    with open(nombre_csv, "r+") as archivo:
        texto = archivo.readlines()
        estudio = texto[0]
        estudio = estudio.rstrip(" \n")
        estudio = estudio.split('"')
        if estudio[(len(estudio)) - 1] == "," or estudio[(len(estudio)) - 1] == ", ":
            estudio.append('Null"\n')
            estudio = '"'.join(estudio)
            texto[0] = estudio
            archivo.seek(0)
            archivo.writelines(texto)
            

def verificar_csv_valido(csv_headers):
    """
    Precondicion: Si el csv existe, verifica que los datos que contenga sean correctos y no este vacio, ademas verifica
    que los headers que utilizaremos esten en el documento.
    PostCondicion: Retorna True si el csv es correcto y False si no lo es.
    """
    if not os.path.exists(RUTA_CSV):
        return False
    try:
        validar_csv('tabla_de_datos.csv')
        with open('tabla_de_datos.csv', "r") as mi_csv:
            texto = mi_csv.readlines()
    except OSError as err:
        print(f"No se pudo abrir o leer el csv {err}")
        return False
    except BaseException as err:    # Las excepciones son clases, y esta es la clase madre de todos los errores
        print(f"Ocurrio un error desconocido {err}")
        return False
    if not texto or len(texto) < 2:
        return False
    for i in csv_headers:
        if i not in texto[0]:
            return False
    return True

def inicio_csv():
    '''
    Pre:Define como constantes el nombre del csv asi como los headers a utilzar y da inicio al programa
    al realizar las validaciones a traves de funciones
    Post:No retorna algo.
    '''
    csv_headers = ("Date","Max Temperature","Min Temperature","Precipitation","Relative Humidity")
    csv_validado = verificar_csv_valido(csv_headers)
    if csv_validado == True:
        historico = pd.read_csv('tabla_de_datos.csv')
        inicio('tabla_de_datos.csv', csv_headers, historico)      
    
def ubicar_provincia():
    '''
        Le pide al usuario que ingrese la abreviatura de su provincia
        y verifica que esta esté en el diccionario PROVINCIAS
        #Retorno
        provincia(str): El nombre de la provincia
    '''
    print("Ingrese la abreviación de su provincia \nEjemplo: Buenos Aires se abrevia como BA, Catamarca como CA.")
    caracteres_provincia = input("Ingrese aquí:").upper()
    while(len(caracteres_provincia) != 2 or caracteres_provincia not in PROVINCIAS):
        print("Ingreso erróneo o provincia inexistente, intente nuevamente")
        caracteres_provincia = input('Provincia: ').upper()
    provincia = PROVINCIAS[caracteres_provincia]
    return provincia

def geolocalizacion_por_nombre():
    """
        Le pide al usuario que ingrese el nombre de su ubicación,
        se verifica que la ubicación exista y que también verifique si el servicio
        esta funcionando correctamente
        
        #Retorno
        diccionario(dicc): Si el servicio retorna None, se retornará un diccionario con
        valores None, en caso contrario, se devolverá un diccionario valores de tipo string
        con el nombre de la ciudad y provincia del usuario
        """
    lugar = input('Ingrese su ubicacion(EJEMPLO: Ezeiza, Buenos Aires): ')
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
    if ubicacion != None:
        if 'address' in ubicacion:
            if 'state' in ubicacion['address']:
                provincia = ubicacion['address']['state']
            elif 'city' in ubicacion['address']:
                provincia = ubicacion['address']['city']
            if 'suburb' in ubicacion['address']:
                ciudad = ubicacion['address']['suburb']
            elif 'city' in ubicacion["address"]:
                ciudad = ubicacion['address']['city']
            elif 'town' in ubicacion['address']:
                ciudad = ubicacion['address']['city']
    diccionario = {'Ciudad': ciudad, 'Provincia': provincia, 'Lugar': locacion}
    return diccionario

def geolocalizacion_por_coordenadas():
    """
       Le pide al usuario que ingrese la latitud y longitud
       de su ubicación, verifica que haya sio correctamente ingresado
       y luego hace la busqueda inversa. Se trabaja con el diccionario 
       devuelto por la libreria

        #Retorno
        diccionario(dicc): Un diccionario que posee la el lugar, la ciudad y la provincia
        como valores
    """
    print('Ingrese a continuacion las coordenadas')
    coordenadas_validas = False
    while not coordenadas_validas:
        try:
            latitud = float(input('Latitud: '))
            if latitud <= 90 or latitud >= -90:
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
            elif 'city' in ubicacion['address']:
                provincia = ubicacion['address']['city']
            if 'suburb' in ubicacion['address']:
                ciudad = ubicacion['address']['suburb']
            elif 'city' in ubicacion["address"]:
                ciudad = ubicacion['address']['city']
            elif 'town' in ubicacion['address']:
                ciudad = ubicacion['address']['city']
    if(provincia == 'Ciudad de Buenos Aires'):
        provincia = 'Buenos Aires'
    diccionario = {'Ciudad': ciudad, 'Provincia': provincia, 'Lugar': locacion}
    return diccionario

def hallar_al_usuario_manualmente():
    '''
        En caso de que no funcione la librería geopy o el usuario halla ingresado
        un nombre de ubicación inexistente, se utilizará esta funcion de repuesto,
        A diferencia de las otras geolocalizaciones, esta será manual.
        #Retorno
        diccionario(str): Posee la ciudad y la provincia como claves
        
    '''
    print("A continuación ingrese la ubicación desde la cuál está usando nuestra aplicación,")
    print("primero la abreviatura de su provincia y luego su ciudad")
    provincia_usuario = ubicar_provincia()
    ciudad_usuario = input("Ingrese el nombre de la ciudad: ").title()
    ciudad_usuario = ciudad_usuario.replace("De", "de")
    ciudad_usuario = ciudad_usuario.replace("Del", "del")
    diccionario = {"Ciudad":ciudad_usuario, "Provincia": provincia_usuario}
    return diccionario

def hallar_usuario():
    """
        Esta función estará activa hasta que el usuario ingrese su ubicación deseada
        o la correcta.
        #Retorno
        ubicacion(dicc): Es el diccionario que contiene la ubicación del usuario
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
            print('Agregue información o revise la escritura.\n')
            ubicacion_correcta = False
    return ubicacion

def verificar_ciudad(respuesta_json, ciudad, provincia):
    '''
        Verifica si la ciuda del usuario está en el archivo JSON entregado
        por la URL de estado actual, también si el usuario ingresó 
        el nombre de una ciudad incompleta, se verificará las ciudades más similares

        #Parametros
        respuesta_json(dicc): Diccionarios entregados por la url de estado actual
        ciudad(str): El nombre de la ciudad del usuario
        provincia(str): El nombre de la provincia del usuario
        #Retorno
        lista(list): Una lista de diccionarios que retorna la ciudad
        o las ciudades más similares a la del usuario 
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
        Mostrará en pantalla todas las alertas a nivel provincial, en caso de que la
        ciudad del usuario no figure en el JSON, además cuenta la cantidad
        de iteraciones para saber cuantos avisos hay en esa provincia
        #Parametros
        respuesta_json(dicc): Diccionarios entregados por el JSON
        provincia(str): El nombre de la provincia del usuario
    '''
    contador = 1
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
    print("La ciudad no pudo ser encontrada en la base de datos del servicio metereológico")
    print("Se mostraron alertas a nivel provincial")
def mostrar_pronostico_ciudad(lista_pronosticos):
    '''
        Recibe una lista que contiene al menos un diccionario proveniente de los datos json de la url weather.
        Muestra el pronostico para la ciudad del usuario o similares.
        #Parametros
        lista_pronosticos(list): Una lista compuesta por diccionarios
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
        Si la ciudad fue encontrada, se mostrarán en pantalla los correspondientes avisos
        en caso de que no haya conexión con el SMN, se le avisará al usuario

        #Parametros
        ubicacion_usuario(dicc): Contiene la ubicación del usuario en los valores de las claves
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
        Muestra las alertas de la URL_ALERTAS que el archivo JSON
        que entrega los avisos a nivel nacional, a veces el archivo 
        JSON puede estar vacío, por lo cual se le indicará al usuario si no 
        hay avisos por el momento
    '''
    conexion = verificar_conexion(URL_ALERTAS) 
    conexion_exitosa = conexion['conexion']
    respuesta_json = conexion['respuesta'].json()

    if (conexion_exitosa == True and len(respuesta_json) != 0):
        print("-"*80)
        print(f"A CONTINUACIÓN SE DARÁ EL PRONÓSTICO A NIVEL NACIONAL")
        print("-"*80)
        for (contador,alertas) in enumerate(respuesta_json):
            zonas = [zona for zona in alertas['zones'].values()]
            print("-"*80)
            print(f"AVISO NÚMERO°{contador+1}")
            print("-"*80)
            print(f"Titulo: {alertas['title']} \nFecha: {alertas['date']} \nHora: {alertas['hour']}")
            print(f"Aviso: {alertas['description']} \n Zonas afectadas: {zonas[0::]}")
            print("-"*80)
    else:
        print('No se pudo establecer conexion con el Servicio Meteorológico Nacional.')
        print("-"*80, "\n")
        print("NO HAY ALERTAS ACTUALES")
        print("-"*80, "\n")

def mostrar_pronostico_extendido_ciudad(lista_pronostico, dia_pronostico):
    '''
        Recorre la lista lista_pronostico, donde en ella hay diccionarios
        Mostrará en pantalla los pronósticos extendidos de la ciudad del usuario o de la ciudad
        con el nombre más similar a ella.

        #Parametros
        lista_pronostico: Lista de diccionarios provenientes del JSON de la URL_P_EXTENDIDO
        dia_pronostico(int): El día del pronóstico extendido
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
        Itera las URL de los pronósticos extendidos,
        si la ciudad del usuario no está en el archivo JSON,
        se le indicará al usuario que no hay información disponible.
        Si falla la conexión con alguna de las URLS, también se le avisará al 
        usuario

        #Parametros
        ubicacion_usuario(dicc): Un diccionario que posee como valores
        la ciudad y la provincia del usuario
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
        Itera la URL de Alertas a nivel nacional para
        luego ver si la provincia del usuario está dentro de las zonas
        afectadas por una tormenta o clima poco habitual.
        En caso de que no existan alertas, se le indicará al usuario en pantalla,
        también si no hubo conexión con el SMN.
        #Nota
        # diccionario['zones'] entrega las zonas afectadas

        # Parametros
        ubicacion_usuario(dicc): Un diccionario que posee como valores
        la ciudad y la provincia del usuario

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
        inicio_csv()
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
        while cerrar_menu == False:
            print(f'UBICACIÓN: {ubicacion_usuario["Ciudad"]}, {ubicacion_usuario["Provincia"]}')
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
    print('Fin del programa\n¡Hasta la proxima!')
main()