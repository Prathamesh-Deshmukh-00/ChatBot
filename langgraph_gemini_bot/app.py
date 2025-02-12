from flask import Flask, jsonify, request
from chatbot.run import run_chatbot

app = Flask(__name__)

# Sample Data (Mock Database)
response = run_chatbot()
users = [
    {"id": 1, "name": response},
    {"id": 2, "name": "Bob"}
]

# Route: Home
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Flask API"})

# Route: Get All Users
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

# Route: Get User by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((user for user in users if user["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

# Route: Add a New User
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    response_data  =  run_chatbot(data["name"])
    # new_user = {"id": len(users) + 1, "name": data["name"]}
    # users.append(new_user)
    return jsonify(), 201

# Route: Delete a User
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [user for user in users if user["id"] != user_id]
    return jsonify({"message": "User deleted"})

# Run the API
if __name__ == '__main__':
    app.run(debug=True)
