'''Se recibe un archivo csv, con el histórico de temperaturas y humedad de la zona fértil y
productora de la Argentina. Se pide:
A)Gráfico con el promedio de temperaturas anuales de los últimos 5 años
B)Gráfico con el promedio de humedad de los últimos 5 años.
C)Milímetros máximos de lluvia de los últimos 5 años.
Temperatura máxima de los últimos 5 años.'''

import pandas as pd
import requests
import matplotlib.pyplot as plt


def constructorPromedio(palabra1, palabra2, historico,años,y1):
    
    cantidad_2013 = años.count("2013")
    cantidad_2014 = años.count("2014")
    suma_temperatura2013=0#sirve para temperatura y humedad
    suma_temperatura2014=0#sirve para temperatura y humedad
    
    for i in range(0,cantidad_2013+1):
        suma_temperatura2013 += historico[palabra1][i]
        if palabra2=='Min Temperature':
            suma_temperatura2013 += historico['Min Temperature'][i]
    for i in range (cantidad_2013+1,(cantidad_2013+cantidad_2014)):
        suma_temperatura2014 += historico[palabra1][i]
        if palabra2=='Min Temperature':
            suma_temperatura2014 += historico['Min Temperature'][i]
        
    if palabra2=='Min Temperature' or palabra1=="Relative Humidity" or palabra1=="Precipitation":
        y1.append(suma_temperatura2013//cantidad_2013)#sirve para temperatura y humedad
        y1.append(suma_temperatura2014//cantidad_2014)#sirve para temperatura y humedad
    

def año(fecha):
    separado=""
    contador=0
    for i in fecha:
        if contador<len(fecha)-1:
            separado+=i+"."
        elif contador==len(fecha)-1:
            separado+=i
        contador+=1
    
    separado= separado.split(".")
    separado = separado[len(separado)-5]+separado[len(separado)-4]+separado[len(separado)-3]+separado[len(separado)-2]
    return separado

def fechas(años):
    with open("C:\\Users\\Usuario\\Documents\\Tp\\weatherdata--389-603.csv", "r") as archivo:
        csv = archivo.read().splitlines()
    fechas=[]
    for i in csv:
        linea= i.split(",")
        fechas.append(linea[0])#"1/1/2013"
        
    fechas.pop(0)
    for i in fechas:
        años.append(año(i))
        
def milimetros(historico):
    años=[]
    fechas(años)
    x1=["2013","2014"]
    y1=[]
    constructorPromedio("Precipitation", "None", historico,años,y1)
    print(y1)
    #Caractersticas del grafico
    plt.bar(x1[0],y1[0], label= "Datos 2013", width=1, color = "blue")
    plt.bar(x1[1],y1[1], label= "Datos 2014", width=1, color = "orange")
    #titulo y nombre de ejes
    plt.title("Promedio de Humedad")
    plt.ylabel("Milimetros de Lluvia")
    plt.xlabel("Año")
    #mostrar
    plt.legend()
    plt.show()  
    
        
def humedad(historico):
    años=[]
    fechas(años)
    x1=["2013","2014"]
    y1=[]
    constructorPromedio("Relative Humidity", "None", historico,años,y1)
    print(y1)
    #Caractersticas del grafico
    plt.bar(x1[0],y1[0], label= "Datos 2013", width=1, color = "blue")
    plt.bar(x1[1],y1[1], label= "Datos 2014", width=1, color = "orange")
    #titulo y nombre de ejes
    plt.title("Promedio de Humedad")
    plt.ylabel("Humedad")
    plt.xlabel("Año")
    #mostrar
    plt.legend()
    plt.show()  
    
    
def dataframe(historico):
    años=[]
    fechas(años)
    x1=["2013","2014"]
    y1=[]
    constructorPromedio('Max Temperature','Min Temperature',historico,años,y1)
    #Caractersticas del grafico
    plt.bar(x1[0],y1[0], label= "Datos 2013", width=1, color = "blue")
    plt.bar(x1[1],y1[1], label= "Datos 2014", width=1, color = "orange")
    #titulo y nombre de ejes
    plt.title("Promedio de temperatura")
    plt.ylabel("Temperatura")
    plt.xlabel("Año")
    #mostrar
    plt.legend()
    plt.show()  


def archivocsv():
    historico = pd.read_csv("C:\\Users\\Usuario\\Documents\\Tp\\weatherdata--389-603.csv")
    print("\n------BIENVENIDO A CONOCER LOS REGISTROS DE LA ZONA FERTIL Y PRODUCTORA ARGENTINA------\n")
    print("1)Marque 1 para ver el gráfico con el promedio de temperaturas anuales de los últimos 5 años.")
    print("2)Marque 2 para ver el gráfico con el promedio de humedad de los últimos 5 años.")
    print("3)Marque 3 para ver el gráfico con los milímetros máximos de lluvia de los últimos 5 años.")
    print("4)Marque 4 para ver el gráfico con la Temperatura máxima de los últimos 5 años.")
    print("0)Marque 0 para salir.")
    opcion=input("Marque la opcion deseada: ")
    while opcion!="1" and opcion!="2" and opcion!="3" and opcion!="4" and opcion!="0":
        opcion=input("Marque una opcion valida: ")
    if opcion == "1":
        dataframe(historico)
    if opcion=="2":
        humedad(historico)
    if opcion=="3":
        milimetros(historico)
def main():
    opcion_usuario = 4
    if opcion_usuario == 4:
        archivocsv()
        
main()
        