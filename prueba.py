class ChordNode:
    def __init__(self, id,total_bits):
        self.id = id
        self.total_bits = total_bits
        self.successor = None
        self.predecessor = None
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
    
    def show_finger_table(self):
        print(f"Finger Table para el nodo {self.id}:")
        for i, entry in enumerate(self.finger_table):
            print(f"Entrada {i+1}: start = {entry['start']}, "
                  f"intervalo = {entry['interval']}, "
                  f"successor = {entry['successor'].id if entry['successor'] else None}")

    def join(self, node_address):
        if node_address > self.id:
            if self.successor is None:
                self.successor = ChordNode(node_address)
            else:
                self.successor.join(node_address)
        elif node_address < self.id:
            if self.predecessor is None:
                self.predecessor = ChordNode(node_address)
            else:
                self.predecessor.join(node_address)
    
    def show(self):
        # Mostrar predecesores de manera recursiva
        if self.predecessor:
            self.predecessor.show()
        # Mostrar el ID actual
        print(f"{self.id} ---> ",end="")
        # Mostrar sucesores de manera recursiva
        if self.successor:
            self.successor.show()
    def leave(self):
        if self.successor and self.predecessor:
            current_successor = self.successor
            current_predecessor = self.predecessor
            current_successor.predecessor = current_predecessor
            current_predecessor.successor = current_successor
            self.successor = None
            self.predecessor = None
    
    def verificar(self):
        return self.predecessor is not None

# Ejemplo de uso
node1 = ChordNode(10,9)

for i in reversed(range(8)):
    print(i)
print(node1.show_finger_table())