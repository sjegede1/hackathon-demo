from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Configure the SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for Todo items
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(128), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# Create the database
with app.app_context():
    db.create_all()

# Route to get all todos
@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([{'id': todo.id, 'task': todo.task, 'completed': todo.completed} for todo in todos])

# Route to get a single todo by id
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        return jsonify({'id': todo.id, 'task': todo.task, 'completed': todo.completed})
    else:
        return jsonify({"error": "Todo not found"}), 404

# Route to create a new todo
@app.route('/todos', methods=['POST'])
def create_todo():
    if not request.json or 'task' not in request.json:
        return jsonify({"error": "Bad request"}), 400
    todo = Todo(task=request.json['task'], completed=False)
    db.session.add(todo)
    db.session.commit()
    return jsonify({'id': todo.id, 'task': todo.task, 'completed': todo.completed}), 201

# Route to update a todo
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    if not request.json:
        return jsonify({"error": "Bad request"}), 400
    todo.task = request.json.get('task', todo.task)
    todo.completed = request.json.get('completed', todo.completed)
    db.session.commit()
    return jsonify({'id': todo.id, 'task': todo.task, 'completed': todo.completed})

# Route to delete a todo
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"result": "Successfully deleted"})

if __name__ == '__main__':
    app.run(debug=True)
