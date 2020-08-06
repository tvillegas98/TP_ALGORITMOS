# Trabajo Practico Integrador de Algoritmos y Programación I #
## Pre-Requisitos ##
La imagen de radar debe ser recortada, que los bordes blancos
y la escala de colores, de modo que no estén en la imagen a leer
(el archivo puede llamarse 'radar' con la extensión png o cambiarle el nombre dentro del programa, pero, la extensión debe ser **PNG**)  
El archivo csv puede ser nombrado 'tabla_de_datos.csv'

La razón por la cuál la imagen debe ser del tipo **PNG**
es porque funciona mejor con la codificación de colores **HSV**

***

## CONSTANTE_REGLA_3_SIMPLES ##
En el programa aparece esta constante y es utilizada  
para re-dimensionar las medidas de la imagen a una escala real
~~~
CONSTANTE_REGLA_3_SIMPLES = 30.747223602 
~~~
### Proviene de las siguientes hipótesis y calculos vectoriales: ###

Como la imágen casi siempre es la misma
y solo varía un poco su tamaño, lo que hicimos
fue hallar las coordenadas de las ciudades 
en la imagen y luego calcular la distancia entre ellas  
Ejemplo:  

Viedma : (386;479)  
Nequen : (230; 409)  
VN = (386;479) - (230;409) = (-156;-70)  
||VN|| = ((156)^2+(70)^2)^1/2  
||VN|| = 170.9853795

Una vez hallada al distancia que hay entre esas  
dos ciudades en la imagen, solo busque la distancia real.  
La distancia real entre Viedma y Neuquen es de: 556,1km  
Por regla de tres simples puedo decir  

556,1km_____170.9853795(Coordenadas de pixeles)
100km____30.747223602(distancia de pixeles)  

Ahora para verificar que tan eficiente es
esa constante, pruebo con 2 otras dos coordenadas
de la imagen  

Bahía Blanca: (410;397)  
Mar del Plata : (557;374)  
||BN|| = 148.7884404  

Aplicando nuevamente la regla de 3 simples 

30.747223602___100km  
148.7884404____483,90km  

Y la distancia real entre Bahía Blanca y Mar del Plata  
es de 463,9km

Hallando el margen de error  
463,9km___100%  
483,9km___104,31%  
Entonces hubo un error del 4% aproximadamente  

Finalmente en el programa se aplica de la siguiente forma
~~~
vector_ciudad = np.array([coordenadas])
vector_color = np.array([coordenada_x,coordenada_y])
norma = np.linalg.norm(vector_ciudad-vector_color)
distancia_real = (norma * CONSTANTE_REGLA_3_SIMPLES)/100
~~~
***
## A continuación dejo las coordenadas entregadas por una imagen del radar (cóordenadas de píxeles) ## 
Número:1, Coordenada X:386; Coordenada Y: 479 (Viedma)  
Numero:2,Coordenada X:230; Coordenada Y: 409 (Neuquen)  
Número:3, Coordenada X:410; Coordenada Y: 397 (Bahía Blanca)  
Número:4, Coordenada X:557; Coordenada Y: 374 (Mar del plata)  
Número:5, Coordenada X:346; Coordenada Y: 314 (Santa Rosa)   
Número:6, Coordenada X:553; Coordenada Y: 252 (La Plata)  
Número:7, Coordenada X:537; Coordenada Y: 238 (C.A.B.A)  
Número:8, Coordenada X:469; Coordenada Y: 207 (Pergamino)  
Número:9, Coordenada X:278; Coordenada Y: 183 (San Luis)  
Número:10, Coordenada X:194; Coordenada Y: 171 (Mendoza)  
Número:11, Coordenada X:473; Coordenada Y: 122 (Parana)  
Número:12, Coordenada X:467; Coordenada Y: 117 (Santa Fe)  
Número:13, Coordenada X:201; Coordenada Y: 116 (San Juan)   
Número:14, Coordenada X:348; Coordenada Y: 107 (Cordoba)  
Número:15, Coordenada X:255; Coordenada Y: 30 (La Rioja)  
Número:16,Coordenada X:561; Coordenada Y: 23 (Mercedes)  
***
## Grupo integrado por ##
+ Villegas Cabral, Tomás Ariel
+ Moavro, Mariano
+ Puentes Rodulfo, Jackson Alberto