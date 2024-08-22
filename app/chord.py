import hashlib
import requests

class ChordNode:
    def __init__(self, id, port):
        self.id = self.hash_id(id)
        self.port = port
        self.successor = None
        self.predecessor = None
        self.finger_table = []
        self.files=[]
    
    def hash_id(self, id):
        sha1 = hashlib.sha1(str(id).encode('utf-8'))
        return int(sha1.hexdigest(), 16)  

    def show(self):
        result = []
        if self.predecessor:
            result.extend(self.predecessor.show())
        result.append(f"{self.id} ({self.port})")
        if self.successor:
            result.extend(self.successor.show())
        return result

    def join(self, node_info):
        node_address, node_port = node_info
        hashed_address = self.hash_id(node_address)
        
        if hashed_address > self.id:
            if self.successor is None:
                self.successor = ChordNode(node_address, node_port)
            else:
                self.successor.join(node_info)
        elif hashed_address < self.id:
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
        hashed_key = self.hash_id(key)
        if self.successor:
            return self.successor.id
        return self.id
