from flask import Blueprint, request, jsonify, current_app
from ..extensions import JWTTokenManager, hash_password, check_password, mongodb

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'GET':
        return _handle_login_get()
    elif request.method == 'POST':
        return _handle_login_post()
        
def _handle_login_get():
    return "Not Implemented", 501

def _handle_login_post():
    username = request.json['username']
    password = request.json['password']
    if _validate(username=username, password=password):
        # Distribute the token
        token = JWTTokenManager.encode_jwt(
            identity=username, exp_seconds=3600
        )
        return jsonify({"jwt_token": token})
    else:
        return "Authentication failed", 401

def _validate(username: str, password: str) -> bool:
    users_collections = mongodb.get_mongodb().get_collection("users")
    document = users_collections.find_one(
        filter={'username': username}
    )
    if not document:
        return False
    hashed_password, salt = document['hashed_password'], document['salt']
    return check_password(
        provided_pwd=password,
        pwd_hash=hashed_password,
        salt=salt
    )

@users_bp.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    # Check if user exists in database
    users_collections = mongodb.get_mongodb().get_collection("users")
    document = users_collections.find_one(
        filter={'username': username}
    )
    if not document:
        # Insert a new one.
        hashed_password, salt = hash_password(password)
        users_collections.insert_one(
            {
                'username': username,
                'hashed_password': hashed_password,
                'salt': salt
            }
        )
        return "User created", 201 # Created
    else:
        return "Username already in use", 409 #Conflict
    