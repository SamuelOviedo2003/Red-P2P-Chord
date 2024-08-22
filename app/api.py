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


@app.route('/lookup', methods=['GET'])
def lookup():
    key = request.args.get('key')
    if key:
        node = chord_node.lookup(key)
        return jsonify({"node": node}), 200
    else:
        return jsonify({"error": "Key is required"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0')


