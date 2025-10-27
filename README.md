# slop-farmer-server
FastAPI-based server to form the backend of the Slop Farmer browser extension.
Handles user authentication, requests to check search result URLs against reported slop,
and new reports of slop URLs from users.

## Docker Container
run the server with `docker run -P --env-file <env file> slopfarmer`

## Environment Variables
DB_URL - The url connection string to pass to SQLAlchemy
TOKEN_SECRET - the secret used for signing JWTs used for user auth after login
