from flask import Blueprint, request, jsonify, current_app, send_file
from ..extensions import JWTTokenManager, JWTTokenManagerError, InvalidTokenError, ExpiredSignatureError, mongodb
from functools import wraps
import os
import logging

data_bp = Blueprint('data_bp', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def jwt_token_required(handler):
    """
    Decorator for checking the jwt token.
    """
    @wraps(handler)
    def decorator(*args, **kwargs):
        jwt_token = None
        if 'Authorization' in request.headers:
            # The header is usually "Bearer <token>"
            auth_header_parts = request.headers['Authorization'].split(" ")
            if len(auth_header_parts) == 2 and auth_header_parts[0] == "Bearer":
                jwt_token = request.headers['Authorization'].split(" ")[1]
        if not jwt_token:
            return jsonify({"error": "Token is missing or in wrong format"}), 401 # Unauthorized
        try:
            token_info = JWTTokenManager.decode_jwt(token=jwt_token)
        except InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401 # Unauthorized
        except ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401 # Unauthorized
        except JWTTokenManagerError:
            return jsonify({"error": "Error in token validation"}), 500 # Internal server error
        identity = token_info.get('identity')
        return handler(identity, *args, **kwargs)
    return decorator

@data_bp.route("/get_identity", methods=["GET"])
@jwt_token_required
def get_identity(identity):
    """
    Endpoint for testing jwt validation.
    """
    return f"Logged in as {identity}"

@data_bp.route("file/<file_identifier>", methods=["GET", "DELETE"])
@jwt_token_required
def file_handler(identity, file_identifier):
    """
    Endpoint for file-related operations
    """
    if request.method == "GET":
        return _handle_file_get(identity, file_identifier)
    elif request.method == "DELETE":
        return _handle_file_delete(identity, file_identifier)
    else:
        return {"error": "File handling error"}, 500
    
@data_bp.route("file", methods=["POST"])
@jwt_token_required
def file_upload_handler(identity):
    return _handle_file_post(identity)


def _handle_file_get(identity, file_identifier):
    """
    Endpoint for file downloading.
    """
    data_collections = mongodb.get_mongodb().get_collection("data")
    result = data_collections.find_one({'file_identifier': file_identifier})
    if not result:
        return jsonify({"error": "File not found"}), 404
    # Authentication to check owner
    if result['owner'] != identity:
        return jsonify({"error": "Unauthorized"}), 401
    file_storage_directory = os.path.abspath(current_app.config['FILE_STORAGE_DIRECTORY'])
    file_path = os.path.join(
        file_storage_directory,
        f"{result['filename']}"
    )
    # Return the file directly
    return send_file(
        path_or_file=file_path,
        as_attachment=True,
        download_name=result['filename']
    ), 200 # OK

def _handle_file_post(identity):
    """
    Endpoint for file uploading.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400 # Bad request
    metadata = request.form.to_dict()
    if 'file_identifier' not in metadata:
        return jsonify({"error": "No file identifier"}), 400 # Bad request
    file = request.files.get('file')
    _, file_extension = os.path.splitext(file.filename)
    new_filename = f"{metadata['file_identifier']}{file_extension}"
    # Save the metadata to the mongo.
    metadata['owner'] = identity
    metadata['filename'] = new_filename
    data_collections = mongodb.get_mongodb().get_collection("data")
    # The identifier shall be universally unique.
    result = data_collections.find_one({'file_identifier': metadata["file_identifier"]})
    if result is not None:
        return jsonify({"error": "File identifier must be globally unique"}), 400 # Bad request
    data_collections.insert_one(document=metadata)
    # Save the file
    try:
        file_storage_directory = os.path.abspath(current_app.config['FILE_STORAGE_DIRECTORY']) 
        saving_path = os.path.join(
            file_storage_directory,
            new_filename
        )
        file.save(saving_path)
    except IOError as e:
        # Rollback the db ops
        data_collections.delete_one({'file_identifier': metadata["file_identifier"]})
        logger.error(f"Error in saving the file: {e}")
        return jsonify({"error": "Error in saving the file"}), 500 # Internal server error
    return jsonify({"message": "File uploaded successfully"}), 201 # Created

def _handle_file_delete(identity, file_identifier):
    """
    Endpoint for deleting file
    """
    data_collections = mongodb.get_mongodb().get_collection("data")
    result = data_collections.find_one({'file_identifier': file_identifier})
    if not result:
        return jsonify({"error": "File not found"}), 404
    # Authentication to check owner
    if result['owner'] != identity:
        return jsonify({"error": "Unauthorized"}), 401
    file_storage_directory = os.path.abspath(current_app.config['FILE_STORAGE_DIRECTORY'])
    file_path = os.path.join(
        file_storage_directory,
        f"{result['filename']}"
    )
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    data_collections.delete_one({'file_identifier': file_identifier})
    return jsonify({"message": "File deleted"}), 200

@data_bp.route("/user_file", methods=["GET"])
@jwt_token_required
def get_all_user_files(identity):
    """
    Get all the file identifiers belonging to the user.
    """
    data_collections = mongodb.get_mongodb().get_collection("data")
    if data_collections.count_documents({'owner': identity}) == 0:
        # Return empty list
        return jsonify({"file_identifiers": []}), 200
    result_cursor = data_collections.find({'owner': identity})
    file_identifiers = [result['file_identifier'] for result in result_cursor]
    return jsonify({"file_identifiers": file_identifiers}), 200

@data_bp.route("/metadata/<file_identifier>", methods=["GET"])
@jwt_token_required
def get_file_metadata(identity, file_identifier):
    """
    Get the metadata of the file.
    """
    data_collections = mongodb.get_mongodb().get_collection("data")
    # Get the result but removing the _id field
    result = data_collections.find_one({'file_identifier': file_identifier}, 
                                       {'_id': 0})
    if not result:
        return jsonify({"error": "File not found"}), 404
    # Authentication to check owner
    if result['owner'] != identity:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(result), 200


    