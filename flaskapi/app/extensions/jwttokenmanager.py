import jwt
import os
import datetime

class JWTTokenManager:
    """
    Class for managing JWT tokens.
    """
    @staticmethod
    def encode_jwt(identity, exp_seconds=3600):
        """
        Encode the JWT token.
        
        :param identity: The identity to encode.
        :param exp_seconds: The expiration time in seconds.
        :return: The encoded JWT token.
        
        :raises EnvironmentError: If the FLASK_SECRET_KEY environment variable is not set.
        """
        secret_key = os.getenv('FLASK_SECRET_KEY')
        if not secret_key:
            raise EnvironmentError("FLASK_SECRET_KEY environment variable is not set.")
        payload = {
            'identity': identity,
            'exp': datetime.datetime.now() + datetime.timedelta(seconds=exp_seconds)
        }
        token = jwt.encode(
            payload, key=secret_key, algorithm="HS256"
        )
        return token
    
    @staticmethod
    def decode_jwt(token) -> dict:
        """
        Decode the JWT token.

        :param token: The token to decode.
        :return: The decoded payload.

        :raises ExpiredSignatureError: If the token has expired.
        :raises InvalidTokenError: If the token is invalid.
        :raises EnvironmentError: If the FLASK_SECRET_KEY environment variable is not set.
        """
        secret_key = os.getenv('FLASK_SECRET_KEY')
        if not secret_key:
            raise EnvironmentError("FLASK_SECRET_KEY environment variable is not set.")
        try:
            payload = jwt.decode(token, key=secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredSignatureError
        except jwt.InvalidTokenError:
            raise InvalidTokenError
            

class JWTTokenManagerError(Exception):
    pass

class ExpiredSignatureError(JWTTokenManagerError):
    pass

class InvalidTokenError(JWTTokenManagerError):
    pass