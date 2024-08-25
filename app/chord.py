import requests
from tabulate import tabulate


class ChordNode:
    def __init__(self, id, port,bits=8):
        self.id = id
        self.port = port
        self.successor = None
        self.predecessor = None
        self.files = []
        self.total_bits=bits
        self.finger_table = self.create_finger_table()

    def create_finger_table(self):
        # Inicializa la tabla de dedos con m entradas
        finger_table = []
        for i in range(1, self.total_bits + 1):
            start = (self.id + 2**(i-1)) % 2**self.total_bits
            finger_table.append({
                'start': start,         # inicio del intervalo
                'interval': (start, (start + 2**(i-1)) % 2**self.total_bits),  # rango de IDs que cubre
                'successor': None       # nodo sucesor (por ahora None)
            })
        return finger_table

    def update_finger_table(self, index, successor):
        if 0 <= index < len(self.finger_table):
            self.finger_table[index]['successor'] = successor
        else:
            print(f"Índice {index} fuera de rango para la tabla de dedos.")
    
    def show_finger_table(self):
        finger_table_data = []
        for i, entry in enumerate(self.finger_table):
            finger_table_data.append({
                'Entry': i+1,
                'Start': entry['start'],
                'Interval': f"[{entry['interval'][0]}, {entry['interval'][1]})",
                'Successor': entry['successor'].id if entry['successor'] else None
            })
        
        # Usar tabulate para crear una tabla bonita
        return tabulate(finger_table_data, headers="keys", tablefmt="pretty")

    def store_file(self, file_id):
        # Determina el nodo correcto para almacenar el archivo
        target_node = self.find_node(file_id)
        if target_node.id != self.id:
            # Usar HTTP para enviar el archivo al nodo destino
            url = f"http://localhost:{target_node.port}/store"
            response = requests.post(url, json={"file_id": file_id})
            if response.status_code == 200:
                print(f"Archivo '{file_id}' almacenado en el nodo con ID {target_node.id} ({target_node.port}).")
            else:
                print(f"Error al almacenar el archivo '{file_id}' en el nodo con ID {target_node.id} ({target_node.port}).")
        else:
            self.files.append(file_id)
            print(f"Archivo '{file_id}' almacenado en el nodo con ID {self.id} ({self.port}).")

    def find_node(self, file_id):
        # Caso especial donde el nodo es el menor ID y el archivo debería estar en el nodo con el mayor ID
        if self.predecessor and self.predecessor.id > self.id:
            if file_id > self.predecessor.id or file_id <= self.id:
                print(f"Archivo será almacenado en el nodo con ID {self.id}.")
                return self
        
        # Si el archivo pertenece al rango entre el nodo actual y su sucesor
        if self.successor and (self.id < file_id <= self.successor.id):
            print(f"Archivo será almacenado en el nodo con ID {self.successor.id}.")
            return self.successor
        
        # Si el archivo pertenece al nodo actual (es el menor nodo)
        if self.predecessor and (self.predecessor.id < file_id <= self.id):
            print(f"Archivo será almacenado en el nodo con ID {self.id}.")
            return self
        
        # Si ninguna de las condiciones anteriores se cumple, seguir buscando hacia adelante
        if self.successor and self.successor.id != self.id:
            return self.successor.find_node(file_id)
        
        # Caso donde solo hay un nodo o no se encontró un nodo sucesor adecuado
        print(f"Archivo será almacenado en el nodo con ID {self.id}.")
        return self


    def show(self):
        result = []
        if self.predecessor:
            result.extend(self.predecessor.show())
        result.append(f"{self.id} ({self.port}) - Archivos: {self.files}")
        if self.successor:
            result.extend(self.successor.show())
        return result

    def update_fingers(self):
        for i in range(len(self.finger_table)):
            start = self.finger_table[i]['start']
            # Si el nuevo nodo está entre el predecesor y el nodo actual
            if self.predecessor and self.predecessor.id < start <= self.id:
                self.update_finger_table(i, self)
            # Si el nuevo nodo está entre el nodo actual y su sucesor
            elif self.successor and (start <= self.successor.id or self.successor.id < self.id):
                if start <= self.successor.id:
                    self.update_finger_table(i, self.successor)
                # Si el nuevo nodo es más adecuado como sucesor
                elif self.successor.id < start <= self.successor.successor.id:
                    self.update_finger_table(i, self.successor.successor)
    
    def notify_others(self):
        if self.successor:
            self.successor.update_fingers()
        if self.predecessor:
            self.predecessor.update_fingers()

    def join(self, node_info):
        node_id, node_port = node_info
        ip = 'localhost'
        port = node_port

        # Verificación para evitar recursión infinita
        if self.id == node_id or (self.successor and self.successor.id == node_id) or (self.predecessor and self.predecessor.id == node_id):
            return

        # Caso cuando el nodo entrante tiene un ID mayor que el actual
        if node_id > self.id:
            if self.successor is None or node_id < self.successor.id:
                previous_successor = self.successor
                self.successor = ChordNode(node_id, node_port)

                # Notificar al nuevo sucesor para que actualice su predecesor
                url = f"http://{ip}:{port}/update_predecessor"
                requests.post(url, json={"predecessor_id": self.id, "predecessor_port": self.port})

                # Notificar al antiguo sucesor para que actualice su predecesor
                if previous_successor:
                    url = f"http://localhost:{previous_successor.port}/update_predecessor"
                    requests.post(url, json={"predecessor_id": node_id, "predecessor_port": node_port})

            else:
                self.successor.join(node_info)

        # Caso cuando el nodo entrante tiene un ID menor que el actual
        elif node_id < self.id:
            if self.predecessor is None or node_id > self.predecessor.id:
                previous_predecessor = self.predecessor
                self.predecessor = ChordNode(node_id, node_port)

                # Notificar al nuevo predecesor para que actualice su sucesor
                url = f"http://{ip}:{port}/update_successor"
                requests.post(url, json={"successor_id": self.id, "successor_port": self.port})

                # Notificar al antiguo predecesor para que actualice su sucesor
                if previous_predecessor:
                    url = f"http://localhost:{previous_predecessor.port}/update_successor"
                    requests.post(url, json={"successor_id": node_id, "successor_port": node_port})

            else:
                self.predecessor.join(node_info)

        # Finalmente, notificar a los nodos predecesor y sucesor si no son el nodo actual o el nodo que se une
        if self.successor and self.successor.id != node_id:
            url = f"http://localhost:{self.successor.port}/join"
            requests.post(url, json={"node_address": node_id, "node_port": node_port})

        if self.predecessor and self.predecessor.id != node_id:
            url = f"http://localhost:{self.predecessor.port}/join"
            requests.post(url, json={"node_address": node_id, "node_port": node_port})

        # Una vez que el nodo se une, actualiza la finger table
        #self.update_fingers()
        # Notifica a otros nodos para que actualicen sus finger tables
        #self.notify_others()

    def leave(self):
        current_successor = self.successor
        current_predecessor = self.predecessor

        if current_successor:
            current_successor.predecessor = current_predecessor
        if current_predecessor:
            current_predecessor.successor = current_successor

        self.successor = None
        self.predecessor = None

        print(f"Nodo {self.id} ha salido del anillo.")
    
    def lookup(self, key):
        if self.successor:
            return self.successor.id
        return self.id

