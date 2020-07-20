'''Se recibe un archivo csv, con el histórico de datoss y humedad de la zona fértil y
productora de la Argentina. Se pide:
A)Gráfico con el promedio de datoss anuales de los últimos 5 años
B)Gráfico con el promedio de humedad de los últimos 5 años.
C)Milímetros máximos de lluvia de los últimos 5 años.
datos máxima de los últimos 5 años.'''

import pandas as pd
import requests
import matplotlib.pyplot as plt

def graficoCaracteristicasprecipitacion(años,datos):
    plt.bar(años[0],datos[0], label= f"{datos[0]}Mm", width=0.5, color = "blue")
    plt.bar(años[1],datos[1], label= f"{datos[1]}Mm", width=0.5, color = "orange")
    plt.bar(años[2],datos[2], label= f"{datos[2]}Mm", width=0.5, color = "black")
    plt.bar(años[3],datos[3], label= f"{datos[3]}Mm", width=0.5, color = "pink")
    plt.bar(años[4],datos[4], label= f"{datos[4]}Mm", width=0.5, color = "red")    

def graficoCaracteristicashumedad(años,datos):
    plt.bar(años[0],datos[0], label= f"{datos[0]}%", width=0.5, color = "blue")
    plt.bar(años[1],datos[1], label= f"{datos[1]}%", width=0.5, color = "orange")
    plt.bar(años[2],datos[2], label= f"{datos[2]}%", width=0.5, color = "black")
    plt.bar(años[3],datos[3], label= f"{datos[3]}%", width=0.5, color = "pink")
    plt.bar(años[4],datos[4], label= f"{datos[4]}%", width=0.5, color = "red")

def graficoCaracteristicastemperatura(años,datos):
    plt.bar(años[0],datos[0], label= f"{datos[0]}°C", width=0.5, color = "blue")
    plt.bar(años[1],datos[1], label= f"{datos[1]}°C", width=0.5, color = "orange")
    plt.bar(años[2],datos[2], label= f"{datos[2]}°C", width=0.5, color = "black")
    plt.bar(años[3],datos[3], label= f"{datos[3]}°C", width=0.5, color = "pink")
    plt.bar(años[4],datos[4], label= f"{datos[4]}°C", width=0.5, color = "red")
    
def estudioDedatosMax(años,datos,busqueda, historico):
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

def estudioDedatosProm(años,datos,busqueda,historico,cantidad_dias):
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
                
def temperaturaLluviamax(historico,busqueda):
    años = ["2013","2014","2015","2016","2017"]
    datos=[0,0,0,0,0]
    estudioDedatosMax(años,datos,busqueda,historico)
    if busqueda=="Precipitation":
        #Caractersticas del grafico
        graficoCaracteristicasprecipitacion(años,datos)
        #titulo y nombre de ejes
        plt.title("Dia Maximo en mm de lluvia")
        plt.ylabel("Mm de lluvia")
        plt.xlabel("Dia")
        #mostrar
        plt.legend()
        plt.show()
    elif busqueda == "Max Temperature" :
        #Caractersticas del grafico
        graficoCaracteristicastemperatura(años,datos)
        #titulo y nombre de ejes
        plt.title("Dia con max temperatura en un año")
        plt.ylabel("Temperatura")
        plt.xlabel("Dia")
        #mostrar
        plt.legend()
        plt.show()
        
        
def temperaturaHumedad(historico,busqueda):
    años = ["2013","2014","2015","2016","2017"]
    datos=[0,0,0,0,0]
    cantidad_dias = [0,0,0,0,0]
    estudioDedatosProm(años,datos,busqueda,historico,cantidad_dias)
    if busqueda == "Relative Humidity":
        datos = list(map(lambda x:x*100//1, datos))
    #Caracteristicas del grafico
    if busqueda == "Max Temperature":
        graficoCaracteristicastemperatura(años,datos)
    else:
        graficoCaracteristicashumedad(años,datos)
    #titulo y nombre de ejes
    plt.title(f"Promedio de {busqueda}")
    plt.ylabel(busqueda)
    plt.xlabel("Año")
    #mostrar
    plt.legend()
    plt.show()   

def archivocsv():
    historico = pd.read_csv("weatherdata--389-603.csv")
    entrada = True
    while entrada == True:
        print("\n------BIENVENIDO A CONOCER LOS REGISTROS DE LA ZONA FERTIL Y PRODUCTORA ARGENTINA------\n")
        print("1)Marque 1 para ver el gráfico con el promedio de datoss anuales de los últimos 5 años.")
        print("2)Marque 2 para ver el gráfico con el promedio de humedad de los últimos 5 años.")
        print("3)Marque 3 para ver el gráfico con los milímetros máximos de lluvia de los últimos 5 años.")
        print("4)Marque 4 para ver el gráfico con la temperatura máxima de los últimos 5 años.")
        print("0)Marque 0 para salir.")
        opcion=input("Marque la opcion deseada: ")
        while opcion!="1" and opcion!="2" and opcion!="3" and opcion!="4" and opcion!="0":
            opcion=input("Marque una opcion valida: ")
        if opcion == "1":
            busqueda = "Max Temperature"
            temperaturaHumedad(historico,busqueda)
        elif opcion=="2":
            busqueda = "Relative Humidity"
            temperaturaHumedad(historico,busqueda)
        elif opcion=="3":
            busqueda="Precipitation"
            temperaturaLluviamax(historico,busqueda)
        elif opcion=="4":
            busqueda="Max Temperature"
            temperaturaLluviamax(historico,busqueda)
        elif opcion=="0":
            entrada=False
            
def main():
    opcion_usuario = 4
    if opcion_usuario == 4:
        archivocsv()
        
main()
        