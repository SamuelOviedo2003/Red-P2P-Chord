import requests
from tabulate import tabulate


class ChordNode:
    def __init__(self, id, port, bits=8):
        self.id = id
        self.port = port
        self.successor = None
        self.predecessor = None
        self.files = []
        self.total_bits = bits
        self.finger_table = self.create_finger_table()
        print(f"[DEBUG] Nodo creado con ID {self.id} y puerto {self.port}")

    def create_finger_table(self):
        finger_table = []
        for i in range(1, self.total_bits + 1):
            start = (self.id + 2**(i-1)) % 2**self.total_bits
            finger_table.append({
                'start': start,
                'interval': (start, (start + 2**(i-1)) % 2**self.total_bits),
                'successor': None
            })
        print(f"[DEBUG] Finger table creada para nodo {self.id}: {finger_table}")
        return finger_table

    def update_finger_table(self, index, successor):
        if 0 <= index < len(self.finger_table):
            self.finger_table[index]['successor'] = successor
            print(f"[DEBUG] Finger table actualizada en nodo {self.id}, índice {index}, con sucesor {successor.id}")
        else:
            print(f"[DEBUG] Índice {index} fuera de rango para la tabla de dedos en nodo {self.id}")

    def show_finger_table(self):
        finger_table_data = []
        for i, entry in enumerate(self.finger_table):
            successor = entry['successor']
            successor_id = successor['id'] if successor else None
            finger_table_data.append({
                'Entry': i+1,
                'Start': entry['start'],
                'Interval': f"[{entry['interval'][0]}, {entry['interval'][1]})",
                'Successor': successor_id
            })
        return tabulate(finger_table_data, headers="keys", tablefmt="pretty")


    def update_fingers_with_new_node(self, new_node_id, new_node_port):
        print(f"[DEBUG] Actualizando finger table en nodo {self.id} con nuevo nodo {new_node_id}")
        for i in range(len(self.finger_table)):
            start = self.finger_table[i]['start']
            current_successor = self.finger_table[i]['successor']['id'] if self.finger_table[i]['successor'] else None
            print(f"[DEBUG] Evaluando entrada {i+1} de la finger table con start {start} y sucesor actual {current_successor}")

            # Condición para manejar el rango circular y evitar sobrescritura incorrecta
            if current_successor is None:
                if start <= new_node_id or (start > new_node_id and start < self.id):
                    print(f"[DEBUG] Nodo {new_node_id} es un mejor sucesor para la finger table del nodo {self.id} en índice {i+1}")
                    self.finger_table[i]['successor'] = {'id': new_node_id, 'port': new_node_port}
            elif (start <= new_node_id < current_successor) or (current_successor < self.id and (start <= new_node_id or new_node_id < current_successor)):
                print(f"[DEBUG] Nodo {new_node_id} es un mejor sucesor para la finger table del nodo {self.id} en índice {i+1}")
                self.finger_table[i]['successor'] = {'id': new_node_id, 'port': new_node_port}
            else:
                print(f"[DEBUG] Nodo {new_node_id} no es un mejor sucesor para la entrada {i+1} en la finger table del nodo {self.id}")

    def get_all_nodes(self):
        nodes = []
        if self.predecessor:
            nodes.extend(self.predecessor.get_all_nodes())
        nodes.append({
            'id': self.id,
            'port': self.port
        })
        if self.successor and self.successor.id != self.id:
            nodes.extend(self.successor.get_all_nodes())
        print(f"[DEBUG] Nodos en la red vistos por nodo {self.id}: {nodes}")
        return nodes


    def notify_all_nodes(self, new_node_id, new_node_port):
        print(f"[DEBUG] Notificando a todos los nodos desde nodo {self.id} sobre nuevo nodo {new_node_id}")
        all_nodes = self.get_all_nodes()
        for node in all_nodes:
                url = f"http://localhost:{node['port']}/update_finger_table"
                try:
                    response = requests.post(url, json={"new_node_id": new_node_id, "new_node_port": new_node_port})
                    if response.status_code == 200:
                        print(f"[DEBUG] Finger table en nodo {node['id']} actualizada correctamente.")
                    else:
                        print(f"[DEBUG] Error al actualizar finger table en nodo {node['id']}: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"[DEBUG] Error de conexión al intentar actualizar finger table en nodo {node['id']} ({node['port']}): {e}")


    def store_file(self, file_id):
        target_node = self.find_node(file_id)
        if target_node.id != self.id:
            url = f"http://localhost:{target_node.port}/store"
            response = requests.post(url, json={"file_id": file_id})
            if response.status_code == 200:
                print(f"[DEBUG] Archivo '{file_id}' almacenado en nodo {target_node.id} ({target_node.port}).")
            else:
                print(f"[DEBUG] Error al almacenar archivo '{file_id}' en nodo {target_node.id} ({target_node.port}).")
        else:
            self.files.append(file_id)
            print(f"[DEBUG] Archivo '{file_id}' almacenado localmente en nodo {self.id} ({self.port}).")

    def find_node(self, file_id):
        print(f"[DEBUG] Buscando nodo para almacenar archivo '{file_id}' desde nodo {self.id}")
        if self.predecessor and self.predecessor.id > self.id:
            if file_id > self.predecessor.id or file_id <= self.id:
                print(f"[DEBUG] Archivo '{file_id}' se almacena en nodo {self.id}")
                return self
        if self.successor and (self.id < file_id <= self.successor.id):
            print(f"[DEBUG] Archivo '{file_id}' se almacena en sucesor {self.successor.id}")
            return self.successor
        if self.predecessor and (self.predecessor.id < file_id <= self.id):
            print(f"[DEBUG] Archivo '{file_id}' se almacena en nodo {self.id}")
            return self
        if self.successor and self.successor.id != self.id:
            return self.successor.find_node(file_id)
        print(f"[DEBUG] Archivo '{file_id}' se almacena en nodo {self.id} (caso por defecto)")
        return self

    def show(self):
        result = []
        if self.predecessor:
            result.extend(self.predecessor.show())
        result.append(f"{self.id} ({self.port}) - Archivos: {self.files}")
        if self.successor:
            result.extend(self.successor.show())
        return result

    def join(self, node_info):
        node_id, node_port = node_info
        ip = 'localhost'
        port = node_port

        print(f"[DEBUG] Nodo {self.id} uniéndose a {node_id} ({node_port})")

        if self.id == node_id or (self.successor and self.successor.id == node_id) or (self.predecessor and self.predecessor.id == node_id):
            print(f"[DEBUG] Nodo {self.id} ya está conectado a {node_id}, evitando recursión")
            return

        if node_id > self.id:
            if self.successor is None or node_id < self.successor.id:
                previous_successor = self.successor
                self.successor = ChordNode(node_id, node_port)
                print(f"[DEBUG] Nodo {self.id} ha actualizado su sucesor a {node_id} ({node_port})")

                url = f"http://{ip}:{port}/update_predecessor"
                requests.post(url, json={"predecessor_id": self.id, "predecessor_port": self.port})

                if previous_successor:
                    url = f"http://localhost:{previous_successor.port}/update_predecessor"
                    requests.post(url, json={"predecessor_id": node_id, "predecessor_port": node_port})

            else:
                self.successor.join(node_info)

        elif node_id < self.id:
            if self.predecessor is None or node_id > self.predecessor.id:
                previous_predecessor = self.predecessor
                self.predecessor = ChordNode(node_id, node_port)
                print(f"[DEBUG] Nodo {self.id} ha actualizado su predecesor a {node_id} ({node_port})")

                url = f"http://{ip}:{port}/update_successor"
                requests.post(url, json={"successor_id": self.id, "successor_port": self.port})

                if previous_predecessor:
                    url = f"http://localhost:{previous_predecessor.port}/update_successor"
                    requests.post(url, json={"successor_id": node_id, "successor_port": node_port})

            else:
                self.predecessor.join(node_info)

        if self.successor and self.successor.id != node_id:
            url = f"http://localhost:{self.successor.port}/join"
            requests.post(url, json={"node_address": node_id, "node_port": node_port})

        if self.predecessor and self.predecessor.id != node_id:
            url = f"http://localhost:{self.predecessor.port}/join"
            requests.post(url, json={"node_address": node_id, "node_port": node_port})

        self.notify_all_nodes(node_id, node_port)
