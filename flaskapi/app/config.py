import os

class DefaultConfig:
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    FILE_STORAGE_DIRECTORY = os.getenv("FILE_STORAGE_DIRECTORY")