import json
import requests
from geopy.distance import geodesic #Medir distancias
from geopy.geocoders import Nominatim #Geolocalización
geolocator = Nominatim(user_agent="TP_ALGORITMOS")

PROVINCIAS = {
        "BA": "Buenos Aires", "CA": "Catamarca", "CH":"Chubut",
        "CB":"Córdoba", "CR":"Corrientes", "ER":"Entre Ríos",
        "FO":"Formosa", "JY":"Jujuy", "LP":"La Pampa", "LR":"La Rioja",
        "MZ": "Mendoza", "MI":"Misiones", "NQ":"Neuquén", "RN":"Río Negro",
        "SA":"Salta", "SJ":"San Juan", "SL":"San Luis", "SC":"Santa Cruz",
        "SF":"Santa Fe", "SE":"Santiago del Estero", 
        "TF":"Tierra del fuego, Antártida e Islas del Atlántico Sur", 
        "TU":"Tucumán"
        }

def verificar_conexiones():
    '''
        Pre:Verifico la conexión a internet mediante un try y except
        Post:Luego retorna un valor booleano en función de si hubo una conexión exitosa o no    
    '''

    try:
        respuesta_uno = requests.get("https://ws.smn.gob.ar/map_items/weather", timeout = 1)
        respuesta_dos = requests.get("https://ws.smn.gob.ar/alerts/type/AL", timeout = 1)
        respuesta_cuatro = requests.get("https://ws.smn.gob.ar/map_items/forecast/1", timeout = 1)
        respuesta_cuatro = requests.get("https://ws.smn.gob.ar/map_items/forecast/2", timeout = 1)
        respuesta_cuatro = requests.get("https://ws.smn.gob.ar/map_items/forecast/3", timeout = 1)
        return False
    except requests.exceptions.Timeout:
        print("Lo lamento, no se pudo conectar con el servicio metereológico nacional...")
        return True

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

def hallar_al_usuario():
    '''
        Pre: Ninguna, luego pide al usuario los datos de su localización
        Post: Retorna un diccionario con la clave Ciudad y Provincia con los datos del usuario
    '''
    ubicacion_ingresada = False
    while(ubicacion_ingresada == False):
        print("A continuación ingrese la ubicación desde la cuál está usando nuestra aplicación, primero la abreviación de su provincia y luego su ciudad")
        provincia_usuario = ubicar_provincia("Ingrese la abreviación de su provincia \nEjemplo: Buenos Aires se abrevia como BA, Catamarca como CA. \nIngrese aquí: ")
        ciudad_usuario = input("Ingrese el nombre de su ciudad(Su nombre de pila, ejemplo: José María Ezeiza): ")
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
        if(diccionario["name"] == ubicacion_usuario["Ciudad"] and ciudad_encontrada == False):
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
        if(diccionarios['province'] == provincia):
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

def mostrar_pronostico_ciudad(respuesta_json, ciudad):
    '''
        Pre:Recibe los datos json de la url weather y la ciudad del usuario
        Post: Muestra el pronóstico de la ciudad del usuario, debido a que fue encontrada en los datos json
    '''
    for diccionarios in respuesta_json:
        if(diccionarios['name'] == ciudad):
            print("-"*80)
            print(f"A CONTINUACIÓN SE DARÁ EL PRONÓSTICO DE LA CIUDAD DE: {ciudad}")
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
    print("Conectando...")
    respuesta_json = requests.get("https://ws.smn.gob.ar/map_items/weather")
    respuesta_json = respuesta_json.json()
    ciudad_verificada = verificar_ciudad(respuesta_json, ubicacion_usuario)
    if(ciudad_verificada == False):
        mostrar_pronostico_provincia(respuesta_json, ubicacion_usuario['Provincia'])
    else:
        mostrar_pronostico_ciudad(respuesta_json, ubicacion_usuario['Ciudad'])

def alertas_nacionales():
    '''
        Pre:Ninguno, primero recibe los datos de la url indicada en el modulo y luego las muestra
        Post:Niguno, muestra las alertas a nivel nacional
    '''
    print("Conectando...")
    respuesta_json = requests.get("https://ws.smn.gob.ar/alerts/type/AL")
    respuesta_json = respuesta_json.json()
    contador = 1
    print("-"*80)
    print(f"A CONTINUACIÓN SE DARÁ EL PRONÓSTICO A NIVEL NACIONAL")
    print("-"*80)
    for alertas in respuesta_json:
        zonas = [zona for zona in alertas['zones'].values()]
        print("-"*80)
        print(f"AVISO NÚMERO°{contador}")
        print("-"*80)
        print(f"Titulo: {alertas['title']} \nFecha: {alertas['date']} \nHora: {alertas['hour']}")
        print(f"Aviso: {alertas['description']} \n Zonas afectadas: {zonas}")
        print("-"*80)
        contador += 1

def menu_de_acciones(opcion, ubicacion_usuario):
    '''
        Pre: Opcion de tipo int y ubicación del usuario
        Post: Ninguno.
    '''
    if(opcion == 1):
        pronostico_usuario(ubicacion_usuario)
    elif(opcion == 2):
        pass
    elif(opcion == 3):
        alertas_nacionales()
    elif(opcion == 4):
        pass
    elif(opcion == 5):
        pass
    elif(opcion == 6):
        pass

def main():
    '''
        Muestra el menú principal
        El programa termina si el usuario ingresa la opción número 7.
    '''
    print("¡Bienvenidos a la aplicación del servicio metereológico de Tormenta!")
    ubicacion_usuario = hallar_al_usuario()
    print("Conectando... ")
    cerrar_menu = verificar_conexiones()
    while(cerrar_menu == False):
        print("¿Que desea hacer? \n1.Ver el pronóstico para su ciudad(En caso de no haber para su ciudad, se mostrarán las ciudades mas cercanas) \n2.Ver el pronóstico de una ciudad ubicada por geolocalización \n3.Listar las alertas a nivel Nacional \n4.Graficar el archivo CSV ingresado \n5.Pronóstico extendido de 1,2 y 3 días de una ciudad ingresada por el usuario \n6.Informe de precipitaciones mediante analisis de imagenes de radar \n7.Cerrar el programa\n")
        opcion = validar_entrada(7)
        if(opcion == 7):
            cerrar_menu = True
            print("¡Hasta la próxima!")
        else:
            menu_de_acciones(opcion,ubicacion_usuario)
main()
