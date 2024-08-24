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
            # Usar gRPC para comunicarte con el nodo destino
            with grpc.insecure_channel(f'localhost:{target_node.port}') as channel:
                stub = chord_pb2_grpc.ChordServiceStub(channel)
                response = stub.StoreFile(chord_pb2.StoreFileRequest(file_id=file_id))
                print(response.message)
        else:
            self.files.append(file_id)
            print(f"Archivo '{file_id}' almacenado en el nodo con ID {self.id} ({self.port}).")
    
    def find_node(self, file_id):
        # Si el ID del archivo es menor que el ID del nodo actual
        if file_id < self.id:
            # Recorrer hacia atrás (predecessor)
            if (self.predecessor is not None) and self.predecessor.id > file_id:
                print(f"Buscando hacia atrás en el nodo con ID {self.predecessor.id}")
                return self.predecessor.find_node(file_id)
            else:
                # Si llegamos a un nodo donde el predecessor ya no es mayor, almacenamos aquí
                print(f"Archivo será almacenado en el nodo con ID {self.id}.")
                return self
        # Si el ID del archivo es mayor que el ID del nodo actual
        elif file_id > self.id:
            # Recorrer hacia adelante (successor)
            if (self.successor is not None) and self.successor.id > file_id:
                print(f"Buscando hacia adelante en el nodo con ID {self.successor.id}")
                return self.successor.find_node(file_id)
            else:
                # Si llegamos a un nodo donde el sucesor ya no es menor, almacenamos aquí
                print(f"Archivo será almacenado en el nodo con ID {self.id}.")
                return self
        else:
            # Si el archivo debe ser almacenado en el nodo actual
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
        node_address, node_port = node_info

        if node_address > self.id:
            if self.successor is None:
                self.successor = ChordNode(node_address, node_port)
            else:
                self.successor.join(node_info)
        elif node_address < self.id:
            if self.predecessor is None:
                self.predecessor = ChordNode(node_address, node_port)
            else:
                self.predecessor.join(node_info)
        # Una vez que el nodo se une, actualiza la finger table
        self.update_fingers()
        # Notifica a otros nodos para que actualicen sus finger tables
        self.notify_others()

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

