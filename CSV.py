'''Se recibe un archivo csv, con el histórico de datoss y humedad de la zona fértil y
productora de la Argentina. Se pide:
A)Gráfico con el promedio de datoss anuales de los últimos 5 años
B)Gráfico con el promedio de humedad de los últimos 5 años.
C)Milímetros máximos de lluvia de los últimos 5 años.
datos máxima de los últimos 5 años.'''

import pandas as pd
import requests
import matplotlib.pyplot as plt

def graficoCaracteristicas(años,datos):
    plt.bar(años[0],datos[0], label= "Datos 2013", width=0.5, color = "blue")
    plt.bar(años[1],datos[1], label= "Datos 2014", width=0.5, color = "orange")
    plt.bar(años[2],datos[2], label= "Datos 2015", width=0.5, color = "black")
    plt.bar(años[3],datos[3], label= "Datos 2016", width=0.5, color = "pink")
    plt.bar(años[4],datos[4], label= "Datos 2017", width=0.5, color = "red")
    
def lluviaMaxdia(historico,maximo,busqueda,año,contador):
    for i in range(contador, len(historico["Date"])):
        red=historico["Date"][contador]
        if (año in red)==False:
            return contador
        if historico[busqueda][contador]>maximo[0]:
            maximo[0]=historico[busqueda][contador]
            maximo[1]=historico["Date"][contador]
        contador+=1

def organizadorPromedio(historico,cantidad_dias,datos):
    for i in range (len(cantidad_dias)-1,-1,-1):
        if i==len(cantidad_dias)-1:
            cantidad_dias[i]=len(historico["Date"])-cantidad_dias[i-1]
        elif i!=0:
            cantidad_dias[i]=cantidad_dias[i]-cantidad_dias[i-1]
            
    for i in range (0,len(cantidad_dias)):
        datos[i]=datos[i]/cantidad_dias[i]

def constructorDatos(historico, read,busqueda,i,año,años,datos):
    Valor = historico[busqueda][i]
    posicion = años.index(año)
    datos[posicion]+=Valor

def datosAnuales(años,datos,busqueda,contador,año, historico):
    for i in range(contador,len(historico["Date"])):
            read = historico["Date"][i]
            if (año in read) == True:
                constructorDatos(historico, read, busqueda,i,año, años, datos)
                contador+=1
            elif (año in read) == False:
                return contador

def iniciador(años,datos,busqueda, historico, cantidad_dias):
    contador=0
    contador1=0
    for año in años:
        if cantidad_dias == 1:
            maximo=[0,0]#Primer posicion de lista es para la fecha de max lluvia y la segunda para la cantidad
            contador = lluviaMaxdia(historico,maximo,busqueda,año,contador)
            años[contador1]=maximo[0]
            datos[contador1]=maximo[1]
            contador1+=1
        else:
            contador = datosAnuales(años,datos,busqueda,contador,año,historico)
        if cantidad_dias != 1:
            cantidad_dias[contador1]=contador
            contador1+=1        
            
def temperaturaLluviamax(historico,busqueda):
    años = ["2013","2014","2015","2016","2017"]
    datos=[0,0,0,0,0]
    if busqueda=="Precipitation":
        iniciador(años,datos,busqueda,historico,1)
        #Caractersticas del grafico
        graficoCaracteristicas(datos,años)
        #titulo y nombre de ejes
        plt.title("Dia Maximo en mm de lluvia")
        plt.ylabel("Mm de lluvia")
        plt.xlabel("Dia")
        #mostrar
        plt.legend()
        plt.show()
    elif busqueda == "Max Temperature" :
        iniciador(años,datos,busqueda,historico,1)
        #Caractersticas del grafico
        graficoCaracteristicas(datos,años)
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
    iniciador(años,datos,busqueda,historico,cantidad_dias)
    organizadorPromedio(historico,cantidad_dias, datos)
    #Caractersticas del grafico
    graficoCaracteristicas(años,datos)
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
        