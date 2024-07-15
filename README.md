# min-object-storage
 A minimum implementation practice for a backend storage system

## Basic implementations
The implementation is a pure backend without frontend UI and purely accessed using RESTful APIs.

Files are saved to the server with a unique ID (similar to the object storage system like AWS S3). The metadata of the file is stored in a MongoDB database.
- Flask-based API with Gunicorn server
- MongoDB metadata and user database
- Authentication and access control with JWT

## Workflow plot
![Architecture](archi.png)

## Run the server
1. Install docker from [here](https://docs.docker.com/get-docker/)
2. Clone the repository and `cd` to the directory
3. Run docker-compose
```bash
docker-compose up --build
```
4. Visit the APIs with `curl` or `HTTPie`.

## Endpoints
### `/users`
Deals with user registration and login, distribution of credentials.
- `POST /users/register`: Register a new user.
- `POST /users/login`: Login with username and password. The system will return a JWT token.

### `/data`
Deals with file upload, download, and identifier retrieval.
- `POST /data/file`: Upload a file, specifying your own identifier.
- `GET /data/file/<file_identifier>`: Download a file with the identifier.
- `GET /data/get_file_list`: Get all the identifiers of the files you uploaded.
- `GET /data/metadata/<file_identifier>`: Get the metadata of the file with the identifier.
