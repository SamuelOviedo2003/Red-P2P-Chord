class ChordNode:
    def __init__(self, id):
        self.id = id
        self.successor = None
        self.predecessor = None

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

# Ejemplo de uso
node1 = ChordNode(10)
node2 = ChordNode(20)
node3 = ChordNode(30)
node4 = ChordNode(40)

node1.join(20)
node1.join(30)
node1.join(40)
node3.leave()

node1.show()