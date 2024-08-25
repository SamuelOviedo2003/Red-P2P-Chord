from flask import Flask, jsonify, request
from .chord import ChordNode

app = Flask(__name__)
chord_node = None

def create_chord_node(id, port):
    global chord_node
    chord_node = ChordNode(id, port)
    return chord_node

@app.route('/join', methods=['POST'])
def join_network():
    node_address = request.json.get('node_address')
    node_port = request.json.get('node_port')
    if node_address and node_port:
        success = chord_node.join((node_address, node_port))
        return jsonify({"success": success}), 200
    else:
        return jsonify({"error": "Node address and port are required"}), 400

@app.route('/leave', methods=['POST'])
def leave_network():
    chord_node.leave()
    return jsonify({"success": True}), 200

@app.route('/show', methods=['GET'])
def show_network():
    network_structure = chord_node.show()
    return jsonify({"success": True, "network": " ---> ".join(network_structure)}), 200

@app.route('/show_finger_table', methods=['GET'])
def show_finger_table():
    finger_table = chord_node.show_finger_table()
    return f"<pre>{finger_table}</pre>", 200

@app.route('/store', methods=['POST'])
def store_file():
    file_id = request.json.get('file_id')  # Asumiendo que ahora pasas un número directamente
    if file_id is not None:
        chord_node.store_file(file_id)
        return jsonify({"success": True, "message": f"Archivo '{file_id}' almacenado."}), 200
    else:
        return jsonify({"error": "File ID is required"}), 400


@app.route('/lookup', methods=['GET'])
def lookup():
    key = request.args.get('key')
    if key:
        node = chord_node.lookup(key)
        return jsonify({"node": node}), 200
    else:
        return jsonify({"error": "Key is required"}), 400

@app.route('/update_predecessor', methods=['POST'])
def update_predecessor():
    predecessor_id = request.json.get('predecessor_id')
    predecessor_port = request.json.get('predecessor_port')
    if predecessor_id and predecessor_port:
        chord_node.predecessor = ChordNode(predecessor_id, predecessor_port)
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Predecessor ID and port are required"}), 400

@app.route('/update_successor', methods=['POST'])
def update_successor():
    successor_id = request.json.get('successor_id')
    successor_port = request.json.get('successor_port')
    if successor_id and successor_port:
        chord_node.successor = ChordNode(successor_id, successor_port)
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Successor ID and port are required"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0')


