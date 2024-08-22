import requests

class ChordNode:
    def __init__(self, id, port):
        self.id = id
        self.port = port
        self.successor = None
        self.predecessor = None
        self.finger_table =[]
    
    def show(self):
        # Mostrar predecesores de manera recursiva
        if self.predecessor:
            self.predecessor.show()
        # Mostrar el ID actual
        print(f"{self.id} ({self.port}) ---> ", end="")
        # Mostrar sucesores de manera recursiva
        if self.successor:
            self.successor.show()
        print("")

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
        self.show()

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



