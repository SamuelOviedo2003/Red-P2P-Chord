# Red-P2P-Chord

## 1. Breve descripción de la actividad

En esta actividad, desarrollamos una red P2P distribuida utilizando el algoritmo Chord, el cual es un tipo de DHT (Distributed Hash Table). Las redes P2P, al no depender de un servidor centralizado, permiten que cada nodo actúe simultáneamente como cliente y servidor, con el objetivo principal de compartir recursos entre los nodos. En nuestro caso, cada nodo es una computadora, y la red estructurada se basa en el funcionamiento de una DHT.

Para implementar esta red P2P, empleamos únicamente API REST como middleware. La comunicación entre nodos se realiza de manera *stateless*, es decir, no se necesita mantener el estado de una petición para procesar la siguiente. La información se intercambia en formato JSON, lo que permite que la interacción entre los nodos funcione como "cajas negras", donde lo único relevante es el contenido enviado y recibido.

### 1.1. Aspectos cumplidos o desarrollados de la actividad propuesta

- **Unirse a la red (join):** Se implementó un servicio que permite a un nodo integrarse en la red P2P.
- **Mostrar conexiones (show):** Se desarrolló un servicio para visualizar las conexiones actuales de un nodo dentro de la red.
- **Mostrar la finger table de cada nodo (show_finger_table):** Se implementó la funcionalidad para que cada nodo pueda mostrar su finger table, un componente esencial en el algoritmo Chord.
- **Subir un archivo a la red (upload):** Se implementó un servicio que permite a los nodos subir archivos a la red, almacenándolos en otros nodos.
- **Buscar y descargar un archivo en una simulación local (store):** Se desarrolló la funcionalidad para que los nodos puedan buscar y descargar archivos desde la red en una simulación local.

### 1.2. Aspectos no cumplidos o desarrollados de la actividad propuesta

- **Problemas de concurrencia:** Se detectaron fallas en el sistema al añadir un cuarto nodo a la red. Este problema impacta la estabilidad de la red cuando se incrementa el número de nodos concurrentes.
- **Uso de IDs numéricos:** Para simplificar el desarrollo y verificar la lógica de Chord, se utilizaron IDs numéricos tanto en los nodos como en los archivos. Esto facilitó la validación del funcionamiento del algoritmo, aunque no es una solución con Hash.
- **Salir del anillo:** No se desarrolló la funcionalidad que permite a un nodo abandonar el anillo de la red P2P.

## 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.
<p align="center">
    <img src="https://miro.medium.com/v2/resize:fit:500/0*WqXs3F73o7NGlXuJ.png" alt="Imagen de Chord" width="200"/>
</p>

### Arquitectura y Algoritmo Chord
En este proyecto, hemos implementado un sistema de compartición de archivos utilizando la arquitectura P2P basada en el algoritmo Chord, que es una solución eficiente para la localización y descarga de archivos en redes descentralizadas.

El algoritmo Chord es fundamental para la gestión y operación de nuestra red P2P. Este algoritmo se basa en dos tablas principales: la tabla Finger y la tabla de archivos. La Finger Table permite a cada nodo mantener información sobre otros nodos que están a distancias exponenciales del nodo actual. Esto significa que, comenzando por el nodo más cercano, cada nodo conoce la ubicación de otros nodos a distancias de 2, 4, 8, y así sucesivamente, lo que permite realizar saltos significativos en la red durante las operaciones de búsqueda, descarga o mantenimiento, mejorando así la eficiencia del sistema.

Además de la Finger Table, cada nodo mantiene información sobre su nodo predecesor y su nodo sucesor.

Chord utiliza un método de hash que mapea tanto nodos como archivos dentro de un mismo rango de bits, lo que facilita la clasificación y localización de archivos en la red. En nuestro proyecto, hemos simplificado este mecanismo utilizando identificadores numéricos para los nodos y los archivos, lo que nos ha permitido verificar el correcto funcionamiento del algoritmo de manera más clara.

### Tablas de Archivos y Simulación Local

Cada nodo en la red Chord posee una tabla de archivos que almacena aquellos archivos cuyo identificador es igual o inmediatamente menor que el ID del nodo. En el contexto de este proyecto, donde utilizamos datos simulados (dummies), esta tabla de archivos se implementa como una lista simple. Además, hemos incorporado una lista separada llamada *archivos local*, que simula la descarga de archivos en un entorno local. Es importante destacar que esta lista local no es considerada dentro del mecanismo de Chord, mientras que los archivos en la tabla de archivos sí lo son.
