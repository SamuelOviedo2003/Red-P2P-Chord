import sys
from app.api import create_chord_node, app

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    node_id = int(sys.argv[2]) if len(sys.argv) > 2 else port

    chord_node = create_chord_node(node_id, port)

    app.run(host='0.0.0.0', port=port)



