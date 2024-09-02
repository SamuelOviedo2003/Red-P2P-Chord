# Red-P2P-Chord

### 1. Breve descripción de la actividad

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
