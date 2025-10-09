from threading import Thread
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from utils import read_json, write_json
from tamagotchi import Tamagotchi
from draw import render_tamagotchi
import argparse
import io

TODO_JSON_PATH = "data/todos.json"
todos = [];

try:
    todos = read_json(TODO_JSON_PATH)
except Exception as e:
    print(f"Could not read {TODO_JSON_PATH}: {e}")

print(todos)

# Find max id persisted
next_id = 0
if (len(todos) > 0):
    next_id = max(todos, key=lambda item: item['id'])['id']
print(f"Max id: {next_id}")

def get_id():
    global next_id
    next_id += 1
    return next_id

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080"])

@app.route('/api/complete_todo', methods=['POST'])
def handle_complete_todo():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON."}), 400

    req_data = request.get_json()
    id = req_data.get('id')

    idx = next((i for i, x in enumerate(todos) if x['id'] == id), None)

    if idx == None:
        return jsonify({"message": "No todo found. :-("}), 400

    print(f"Completing todo: {todos[idx]}")

    if todos[idx]["completed"]:
        return jsonify({"message": "Already completed"}), 400
 
    todos[idx]["completed"] = True
    todos[idx]["date_completed"] = datetime.now()

    write_json(todos, TODO_JSON_PATH);
    thread = Thread(target=tamagotchi.update, args=(todos[idx]["message"],))
    thread.start()

    return jsonify({"message": "Success!"}), 201


@app.route('/api/delete_todo', methods=['POST'])
def handle_delete_todo():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON."}), 400

    req_data = request.get_json()
    id = req_data.get('id')

    global todos
    todos = [item for item in todos if item['id'] != id]

    write_json(todos, TODO_JSON_PATH);

    return jsonify({"message": "Success!"}), 201


@app.route('/api/submit_todo', methods=['POST'])
def handle_submit_todo():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON."}), 400

    req_data = request.get_json()
    message = req_data.get('message')
    tag = req_data.get('tag')
    completed = bool(req_data.get('completed'))
    id = get_id()
    date_added = datetime.now()

    data = {
        "id": id,
        "message": message,
        "tag": tag,
        "date_added": date_added,
        "date_completed": date_added if completed else None,
        "completed": completed
    }

    print(f"Adding new todo: {data}")
    todos.append(data)

    write_json(todos, TODO_JSON_PATH);

    return jsonify({"message": "Success!"}), 201


@app.route('/api/get_todos')
def handle_get_todos():
    return jsonify(todos), 200

@app.route('/api/tamagotchi_image')
def handle_tamagotchi_image():
    tamagotchi.update()
    sprite = tamagotchi.get_sprite()
    quote = tamagotchi.generate_quote()
    img = render_tamagotchi(tamagotchi, sprite, quote)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--draw", action="store_true")
    args = parser.parse_args()

    tamagotchi = Tamagotchi()

    if args.draw:
        from render_loop import launch_render_loop
        launch_render_loop(tamagotchi)

    app.run(debug=True)
