from flask import Blueprint, request, jsonify, current_app, send_file
from ..extensions import JWTTokenManager, JWTTokenManagerError, InvalidTokenError, ExpiredSignatureError, mongodb
from typing import Callable
from functools import wraps
import os

data_bp = Blueprint('data_bp', __name__)

# Decorator for token protection
def jwt_token_required(handler):
    @wraps(handler)
    def decorator(*args, **kwargs):
        jwt_token = None
        if 'Authorization' in request.headers:
            # The header is usually "Bearer <token>"
            auth_header_parts = request.headers['Authorization'].split(" ")
            if len(auth_header_parts) == 2 and auth_header_parts[0] == "Bearer":
                jwt_token = request.headers['Authorization'].split(" ")[1]
        if not jwt_token:
            return "Wrong JWT token format or no token", 401
        try:
            token_info = JWTTokenManager.decode_jwt(token=jwt_token)
        except InvalidTokenError:
            return "Token invalid", 401
        except ExpiredSignatureError:
            return "Signature expired", 401
        except JWTTokenManagerError:
            return "Error in parsing the token", 401
        identity = token_info.get('identity')
        return handler(identity, *args, **kwargs)
    return decorator

@data_bp.route("/test_jwt", methods=["POST"])
@jwt_token_required
def test_jwt(identity):
    """
    Endpoint for testing jwt validation.
    """
    return f"Logged in as {identity}"

@data_bp.route("/upload_file", methods=["POST"])
@jwt_token_required
def upload_file(identity):
    """
    Endpoint for file uploading.
    """
    if 'file' not in request.files:
        return "File not uploaded", 400 # Bad request
    metadata = request.form.to_dict()
    if 'file_identifier' not in metadata:
        return "File identifier not specified", 400 # Bad request
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
        return "File identifier must be globally unique", 400 # Bad request
    data_collections.insert_one(document=metadata)
    # Save the file
    try:
        file_storage_directory = os.path.abspath(current_app.config['FILE_STORAGE_DIRECTORY']) 
        saving_path = os.path.join(
            file_storage_directory,
            new_filename
        )
        file.save(saving_path)
    except:
        # Rollback the db ops
        data_collections.delete_one({'file_identifier': metadata["file_identifier"]})
        # Raise exception with the original error message
        raise
    return "File uploaded successfully", 201 # Created

@data_bp.route("/download_file/<file_identifier>", methods=["GET"])
@jwt_token_required
def download_file(identity, file_identifier):
    """
    Endpoint for file downloading.
    """
    print(file_identifier)
    data_collections = mongodb.get_mongodb().get_collection("data")
    result = data_collections.find_one({'file_identifier': file_identifier})
    if not result:
        return "File not found", 404
    # Authentication to check owner
    if result['owner'] != identity:
        return "Unauthorized", 401
    print(result)
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
    )



    